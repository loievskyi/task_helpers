import avro.schema
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
from typing import Any, Dict
import io

from ..base import Converter


class AvroConverter(Converter[Dict, bytes]):
    def __init__(self, schema_str: str):
        """
        Args:
            schema_str: Avro схема в JSON формате
        """
        self.schema = avro.schema.parse(schema_str)
        self.writer = DatumWriter(self.schema)
        self.reader = DatumReader(self.schema)

    def encode(self, source: Dict) -> bytes:
        bytes_io = io.BytesIO()
        encoder = BinaryEncoder(bytes_io)
        self.writer.write(source, encoder)
        return bytes_io.getvalue()

    def decode(self, target: bytes) -> Dict:
        bytes_io = io.BytesIO(target)
        decoder = BinaryDecoder(bytes_io)
        return self.reader.read(decoder)