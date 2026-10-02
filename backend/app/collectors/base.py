from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
@dataclass
class CollectedItem:
    kind: str
    value: str
    source: str
    source_url: str|None
    normalized_value: str
    confidence: float
    raw_reference: str|None=None
class DataSourceAdapter(ABC):
    @abstractmethod
    def collect(self, target: str, **kwargs) -> list[CollectedItem]: ...
    @abstractmethod
    def health_check(self) -> bool: ...
    def normalize(self, value: Any) -> str: return str(value).strip().lower()
    @abstractmethod
    def get_source_name(self) -> str: ...
