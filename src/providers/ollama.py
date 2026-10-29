import json
import requests
from typing import List
from .base import BaseLLMProvider
from ..core.types import ActionItem

class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama3.2", endpoint: str = "http://127.0.0.1:11434"):
        self.model = model
        self.endpoint = endpoint.rstrip("/")

    @property
    def name(self) -> str:
        return "ollama"

    def extract_action_items(self, transcript_text: str) -> List[ActionItem]:
        url = f"{self.endpoint}/api/generate"
        prompt = (
            "Extract meeting action items from the transcript. Output valid JSON array with keys: "
            "'task', 'owner', 'deadline', 'priority', 'context_quote', 'timestamp'.\n\n"
            f"TRANSCRIPT:\n{transcript_text}"
        )

        resp = requests.post(
            url,
            json={"model": self.model, "prompt": prompt, "format": "json", "stream": False},
            timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        raw_text = data.get("response", "[]").strip()
        items_raw = json.loads(raw_text)
        if isinstance(items_raw, dict):
            items_raw = items_raw.get("action_items", items_raw.get("items", []))

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

