import bson
from typing import Dict

from .base import BytesConverter, Converter


class BsonConverter(BytesConverter, Converter[Dict, bytes]):
    def encode(self, source: Dict) -> bytes:
        return bson.dumps(source)

    def decode(self, target: bytes) -> Dict:
        return bson.loads(target)
