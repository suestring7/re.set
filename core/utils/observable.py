from __future__ import annotations
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class Observable(Generic[T]):
    """Single-value observable. Notifies subscribers synchronously on assignment."""

    def __init__(self, initial: T) -> None:
        self._value = initial
        self._subs: list[Callable[[T], None]] = []

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new: T) -> None:
        self._value = new
        for fn in list(self._subs):
            fn(new)

    def subscribe(self, fn: Callable[[T], None]) -> None:
        self._subs.append(fn)

    def unsubscribe(self, fn: Callable[[T], None]) -> None:
        try:
            self._subs.remove(fn)
        except ValueError:
            pass
