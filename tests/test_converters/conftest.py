import random
import string
from typing import TypeVar

import pytest

from task_helpers.converters.base import Converter
from task_helpers.converters.task import TaskTupleConverter
from task_helpers.converters.stub import ConverterStub

Type = TypeVar("Type")


class StrIntConverter(Converter[str, int]):
    def encode(self, source: str) -> int:
        return int(source)

    def decode(self, target: int) -> str:
        return str(target)


@pytest.fixture
def converter():
    return StrIntConverter()


class TestConverterStub(Converter[Type, Type]):
    def encode(self, source: Type) -> Type:
        return source

    def decode(self, target: Type) -> Type:
        return target


@pytest.fixture
def task_converter():
    return TaskTupleConverter(TestConverterStub())


@pytest.fixture
def converter_stub():
    return ConverterStub()


@pytest.fixture
def random_text() -> str:
    length = random.randint(10, 100)
    chars = string.ascii_letters
    return "".join(random.choice(chars) for _ in range(length))
