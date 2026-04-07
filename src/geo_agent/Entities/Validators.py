from typing import Annotated, Callable
from pydantic import AfterValidator

# Allow range based validation in pydantic models
def _score_between(start: float, end: float) -> Callable[[float], float]:
    def fn(value: float) -> float:
        if not (start <= value <= end):
            raise ValueError(f"{value} is not between {start} and {end}")
        return value
    return fn

# Standard annotated types in use
Between10 = Annotated[float, AfterValidator(_score_between(-10, 10))]
Between10p = Annotated[float, AfterValidator(_score_between(0, 10))]
Percentage = Annotated[float, AfterValidator(_score_between(0, 100))]