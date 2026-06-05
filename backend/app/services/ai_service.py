import google.generativeai as genai
import os
from backend.app.config import settings
from backend.app.models.complaint import (
    CategoryEnum, SeverityEnum, LanguageEnum, AIClassificationResponse
)
from sentence_transformers import SentenceTransformer
from langdetect import detect, LangDetectException
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    """AI Service for complaint classification and analysis"""
    
    _instance = None
    _embedder = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize AI service"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use environment override if provided, otherwise prefer gemini-2.5-flash
            model_name = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
            self.model = genai.GenerativeModel(model_name)
            logger.info("✅ Gemini API initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini API: {e}")
            self.model = None
        
        # Load embedding model
        try:
            if self._embedder is None:
                self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Embedding model loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
    
    def detect_language(self, text: str) -> str:
        """Detect language of complaint"""
        try:
            lang_code = detect(text)
            
            # Map language codes to our languages
            lang_map = {
                'ur': LanguageEnum.URDU.value,
                'en': LanguageEnum.ENGLISH.value,
                'hi': LanguageEnum.ROMAN_URDU.value,  # Approximation for Roman Urdu
            }
            
            return lang_map.get(lang_code, LanguageEnum.ENGLISH.value)
        except LangDetectException:
            return LanguageEnum.ENGLISH.value
    
    def classify_complaint(self, complaint_text: str, location: str) -> AIClassificationResponse:
        """Classify complaint using Gemini API"""
        try:
            # Prepare the prompt
            prompt = f"""
            Analyze this civic complaint and provide classification:
            
            Complaint Text: {complaint_text}
            Location: {location}
            
            Classify and respond in JSON format:
            {{
                "category": One of [Roads, Water, Electricity, Sanitation, Traffic, Public Safety, Environment],
                "severity": One of [Low, Medium, High, Critical],
                "priority": 1-100 (100 = highest priority based on severity + urgency + social impact),
                "department": Responsible department,
                "recommendation": Specific action to take (max 100 words),
                "confidence": 0.0-1.0
            }}
            
            Be specific and actionable in recommendations.
            """
            
            # Get response from Gemini
            if self.model:
                response = self.model.generate_content(prompt)
                response_text = response.text
                
                # Try to extract JSON from response
                try:
                    # Find JSON in response
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        classification_data = json.loads(json_str)
                    else:
                        classification_data = self._parse_response(response_text)
                except json.JSONDecodeError:
                    classification_data = self._parse_response(response_text)
            else:
                # Fallback classification
                classification_data = self._fallback_classification(complaint_text, location)
            
            # Ensure all required fields
            classification_data.setdefault('category', 'Environment')
            classification_data.setdefault('severity', 'Medium')
            classification_data.setdefault('priority', 50)
            classification_data.setdefault('department', 'General Services')
            classification_data.setdefault('recommendation', 'This complaint requires further investigation.')
            classification_data.setdefault('confidence', 0.75)
            # Ensure language is set (model may omit it)
            classification_data.setdefault('language', self.detect_language(complaint_text))
            
            return AIClassificationResponse(**classification_data)
            
        except Exception as e:
            logger.error(f"❌ Classification error: {e}")
            # Ensure we always return an AIClassificationResponse instance
            fallback = self._fallback_classification(complaint_text, location)
            try:
                return AIClassificationResponse(**fallback)
            except Exception:
                # As last resort, return a minimal safe response
                return AIClassificationResponse(
                    category="Environment",
                    severity="Medium",
                    priority=50,
                    language=LanguageEnum.ENGLISH.value,
                    department="General Services",
                    recommendation="This complaint requires further investigation.",
                    confidence=0.5,
                )
    
    def _parse_response(self, response_text: str) -> dict:
        """Parse Gemini response manually"""
        return {
            'category': self._extract_category(response_text),
            'severity': self._extract_severity(response_text),
            'priority': self._extract_priority(response_text),
            'department': self._extract_department(response_text),
            'recommendation': self._extract_recommendation(response_text),
            'confidence': 0.7
        }
    
    def _extract_category(self, text: str) -> str:
        """Extract category from response"""
        categories = [cat.value for cat in CategoryEnum]
        for cat in categories:
            if cat.lower() in text.lower():
                return cat
        return "Environment"
    
    def _extract_severity(self, text: str) -> str:
        """Extract severity from response"""
        severities = [sev.value for sev in SeverityEnum]
        for sev in severities:
            if sev.lower() in text.lower():
                return sev
        return "Medium"
    
    def _extract_priority(self, text: str) -> int:
        """Extract priority score from response"""
        try:
            import re
            priority_match = re.search(r'"priority":\s*(\d+)', text)
            if priority_match:
                return int(priority_match.group(1))
        except:
            pass
        return 50
    
    def _extract_department(self, text: str) -> str:
        """Extract department from response"""
        try:
            import re
            dept_match = re.search(r'"department":\s*"([^"]+)"', text)
            if dept_match:
                return dept_match.group(1)
        except:
            pass
        return "General Services"
    
    def _extract_recommendation(self, text: str) -> str:
        """Extract recommendation from response"""
        try:
            import re
            rec_match = re.search(r'"recommendation":\s*"([^"]+)"', text)
            if rec_match:
                return rec_match.group(1)
        except:
            pass
        return "This complaint requires further investigation."
    
    def _fallback_classification(self, complaint_text: str, location: str) -> dict:
        """Fallback classification when API fails"""
        # Simple keyword-based classification
        text_lower = complaint_text.lower()
        
        if any(word in text_lower for word in ['pothole', 'road', 'street', 'pavement']):
            return {
                'category': 'Roads',
                'severity': 'High',
                'priority': 75,
                'department': 'Public Works',
                'recommendation': 'Schedule road inspection and repair.',
                'confidence': 0.6
            }
        elif any(word in text_lower for word in ['water', 'pipeline', 'tap', 'leak']):
            return {
                'category': 'Water',
                'severity': 'High',
                'priority': 80,
                'department': 'Water Authority',
                'recommendation': 'Urgent water supply inspection required.',
                'confidence': 0.6
            }
        elif any(word in text_lower for word in ['electricity', 'light', 'power', 'wire']):
            return {
                'category': 'Electricity',
                'severity': 'Critical',
                'priority': 90,
                'department': 'Electric Utility',
                'recommendation': 'Urgent electrical safety inspection.',
                'confidence': 0.6
            }
        elif any(word in text_lower for word in ['garbage', 'trash', 'dirt', 'sanitation']):
            return {
                'category': 'Sanitation',
                'severity': 'Medium',
                'priority': 60,
                'department': 'Sanitation Services',
                'recommendation': 'Schedule cleanup and sanitization.',
                'confidence': 0.6
            }
        elif any(word in text_lower for word in ['traffic', 'accident', 'road', 'vehicle']):
            return {
                'category': 'Traffic',
                'severity': 'High',
                'priority': 70,
                'department': 'Traffic Authority',
                'recommendation': 'Deploy traffic management resources.',
                'confidence': 0.6
            }
        else:
            return {
                'category': 'Environment',
                'severity': 'Medium',
                'priority': 50,
                'department': 'General Services',
                'recommendation': 'Route to appropriate department for investigation.',
                'confidence': 0.5
            }
    
    def get_embeddings(self, text: str) -> list:
        """Get sentence embeddings for duplicate detection"""
        try:
            if self._embedder:
                embeddings = self._embedder.encode(text, convert_to_tensor=False)
                return embeddings.tolist()
            return []
        except Exception as e:
            logger.error(f"❌ Embedding error: {e}")
            return []
    
    def calculate_similarity(self, embedding1: list, embedding2: list) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            similarity = cosine_similarity(
                [embedding1], 
                [embedding2]
            )[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Similarity calculation error: {e}")
            return 0.0

# Singleton instance
ai_service = AIService()
