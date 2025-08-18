import uuid

from task_helpers.tasks import Task
from .conftest import converter_stub


def test_encode_task(converter_stub, random_text: str):
    task = Task(data=random_text)
    encoded = converter_stub.encode(task)
    assert encoded is task


def test_encode_text(converter_stub, random_text: str):
    encoded = converter_stub.encode(random_text)
    assert encoded is random_text


def test_decode_task(converter_stub, random_text):
    task_id = uuid.uuid4()
    task_data = random_text
    excepted = Task(id=task_id, data=task_data)

    task = converter_stub.decode(excepted)
    assert excepted is task
    assert task.id == excepted.id
    assert task.data == excepted.data


def test_decode_text(converter_stub, random_text):
    decoded = converter_stub.decode(random_text)
    assert decoded is random_text


def test_encode_decode_cycle(converter_stub, random_text: str):
    task = Task(data=random_text)
    encoded = converter_stub.encode(task)
    decoded = converter_stub.decode(encoded)
    assert task.id == decoded.id
    assert task.data == decoded.data
