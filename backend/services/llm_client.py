import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")

    async def chat(self, messages: list[dict]) -> str:
        formatted_history = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "assistant":
                role = "model"
            elif role == "system":
                role = "user" 
            
            formatted_history.append({
                "role": role,
                "parts": [content]
            })

        generation_config = genai.types.GenerationConfig(
            temperature=0 # Defini como 0 pro modelo não inventar nada, da pra rever depois
        )

        response = await self.model.generate_content_async(
            formatted_history,
            generation_config=generation_config
        )

        return response.text.strip()