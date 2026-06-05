import logging
from typing import List, Optional

import aiohttp

from backend.app.config import settings

logger = logging.getLogger(__name__)


class MapsService:
    """Google Maps Places autocomplete and geocoding."""

    @staticmethod
    def is_configured() -> bool:
        return bool(settings.google_maps_key)

    @staticmethod
    async def _classic_autocomplete(query: str) -> tuple[List[dict], str]:
        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            "input": query,
            "key": settings.google_maps_key,
            "components": "country:pk",
            "language": "en",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                status = data.get("status", "UNKNOWN")
                if status not in ("OK", "ZERO_RESULTS"):
                    error_msg = data.get("error_message", status)
                    logger.warning(f"Places autocomplete: {status} - {error_msg}")
                    return [], error_msg

                suggestions = [
                    {"description": p.get("description"), "place_id": p.get("place_id")}
                    for p in data.get("predictions", [])
                ]
                return suggestions, status

    @staticmethod
    async def _new_places_autocomplete(query: str) -> tuple[List[dict], str]:
        url = "https://places.googleapis.com/v1/places:autocomplete"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.google_maps_key,
            "X-Goog-FieldMask": "suggestions.placePrediction.placeId,suggestions.placePrediction.text",
        }
        body = {
            "input": query,
            "includedRegionCodes": ["pk"],
            "languageCode": "en",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as response:
                if response.status != 200:
                    text = await response.text()
                    logger.warning(f"New Places API error {response.status}: {text[:200]}")
                    return [], f"HTTP {response.status}"

                data = await response.json()
                suggestions = []
                for item in data.get("suggestions", []):
                    pred = item.get("placePrediction", {})
                    text = pred.get("text", {}).get("text", "")
                    place_id = pred.get("placeId", "")
                    if text and place_id:
                        suggestions.append({"description": text, "place_id": place_id})
                return suggestions, "OK"

    @staticmethod
    async def autocomplete(query: str) -> dict:
        if not MapsService.is_configured():
            return {"suggestions": [], "error": "GOOGLE_MAP_API_KEY not set in .env"}

        try:
            suggestions, status = await MapsService._new_places_autocomplete(query)
            if not suggestions:
                suggestions, status = await MapsService._classic_autocomplete(query)
            return {"suggestions": suggestions, "error": None if suggestions else status}
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            return {"suggestions": [], "error": str(e)}

    @staticmethod
    async def geocode_place(place_id: Optional[str] = None, address: Optional[str] = None) -> dict:
        if not MapsService.is_configured():
            return {"latitude": None, "longitude": None, "formatted_address": address or "", "error": "API key not configured"}

        try:
            async with aiohttp.ClientSession() as session:
                if place_id:
                    url = "https://maps.googleapis.com/maps/api/place/details/json"
                    params = {
                        "place_id": place_id,
                        "fields": "geometry,formatted_address",
                        "key": settings.google_maps_key,
                    }
                    async with session.get(url, params=params) as response:
                        data = await response.json()
                        if data.get("status") != "OK":
                            err = data.get("error_message", data.get("status"))
                            logger.warning(f"Place details error: {err}")
                            return await MapsService._geocode_address(session, address, err)

                        result = data.get("result", {})
                        location = result.get("geometry", {}).get("location", {})
                        return {
                            "latitude": location.get("lat"),
                            "longitude": location.get("lng"),
                            "formatted_address": result.get("formatted_address", address or ""),
                            "error": None,
                        }

                return await MapsService._geocode_address(session, address)
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return {"latitude": None, "longitude": None, "formatted_address": address or "", "error": str(e)}

    @staticmethod
    async def _geocode_address(session, address: Optional[str], prior_error: str = None) -> dict:
        if not address:
            return {"latitude": None, "longitude": None, "formatted_address": "", "error": prior_error or "No address"}

        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": settings.google_maps_key, "components": "country:PK"}
        async with session.get(url, params=params) as response:
            data = await response.json()
            if data.get("status") != "OK" or not data.get("results"):
                err = data.get("error_message", data.get("status", prior_error))
                return {"latitude": None, "longitude": None, "formatted_address": address, "error": err}

            result = data["results"][0]
            location = result.get("geometry", {}).get("location", {})
            return {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
                "formatted_address": result.get("formatted_address", address),
                "error": None,
            }
