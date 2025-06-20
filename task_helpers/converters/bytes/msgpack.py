import msgpack
from typing import Any

from .base import BytesConverter, Converter


class MsgPackConverter(BytesConverter, Converter[Any, bytes]):
    def encode(self, source: Any) -> bytes:
        return msgpack.packb(source)

    def decode(self, target: bytes) -> Any:
        return msgpack.unpackb(target)
