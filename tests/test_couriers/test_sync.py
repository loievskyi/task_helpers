import threading
import time
import uuid
from typing import Type

import pytest

from task_helpers.backends.sync import Backend
from task_helpers.couriers import Courier, ClientSideCourier, WorkerSideCourier
from task_helpers.exceptions import TaskResultDoesNotExist, TaskDoesNotExist
from task_helpers.serializers import TaskSerializer, TaskResultSerializer
from task_helpers.tasks import Task
from tests.conftest import mock_task_serializer, mock_task_result_serializer, backend, assert_blocks_longer_than


class TestCourier:
    @pytest.fixture
    def mock_courier(self, backend: Backend,
                     mock_task_serializer: TaskSerializer,
                     mock_task_result_serializer: TaskResultSerializer):
        return Courier(
            task_serializer=mock_task_serializer,
            task_result_serializer=mock_task_result_serializer,
            backend=backend,
            prefix_queue=f"test_prefix_{uuid.uuid4().hex[:8]}"
        )

    @pytest.fixture(params=[
        pytest.param(("simple", "value"), id="simple_data"),
        pytest.param({"url": "https://test.com"}, id="dict_data"),
        pytest.param(["list", "of", "strings"], id="list_data"),
    ])
    def sample_task_data(self, request):
        return request.param

    def test_add_task_to_queue(self, mock_courier, sample_task_data):
        task_id = mock_courier.add_task_to_queue("test_queue", sample_task_data)
        assert isinstance(task_id, uuid.UUID)

    def test_add_task_to_queue_get_task(self, mock_courier, sample_task_data):
        queue_name = "test_queue_name"
        task_id = mock_courier.add_task_to_queue(queue_name, sample_task_data)
        task = mock_courier.get_task(queue_name)
        assert isinstance(task, Task)
        assert task.id == task_id
        assert task.data == sample_task_data

    def test_bulk_add_task_to_queue(self, mock_courier, sample_task_data):
        tasks_data = [sample_task_data] * 10
        tasks_ids = mock_courier.bulk_add_tasks_to_queue("test_queue", tasks_data)
        assert len(tasks_ids) == len(tasks_data)

    def test_bulk_add_task_to_queue_if_no_data_provided(self, mock_courier):
        tasks_data = []
        tasks_ids = mock_courier.bulk_add_tasks_to_queue("test_queue", tasks_data)
        assert len(tasks_ids) == 0

    def test_courier_queue_works_as_fifo_with_single_operations(self, mock_courier):
        queue_name = "test_queue_name"
        first_task_data = {
            "id": 123,
            "function": "test_function",
            "args": ("arg1", "arg2"),
        }
        second_task_data = {
            "id": 456,
            "function": "test_function",
            "args": ("arg3", "arg4"),
        }

        first_task_id = mock_courier.add_task_to_queue(queue_name, first_task_data)
        second_task_id = mock_courier.add_task_to_queue(queue_name, second_task_data)
        first_task = mock_courier.get_task(queue_name)
        second_task = mock_courier.get_task(queue_name)
        assert first_task_id == first_task.id
        assert first_task_data == first_task.data
        assert second_task_id == second_task.id
        assert second_task_data == second_task.data

    def test_bulk_add_task_to_queue_adds_as_fifo(self, mock_courier):
        queue_name = "test_queue_name"
        count_tasks = 10

        tasks_data = [f"task_data_{n}" for n in range(count_tasks)]
        tasks_ids = mock_courier.bulk_add_tasks_to_queue(queue_name, tasks_data)

        for n in range(count_tasks):
            task_id = tasks_ids[n]
            task = mock_courier.get_task(queue_name)
            assert task.id == task_id
            assert task.data == tasks_data[n]

    def test_get_task_result_if_result_exists_with_delete_data_true(self, mock_courier):
        task_id = uuid.uuid4()
        excepted_task_result = "test_task_result"
        queue_name = "test_queue"
        mock_courier.return_task_result("test_queue", task_id, excepted_task_result)
        task_result = mock_courier.get_task_result(queue_name, task_id, delete_data=True)
        assert task_result == excepted_task_result
        with pytest.raises(TaskResultDoesNotExist):
            mock_courier.get_task_result(queue_name, task_id)

    def test_get_task_result_if_result_exists_with_delete_data_false(self, mock_courier):
        task_id = uuid.uuid4()
        excepted_task_result = "test_task_result"
        queue_name = "test_queue"
        mock_courier.return_task_result("test_queue", task_id, excepted_task_result)
        task_result = mock_courier.get_task_result(queue_name, task_id, delete_data=False)
        assert task_result == excepted_task_result

        task_result = mock_courier.get_task_result(queue_name, task_id, delete_data=False)
        assert task_result == excepted_task_result

    def test_get_task_result_if_result_not_exists_with_delete_data_true(self, mock_courier):
        task_id = uuid.uuid4()
        with pytest.raises(TaskResultDoesNotExist):
            mock_courier.get_task_result("test_queue", task_id, delete_data=True)

    def test_get_task_result_if_result_not_exists_with_delete_data_false(self, mock_courier):
        task_id = uuid.uuid4()
        with pytest.raises(TaskResultDoesNotExist):
            mock_courier.get_task_result("test_queue", task_id, delete_data=False)

    def test_wait_for_task_result_with_delete_data_true(self, mock_courier):
        task_id = uuid.uuid4()
        excepted_task_result = "test_task_result"
        queue_name = "test_queue"
        mock_courier.return_task_result("test_queue", task_id, excepted_task_result)
        task_result = mock_courier.wait_for_task_result(queue_name, task_id, delete_data=True)
        assert task_result == excepted_task_result

        # verify result deletion
        with pytest.raises(TaskResultDoesNotExist):
            mock_courier.get_task_result(queue_name, task_id)

    def test_wait_for_task_result_with_delete_data_false(self, mock_courier):
        task_id = uuid.uuid4()
        excepted_task_result = "test_task_result"
        queue_name = "test_queue"
        mock_courier.return_task_result("test_queue", task_id, excepted_task_result)
        task_result = mock_courier.wait_for_task_result(queue_name, task_id, delete_data=False)
        assert task_result == excepted_task_result

        # verify result not deleted
        task_result = mock_courier.get_task_result(queue_name, task_id, delete_data=False)
        assert task_result == excepted_task_result

    def test_wait_for_task_result_with_delayed_result(self, mock_courier, sample_task_data):
        def set_result(mock_courier_: Courier, queue_name_, task_id_, task_result_, sleep_seconds_):
            time.sleep(sleep_seconds_)
            mock_courier_.return_task_result(queue_name_, task_id_, task_result_)

        task_id = uuid.uuid4()
        queue_name = "test_queue_name"
        thread = threading.Thread(target=set_result, kwargs={
            "mock_courier_": mock_courier,
            "queue_name_": queue_name,
            "task_id_": task_id,
            "task_result_": sample_task_data,
            "sleep_seconds_": 1,
        })
        thread.start()

        real_task_result = mock_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id,
            delete_data=True)

        assert real_task_result == sample_task_data

    def test_wait_for_task_result_without_result_with_timeout(self, mock_courier):
        task_id = uuid.uuid4()
        with pytest.raises(TimeoutError):
            mock_courier.wait_for_task_result(
                queue_name="test_queue_name",
                task_id=task_id,
                timeout_seconds=1)

    @assert_blocks_longer_than(1)
    def test_wait_for_task_result_without_result_without_timeout(self, mock_courier):
        task_id = uuid.uuid4()
        mock_courier.wait_for_task_result(
            queue_name="test_queue_name",
            task_id=task_id
        )

    def test_check_for_done_if_result_not_exists(self, mock_courier):
        task_id = uuid.uuid4()
        exists = mock_courier.check_for_done("test_queue", task_id)
        assert isinstance(exists, bool)
        assert not exists

    def test_check_for_done_if_result_exists(self, mock_courier):
        task_id = uuid.uuid4()
        task_result = "test_task_result"
        mock_courier.return_task_result("test_queue", task_id, task_result)
        exists = mock_courier.check_for_done("test_queue", task_id)
        assert isinstance(exists, bool)
        assert exists

    def test_get_task_if_task_exists(self, mock_courier, sample_task_data):
        task_id = mock_courier.add_task_to_queue("test_queue", sample_task_data)
        task = mock_courier.get_task("test_queue")
        assert isinstance(task, Task)
        assert task.id == task_id
        assert task.data == sample_task_data

    def test_get_task_if_task_not_exists(self, mock_courier):
        with pytest.raises(TaskDoesNotExist):
            mock_courier.get_task("test_queue")

    def test_bulk_get_tasks_works_as_fifo(self, mock_courier):
        count_tasks = 10
        tasks_data = [f"task_data_{n}" for n in range(count_tasks)]

        tasks_ids = []
        for task_data in tasks_data:
            task_id = mock_courier.add_task_to_queue("test_queue", task_data)
            tasks_ids.append(task_id)

        tasks = mock_courier.bulk_get_tasks("test_queue", max_count=count_tasks)
        assert len(tasks) == len(tasks_ids)
        for n in range(count_tasks):
            task = tasks[n]
            assert isinstance(task, Task)
            assert task.id == tasks_ids[n]
            assert task.data == tasks_data[n]

    def test_bulk_get_tasks_if_no_tasks_exists(self, mock_courier):
        tasks = mock_courier.bulk_get_tasks("test_queue", max_count=10)
        assert len(tasks) == 0

    def test_bulk_get_tasks_if_tasks_exists_with_max_count(self, mock_courier):
        count_added_tasks = 10
        count_got_tasks = 5
        tasks_data = [f"task_data_{n}" for n in range(count_added_tasks)]
        tasks_ids = [mock_courier.add_task_to_queue("test_queue", task_data)
                     for task_data in tasks_data]

        tasks = mock_courier.bulk_get_tasks("test_queue", max_count=count_got_tasks)
        assert len(tasks) == count_got_tasks
        for n in range(count_got_tasks):
            task = tasks[n]
            assert isinstance(task, Task)
            assert task.id == tasks_ids[n]
            assert task.data == tasks_data[n]


    def test_wait_for_task(self, mock_courier, sample_task_data):
        task_id = mock_courier.add_task_to_queue("test_queue", sample_task_data)
        task = mock_courier.wait_for_task("test_queue")
        assert isinstance(task, Task)
        assert task.id == task_id
        assert task.data == sample_task_data

    def test_wait_for_task_with_delayed_task(self, mock_courier, sample_task_data):
        def set_task(mock_courier_: Courier, queue_name_, task_data_, sleep_seconds_):
            time.sleep(sleep_seconds_)
            mock_courier_.add_task_to_queue(queue_name_, task_data=task_data_)

        queue_name = "test_queue_name"
        thread = threading.Thread(target=set_task, kwargs={
            "mock_courier_": mock_courier,
            "queue_name_": queue_name,
            "task_data_": sample_task_data,
            "sleep_seconds_": 1,
        })
        thread.start()

        task = mock_courier.wait_for_task(queue_name=queue_name)
        assert task.data == sample_task_data

    def test_wait_for_task_without_task_with_timeout(self, mock_courier):
        with pytest.raises(TimeoutError):
            mock_courier.wait_for_task(
                queue_name="test_queue_name",
                timeout_seconds=1)

    @assert_blocks_longer_than(1)
    def test_wait_for_task_without_task_without_timeout(self, mock_courier):
        mock_courier.wait_for_task(queue_name="test_queue_name")

    def test_wait_for_task_works_as_fifo(self, mock_courier):
        count_tasks = 10
        tasks_data = [f"task_data_{n}" for n in range(count_tasks)]
        tasks_ids = []
        for task_data in tasks_data:
            task_id = mock_courier.add_task_to_queue("test_queue", task_data)
            tasks_ids.append(task_id)

        for n in range(count_tasks):
            task = mock_courier.wait_for_task("test_queue")
            assert isinstance(task, Task)
            assert task.id == tasks_ids[n]
            assert task.data == tasks_data[n]

    def test_bulk_wait_for_tasks_works_as_fifo(self, mock_courier):
        count_tasks = 10
        tasks_data = [f"task_data_{n}" for n in range(count_tasks)]
        tasks_ids = []
        for task_data in tasks_data:
            task_id = mock_courier.add_task_to_queue("test_queue", task_data)
            tasks_ids.append(task_id)

        tasks = mock_courier.bulk_wait_for_tasks("test_queue", max_count=count_tasks)
        assert len(tasks) == len(tasks_ids)
        for n in range(count_tasks):
            task = tasks[n]
            assert isinstance(task, Task)
            assert task.id == tasks_ids[n]
            assert task.data == tasks_data[n]

    def test_bulk_wait_for_tasks_with_delayed_tasks(self, mock_courier, sample_task_data):
        def set_tasks(mock_courier_: Courier, queue_name_, task_data_, sleep_seconds_):
            time.sleep(sleep_seconds_)
            mock_courier_.add_task_to_queue(queue_name_, task_data=task_data_)
            mock_courier_.add_task_to_queue(queue_name_, task_data=task_data_)

        queue_name = "test_queue_name"
        thread = threading.Thread(target=set_tasks, kwargs={
            "mock_courier_": mock_courier,
            "queue_name_": queue_name,
            "task_data_": sample_task_data,
            "sleep_seconds_": 1,
        })
        thread.start()

        # If no tasks are available initially - waits for the first one and returns it
        tasks = mock_courier.bulk_wait_for_tasks(queue_name=queue_name, max_count=2)
        assert len(tasks) == 1
        assert tasks[0].data == sample_task_data

    def test_bulk_wait_for_tasks_without_tasks_with_timeout(self, mock_courier):
        with pytest.raises(TimeoutError):
            mock_courier.bulk_wait_for_tasks(
                queue_name="test_queue_name",
                timeout_seconds=1,
                max_count=10)

    @assert_blocks_longer_than(1)
    def test_bulk_wait_for_tasks_without_tasks_without_timeout(self, mock_courier):
        mock_courier.bulk_wait_for_tasks(queue_name="test_queue_name", max_count=10)

    def test_bulk_wait_for_tasks_if_no_tasks_exists_with_timeout(self, mock_courier):
        with pytest.raises(TimeoutError):
            mock_courier.bulk_wait_for_tasks("test_queue", max_count=10, timeout_seconds=1)

    def test_bulk_wait_for_tasks_if_tasks_exists_with_max_count(self, mock_courier):
        count_added_tasks = 10
        count_got_tasks = 5
        tasks_data = [f"task_data_{n}" for n in range(count_added_tasks)]
        tasks_ids = [mock_courier.add_task_to_queue("test_queue", task_data)
                     for task_data in tasks_data]

        tasks = mock_courier.bulk_wait_for_tasks("test_queue", max_count=count_got_tasks)
        assert len(tasks) == count_got_tasks
        for n in range(count_got_tasks):
            task = tasks[n]
            assert isinstance(task, Task)
            assert task.id == tasks_ids[n]
            assert task.data == tasks_data[n]

    def test_return_task_result(self, mock_courier, sample_task_data):
        queue_name = "test_queue"
        task_id = uuid.uuid4()
        excepted_task_result = sample_task_data

        mock_courier.return_task_result(
            queue_name=queue_name,
            task_id=task_id,
            task_result=excepted_task_result)

        task_result = mock_courier.get_task_result(queue_name, task_id)
        assert task_result == excepted_task_result

    def test_return_task_result_without_timeout(self, mock_courier, sample_task_data):
        mock_courier.result_timeout_seconds = None
        queue_name = "test_queue"
        task_id = uuid.uuid4()
        excepted_task_result = sample_task_data

        mock_courier.return_task_result(
            queue_name=queue_name,
            task_id=task_id,
            task_result=excepted_task_result)

        task_result = mock_courier.get_task_result(queue_name, task_id)
        assert task_result == excepted_task_result

    def test_return_task_result_result_expires_after_timeout(self, mock_courier, sample_task_data):
        mock_courier.result_timeout_seconds = 1
        queue_name = "test_queue"
        task_id = uuid.uuid4()
        excepted_task_result = sample_task_data

        mock_courier.return_task_result(
            queue_name=queue_name,
            task_id=task_id,
            task_result=excepted_task_result)

        time.sleep(1.1)
        with pytest.raises(TaskResultDoesNotExist):
            mock_courier.get_task_result(queue_name, task_id)

    def test_return_task_result_result_persists_within_timeout(self, mock_courier, sample_task_data):
        mock_courier.result_timeout_seconds = 2
        queue_name = "test_queue"
        task_id = uuid.uuid4()
        excepted_task_result = sample_task_data

        mock_courier.return_task_result(
            queue_name=queue_name,
            task_id=task_id,
            task_result=excepted_task_result)

        time.sleep(1)
        task_result = mock_courier.get_task_result(queue_name, task_id)
        assert task_result == excepted_task_result

    def test_bulk_return_task_results(self, mock_courier):
        queue_name = "test_queue"
        count_tasks = 10
        tasks = [Task(data=None, result=f"test_task_data_{n}") for n in range(count_tasks)]

        mock_courier.bulk_return_tasks_results(
            queue_name=queue_name,
            tasks=tasks)

        for task in tasks:
            task_result = mock_courier.get_task_result(queue_name, task.id)
            assert task_result == task.result

    def test_bulk_return_task_results_without_timeout(self, mock_courier):
        mock_courier.result_timeout_seconds = None
        queue_name = "test_queue"
        count_tasks = 10
        tasks = [Task(data=None, result=f"test_task_data_{n}") for n in range(count_tasks)]

        mock_courier.bulk_return_tasks_results(
            queue_name=queue_name,
            tasks=tasks)

        for task in tasks:
            task_result = mock_courier.get_task_result(queue_name, task.id)
            assert task_result == task.result

    def test_bulk_return_task_results_results_expires_after_timeout(self, mock_courier):
        mock_courier.result_timeout_seconds = 1
        queue_name = "test_queue"
        count_tasks = 10
        tasks = [Task(data=None, result=f"test_task_data_{n}") for n in range(count_tasks)]

        mock_courier.bulk_return_tasks_results(
            queue_name=queue_name,
            tasks=tasks)
        time.sleep(1.1)

        for task in tasks:
            with pytest.raises(TaskResultDoesNotExist):
                mock_courier.get_task_result(queue_name, task.id)


    def test_bulk_return_task_results_results_persists_within_timeout(self, mock_courier):
        mock_courier.result_timeout_seconds = 2
        queue_name = "test_queue"
        count_tasks = 10
        tasks = [Task(data=None, result=f"test_task_data_{n}") for n in range(count_tasks)]

        mock_courier.bulk_return_tasks_results(
            queue_name=queue_name,
            tasks=tasks)
        time.sleep(1.1)

        for task in tasks:
            task_result = mock_courier.get_task_result(queue_name, task.id)
            assert task_result == task.result


class TestCouriersInit:
    @pytest.fixture(params=[
        pytest.param(ClientSideCourier, id="client_side"),
        pytest.param(WorkerSideCourier, id="worker_side"),
        pytest.param(Courier, id="all_side"),
    ])
    def courier_class(self, request):
        return request.param


    def test_client_side_courier_init_with_kwargs(
            self, courier_class: Type[ClientSideCourier | WorkerSideCourier | Courier],
            backend: Backend,
            mock_task_serializer: TaskSerializer,
            mock_task_result_serializer: TaskResultSerializer):
        """Test that kwargs are properly set as attributes"""
        custom_prefix = f"custom_prefix_{uuid.uuid4().hex[:8]}"
        custom_timeout = 300
        custom_param = "test_value"

        courier = courier_class(
            task_serializer=mock_task_serializer,
            task_result_serializer=mock_task_result_serializer,
            backend=backend,
            prefix_queue=custom_prefix,
            result_timeout_seconds=custom_timeout,
            custom_parameter=custom_param
        )

        # Verify that kwargs were set as attributes
        assert courier.task_serializer == mock_task_serializer
        assert courier.task_result_serializer == mock_task_result_serializer
        assert courier.backend == backend
        assert courier.prefix_queue == custom_prefix
        assert courier.result_timeout_seconds == custom_timeout
        assert hasattr(courier, "custom_parameter")
        assert getattr(courier, "custom_parameter") == custom_param

    def test_client_side_courier_init_without_kwargs(
            self, courier_class: Type[ClientSideCourier | WorkerSideCourier | Courier],
            backend: Backend,
            mock_task_serializer: TaskSerializer,
            mock_task_result_serializer: TaskResultSerializer):
        """Test courier initialization without additional kwargs"""
        courier = courier_class(
            task_serializer=mock_task_serializer,
            task_result_serializer=mock_task_result_serializer,
            backend=backend
        )

        # Verify basic attributes are set
        assert courier.task_serializer == mock_task_serializer
        assert courier.task_result_serializer == mock_task_result_serializer
        assert courier.backend == backend
        # Default values should be preserved
        assert courier.prefix_queue == ""  # default value
        if isinstance(courier, WorkerSideCourier):
            assert courier.result_timeout_seconds == 600  # default value
