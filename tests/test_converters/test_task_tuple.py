import random
import string
import uuid

import pytest

from task_helpers.converters.task_tuple import TaskTupleConverter
from task_helpers.tasks import Task


@pytest.fixture
def converter():
    return TaskTupleConverter()


@pytest.fixture
def random_text() -> str:
    length = random.randint(10, 100)
    chars = string.ascii_letters
    return "".join(random.choice(chars) for _ in range(length))


def test_encode_task(converter, random_text: str):
    task = Task(data=random_text)
    encoded = converter.encode(task)
    assert isinstance(encoded, tuple)


def test_decode_task(converter, random_text):
    task_id = uuid.uuid4()
    task_data = random_text
    source = (task_id.bytes, task_data)
    excepted = Task(id=task_id, data=task_data)

    task = converter.decode(source)
    assert isinstance(task, Task)
    assert task.id == excepted.id
    assert task.data == excepted.data

def test_encode_decode_cycle(converter, random_text: str):
    task = Task(data=random_text)
    encoded = converter.encode(task)
    decoded = converter.decode(encoded)
    assert task.id == decoded.id
    assert task.data == decoded.data
