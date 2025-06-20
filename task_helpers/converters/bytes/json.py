import json
from typing import Any

from .base import BytesConverter, Converter


class JsonConverter(BytesConverter, Converter[Any, bytes]):
    def encode(self, source: Any) -> bytes:
        return json.dumps(source).encode("utf-8")

    def decode(self, target: bytes) -> Any:
        return json.loads(target.decode("utf-8"))
