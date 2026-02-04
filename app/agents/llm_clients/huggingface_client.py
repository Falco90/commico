import httpx
from typing import Optional
from app.core.settings import settings


HF_API_BASE = "https://api-inference.huggingface.co/models"


class HuggingFaceClient:
    """
    Minimal async Hugging Face Inference API client.

    Designed for:
    - text generation
    - agent-style usage
    - drop-in replacement for OpenAI clients
    """

    def __init__(
        self,
        *,
        model: str,
        api_key: Optional[str] = None,
        timeout_seconds: int = 60,
    ):
        self.model = model or "google/flan-t5-large"
        self.api_key = api_key or settings.HF_API_KEY
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            raise RuntimeError(
                "HF_API_KEY is not configured. "
                "Set it in your .env file or pass api_key explicitly."
            )

    async def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt.

        Returns plain text (no metadata).
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 300,
                "temperature": 0.4,
                "top_p": 0.9,
                "return_full_text": False,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{HF_API_BASE}/{self.model}",
                headers=headers,
                json=payload,
            )

        # Handle common HF API edge cases
        if response.status_code == 503:
            raise RuntimeError(
                "Hugging Face model is loading (cold start). "
                "Retry in a few seconds."
            )

        response.raise_for_status()

        data = response.json()

        # Expected HF response:
        # [{"generated_text": "..."}]
        if not isinstance(data, list) or "generated_text" not in data[0]:
            raise RuntimeError(f"Unexpected Hugging Face response: {data}")

        return data[0]["generated_text"].strip()

