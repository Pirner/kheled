import requests
from typing import Any, Dict, List

class LMStudioClient:
    def __init__(self, base_url: str = "http://192.168.178.78:1234/v1", model: str = "local-model"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "temperature": 0.1
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        return response.json()
