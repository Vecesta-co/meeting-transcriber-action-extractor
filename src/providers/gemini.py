import json
import requests
from typing import List
from .base import BaseLLMProvider
from ..core.types import ActionItem

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        if not api_key:
            raise ValueError("GeminiProvider requires GEMINI_API_KEY.")
        self.api_key = api_key
        self.model = model

    @property
    def name(self) -> str:
        return "gemini"

    def extract_action_items(self, transcript_text: str) -> List[ActionItem]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            "You are an executive assistant. Review the following meeting transcript. "
            "Extract all commitments, tasks, owners, and deadlines. Return ONLY a valid JSON array of objects "
            "with keys: 'task', 'owner', 'deadline', 'priority' (HIGH/MEDIUM/LOW), 'context_quote', 'timestamp'.\n\n"
            f"TRANSCRIPT:\n{transcript_text}"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        items_raw = json.loads(raw_text)

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

