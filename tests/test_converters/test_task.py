import uuid

from task_helpers.tasks import Task
from .conftest import task_converter, random_text


def test_encode_task(task_converter, random_text: str):
    task = Task(data=random_text)
    encoded = task_converter.encode(task)
    assert isinstance(encoded, tuple)


def test_decode_task(task_converter, random_text):
    task_id = uuid.uuid4()
    task_data = random_text
    source = (task_id.bytes, task_data)
    excepted = Task(id=task_id, data=task_data)

    task = task_converter.decode(source)
    assert isinstance(task, Task)
    assert task.id == excepted.id
    assert task.data == excepted.data


def test_encode_decode_cycle(task_converter, random_text: str):
    task = Task(data=random_text)
    encoded = task_converter.encode(task)
    decoded = task_converter.decode(encoded)
    assert task.id == decoded.id
    assert task.data == decoded.data
