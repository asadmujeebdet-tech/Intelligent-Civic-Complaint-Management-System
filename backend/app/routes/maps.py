from fastapi import APIRouter, HTTPException, Query

from backend.app.services.maps_service import MapsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/maps", tags=["maps"])


@router.get("/status")
async def maps_status():
    """Check if Google Maps API is configured."""
    return {
        "configured": MapsService.is_configured(),
        "message": "Ready" if MapsService.is_configured() else "Set GOOGLE_MAP_API_KEY in .env",
    }


@router.get("/autocomplete")
async def places_autocomplete(q: str = Query(..., min_length=2)):
    """Google Places autocomplete proxy."""
    if not MapsService.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Google Maps API key not configured. Add GOOGLE_MAP_API_KEY to your .env file.",
        )
    result = await MapsService.autocomplete(q)
    return {
        "status": "success",
        "data": result["suggestions"],
        "error": result.get("error"),
    }


@router.get("/geocode")
async def geocode_location(
    place_id: str = Query(None),
    address: str = Query(None),
):
    """Geocode a place to latitude/longitude."""
    if not MapsService.is_configured():
        raise HTTPException(status_code=503, detail="Google Maps API not configured")
    if not place_id and not address:
        raise HTTPException(status_code=400, detail="place_id or address required")
    result = await MapsService.geocode_place(place_id=place_id, address=address)
    return {"status": "success", "data": result}
