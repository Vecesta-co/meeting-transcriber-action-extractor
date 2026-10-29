from abc import ABC, abstractmethod
from typing import List, Optional
from ..core.types import ActionItem

class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def extract_action_items(self, transcript_text: str) -> List[ActionItem]:
        pass

