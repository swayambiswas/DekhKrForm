import os
import json
import asyncio
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)

class LLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[LLMService] Failed to initialize google-genai client: {e}")

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.2
    ) -> T:
        """
        Calls Gemini API with structured output schema enforcement.
        If no API key is provided, gracefully delegates to heuristic agent simulator.
        """
        if self.client:
            try:
                # Use Gemini client
                full_prompt = f"{system_prompt}\n\nUSER REQUEST:\n{user_prompt}"
                
                # Gemini structured output via json schema
                schema = response_model.model_json_schema()
                
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=settings.DEFAULT_MODEL,
                    contents=full_prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": response_model,
                        "temperature": temperature,
                    }
                )
                
                if response.text:
                    parsed_json = json.loads(response.text)
                    return response_model.model_validate(parsed_json)
            except Exception as e:
                print(f"[LLMService] Gemini API call failed or timed out ({e}). Falling back to simulation engine.")
        
        # If no client or API error, return None to trigger domain fallback in agent
        return None

llm_service = LLMService()

