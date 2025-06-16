import bson
from typing import Dict

from ..base import Converter


class BsonConverter(Converter[Dict, bytes]):
    def encode(self, source: Dict) -> bytes:
        return bson.dumps(source)

    def decode(self, target: bytes) -> Dict:
        return bson.loads(target)
