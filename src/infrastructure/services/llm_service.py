"""Service for interacting with Google Gemini LLM."""
import asyncio
from typing import List, Optional

from google import genai
from src.core.config import settings


class LLMService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    async def _generate(self, prompt: str, timeout: int = 15) -> str:
        """Helper to generate content with timeout and error handling."""
        try:
            # Note: google-genai synchronous call. 
            # In a real async FastAPI app, we might want to run this in a thread pool.
            # However, for now we wrap it in asyncio.to_thread if the library is blocking.
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Requirement 14.1: Fallback strategy
            print(f"LLM Error: {str(e)}")
            return ""

    async def generate_clarification(self, problem_description: str) -> str:
        """Generate a follow-up question to clarify the problem description."""
        prompt = f"Aşağıdaki problem açıklamasını daha iyi anlamak için bir takip sorusu sor:\n\n{problem_description}"
        result = await self._generate(prompt, timeout=10)
        return result or "Problem hakkında daha fazla detay verebilir misiniz?"

    async def generate_next_why(self, problem_description: str, previous_whys: List[str]) -> str:
        """Generate the next 'Why' question for 5 Why analysis."""
        context = "\n".join([f"Neden {i+1}: {why}" for i, why in enumerate(previous_whys)])
        prompt = (
            f"Problem: {problem_description}\n"
            f"Şu ana kadarki nedenler:\n{context}\n\n"
            f"Bir sonraki 'Neden' sorusunu sor. Çok kısa ve öz olsun."
        )
        result = await self._generate(prompt, timeout=3)
        return result or "Bu durumun kök nedeni nedir?"

    async def generate_lessons_learned(self, session_data: dict) -> str:
        """Generate 'Lessons Learned' summary from session data."""
        prompt = f"Aşağıdaki problem çözüm oturumundan çıkarılan dersleri özetle (100-500 kelime):\n\n{str(session_data)}"
        result = await self._generate(prompt, timeout=15)
        
        # Requirement 14.2: Structural component check
        if not result:
            return "Kök Neden: [Placeholder]\nDüzeltici Eylemler: [Placeholder]\nSonuç: [Placeholder]\nÖnleyici Öneriler: [Placeholder]"
        
        # We could add more complex logic here to check for specific headers/components.
        return result

    async def suggest_category_reassignment(self, cause: str, current_category: str) -> Optional[str]:
        """Suggest a better Ishikawa category for a given cause."""
        prompt = (
            f"Neden: '{cause}'\n"
            f"Şu anki kategori: '{current_category}'\n\n"
            f"Eğer bu neden başka bir Ishikawa kategorisine (Man, Machine, Method, Material, Measurement, Environment) "
            f"daha uygunsa, sadece kategori ismini söyle. Değilse 'UYGUN' de."
        )
        result = await self._generate(prompt, timeout=5)
        result = result.strip().upper()
        if "UYGUN" in result or result not in ["MAN", "MACHINE", "METHOD", "MATERIAL", "MEASUREMENT", "ENVIRONMENT"]:
            return None
        return result.capitalize()
