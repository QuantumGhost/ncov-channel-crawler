import typing as tp

T = tp.TypeVar("T")


def identity(x: T) -> T:
    return x


class KeyedList(list):
    def __init__(self, it, *, key=None):
        if key is None:
            key = identity
        super().__init__(it)
        self._key = key

    def __getitem__(self, item):
        return self._key(super().__getitem__(item))
