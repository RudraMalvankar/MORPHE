import asyncio
import json
import re
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging import logger


class GeminiClient:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self._initialized = True
            logger.info(
                f"Gemini client initialized with model: {settings.GEMINI_MODEL}"
            )
        else:
            self._initialized = False
            logger.warning(
                "Gemini API key not configured. AI features will be unavailable."
            )

    @property
    def is_available(self) -> bool:
        return self._initialized

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        if not self._initialized:
            raise RuntimeError(
                "Gemini API key not configured. Set GEMINI_API_KEY in .env"
            )

        config = types.GenerateContentConfig(
            temperature=temperature or settings.GEMINI_TEMPERATURE,
            max_output_tokens=max_tokens or settings.GEMINI_MAX_OUTPUT_TOKENS,
        )

        if system_instruction:
            config.system_instruction = system_instruction

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise RuntimeError(f"Gemini generation failed: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        structured_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, "
            "no extra text.\nThe JSON must be parseable by Python's json.loads()."
        )

        response = await self.generate(
            structured_prompt,
            system_instruction=system_instruction,
            temperature=temperature or 0.3,
        )

        response = response.strip()
        if response.startswith("```"):
            response = re.sub(r"^```(?:json)?\n?", "", response)
            response = re.sub(r"\n?```$", "", response)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(
                f"Failed to parse Gemini response as JSON: {response[:200]}"
            )

    async def generate_sections(
        self,
        prompt: str,
        section_markers: List[str],
        system_instruction: Optional[str] = None,
    ) -> Dict[str, str]:
        marker_list = "\n".join(
            f"- {{{{SECTION:{marker}}}}}" for marker in section_markers
        )
        full_prompt = (
            f"{prompt}\n\n"
            "Return the output with sections marked exactly as shown:\n"
            f"{marker_list}\n\n"
            "Each section starts with its marker on its own line, "
            "followed by the content."
        )

        response = await self.generate(
            full_prompt, system_instruction=system_instruction
        )

        sections: Dict[str, str] = {}
        current_section: Optional[str] = None
        current_content: List[str] = []

        for line in response.split("\n"):
            stripped = line.strip()
            found_marker = False
            for marker in section_markers:
                if stripped == f"{{{{SECTION:{marker}}}}}":
                    if current_section:
                        sections[current_section] = (
                            "\n".join(current_content).strip()
                        )
                    current_section = marker
                    current_content = []
                    found_marker = True
                    break
            if not found_marker and current_section is not None:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections


gemini_client = GeminiClient()
