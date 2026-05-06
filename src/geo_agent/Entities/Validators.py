from typing import Annotated, Callable, Any
from pydantic import AfterValidator

# Allow range based validation in pydantic models
def _score_between(start: float | None, end: float | None) -> Callable[[float], float]:
    def fn(value: float) -> float:
        if (start is not None and start > value) or (end is not None and end < value):
            raise ValueError(f"{value} is not between {start or "inf"} and {end or "inf"}")
        return value
    return fn

def _score_between_int(start: int | None, end: int | None) -> Callable[[int], int]:
    def fn(value: int) -> int:
        if (start is not None and start > value) or (end is not None and end < value):
            raise ValueError(f"{value} is not between {start or "inf"} and {end or "inf"}")
        return value
    return fn

def length_between(start: int | None, end: int | None) -> Callable[[list[Any]], list[Any]]:
    def fn(value: list[Any]) -> list[Any]:
        size = len(value)
        if (start is not None and start > size) or (end is not None and end < size):
            raise ValueError(f"List length {value} is not between {start or "inf"} and {end or "inf"}")
        return value
    return fn

# Standard annotated types in use
Between10 = Annotated[float, AfterValidator(_score_between(-10, 10))]
Between10p = Annotated[float, AfterValidator(_score_between(0, 10))]
Percentage = Annotated[float, AfterValidator(_score_between(0, 100))]

Count = Annotated[int, AfterValidator(_score_between_int(1, None))] # must be >= 1