from typing import Type, TypeVar
from google.protobuf.message import Message

from ..base import Converter

Source = TypeVar("Source", bound=Message)

class ProtobufConverter(Converter[Source, bytes]):
    def __init__(self, message_class: Type[Source]):
        self.message_class = message_class

    def encode(self, source: Source) -> bytes:
        return source.SerializeToString()

    def decode(self, target: bytes) -> Source:
        message = self.message_class()
        message.ParseFromString(target)
        return message
