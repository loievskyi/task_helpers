import csv
from typing import List, Any
from io import StringIO

from ..base import Converter


class CsvConverter(Converter[List[dict], bytes]):
    def encode(self, source: List[dict]) -> bytes:
        if not source:
            return b""
        output = StringIO()
        fieldnames = source[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(source)
        return output.getvalue().encode('utf-8')

    def decode(self, target: bytes) -> List[dict]:
        if not target:
            return []
        input_str = target.decode('utf-8')
        input_io = StringIO(input_str)
        reader = csv.DictReader(input_io)
        return list(reader)