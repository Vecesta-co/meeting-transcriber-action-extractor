import json
import requests
from typing import List
from .base import BaseLLMProvider
from ..core.types import ActionItem

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", endpoint: str = "https://api.openai.com/v1"):
        if not api_key:
            raise ValueError("OpenAIProvider requires OPENAI_API_KEY.")
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint.rstrip("/")

    @property
    def name(self) -> str:
        return "openai"

    def extract_action_items(self, transcript_text: str) -> List[ActionItem]:
        url = f"{self.endpoint}/chat/completions"
        prompt = (
            "Extract meeting action items from the transcript. Output valid JSON object with an 'action_items' array. "
            "Each item must have keys: 'task', 'owner', 'deadline', 'priority', 'context_quote', 'timestamp'.\n\n"
            f"TRANSCRIPT:\n{transcript_text}"
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        items_raw = parsed.get("action_items", parsed.get("items", []))

        results: List[ActionItem] = []
        for it in items_raw:
            results.append(ActionItem(
                task=it.get("task", ""),
                owner=it.get("owner", "Unassigned"),
                deadline=it.get("deadline", "None specified"),
                priority=it.get("priority", "MEDIUM"),
                context_quote=it.get("context_quote", ""),
                timestamp=it.get("timestamp", "00:00")
            ))
        return results

