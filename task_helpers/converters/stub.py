from typing import TypeVar

from .base import Converter

Type = TypeVar("Type")


class ConverterStub(Converter[Type, Type]):
    def encode(self, source: Type) -> Type:
        return source

    def decode(self, target: Type) -> Type:
        return target
