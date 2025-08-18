from typing import TypeVar

import pytest

from task_helpers.converters.base import Converter
from task_helpers.converters.bytes import PickleConverter, MsgPackConverter
from task_helpers.converters.custom_type import CustomTypeConverter
from task_helpers.converters.perform_task_error import PerformTaskErrorTupleConverter
from task_helpers.converters.stub import ConverterStub
from task_helpers.converters.task import TaskTupleConverter

Type = TypeVar("Type")


class StrIntConverter(Converter[str, int]):
    def encode(self, source: str) -> int:
        return int(source)

    def decode(self, target: int) -> str:
        return str(target)


@pytest.fixture
def mock_converter():
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
def perform_task_error_converter(task_converter):
    return PerformTaskErrorTupleConverter(task_converter)


@pytest.fixture
def custom_type_converter(task_converter, converter_stub):
    perform_task_error_converter = PerformTaskErrorTupleConverter(task_converter)
    return CustomTypeConverter(
        perform_task_error_converter=perform_task_error_converter,
        task_converter=task_converter,
        converter_stub=converter_stub
    )


@pytest.fixture(params=[
    pytest.param(PickleConverter, id="pickle"),
    pytest.param(MsgPackConverter, id="msgpack"),
])
def bytes_converter(request):
    converter_class = request.param
    return converter_class()
