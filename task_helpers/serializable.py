import pickle
from abc import abstractmethod, ABC
from collections.abc import Callable

import msgpack


class AbstractSerializable(ABC):
    dumps_method: Callable = pickle.dumps
    loads_method: Callable = pickle.loads

    @abstractmethod
    def serialize(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, serialized_obj):
        raise NotImplementedError


class PickleSerializable(AbstractSerializable, ABC):
    dumps_method: Callable = pickle.dumps
    loads_method: Callable = pickle.loads


class MsgpackSerializable(AbstractSerializable, ABC):
    dumps_method: Callable = msgpack.dumps
    loads_method: Callable = msgpack.loads
