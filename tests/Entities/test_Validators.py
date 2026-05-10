import pytest
from pydantic import BaseModel, ValidationError

from geo_agent.Entities.Validators import (
    Between10,
    Between10p,
    Percentage,
    Count,
    length_between,
    _score_between,
    _score_between_int,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class _B10(BaseModel):
    v: Between10

class _B10p(BaseModel):
    v: Between10p

class _Pct(BaseModel):
    v: Percentage

class _Count(BaseModel):
    v: Count


# ─────────────────────────────────────────────────────────────────────────────
# _score_between (float, both bounds present)
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreBetween:
    def _fn(self, lo, hi):
        return _score_between(lo, hi)

    def test_value_within_range_returned(self):
        fn = self._fn(0.0, 10.0)
        assert fn(5.0) == 5.0

    def test_lower_bound_accepted(self):
        assert self._fn(0.0, 10.0)(0.0) == 0.0

    def test_upper_bound_accepted(self):
        assert self._fn(0.0, 10.0)(10.0) == 10.0

    def test_below_lower_bound_raises(self):
        with pytest.raises(ValueError):
            self._fn(0.0, 10.0)(-0.1)

    def test_above_upper_bound_raises(self):
        with pytest.raises(ValueError):
            self._fn(0.0, 10.0)(10.1)

    def test_none_lower_bound_allows_any_low_value(self):
        assert self._fn(None, 10.0)(-999.0) == -999.0

    def test_none_upper_bound_allows_any_high_value(self):
        assert self._fn(0.0, None)(999.0) == 999.0

    def test_both_bounds_none_accepts_anything(self):
        fn = self._fn(None, None)
        assert fn(-1e9) == -1e9
        assert fn(1e9) == 1e9


# ─────────────────────────────────────────────────────────────────────────────
# _score_between_int (int, both bounds present)
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreBetweenInt:
    def _fn(self, lo, hi):
        return _score_between_int(lo, hi)

    def test_value_within_range_returned(self):
        assert self._fn(1, 10)(5) == 5

    def test_lower_bound_accepted(self):
        assert self._fn(1, 10)(1) == 1

    def test_upper_bound_accepted(self):
        assert self._fn(1, 10)(10) == 10

    def test_below_lower_bound_raises(self):
        with pytest.raises(ValueError):
            self._fn(1, 10)(0)

    def test_above_upper_bound_raises(self):
        with pytest.raises(ValueError):
            self._fn(1, 10)(11)

    def test_none_lower_bound_allows_any_low_value(self):
        assert self._fn(None, 10)(-100) == -100

    def test_none_upper_bound_allows_any_high_value(self):
        assert self._fn(1, None)(10_000) == 10_000


# ─────────────────────────────────────────────────────────────────────────────
# length_between
# ─────────────────────────────────────────────────────────────────────────────

class TestLengthBetween:
    def test_list_within_length_returned(self):
        fn = length_between(1, 5)
        lst = [1, 2, 3]
        assert fn(lst) is lst

    def test_exact_minimum_length_accepted(self):
        fn = length_between(2, 5)
        assert fn([1, 2]) == [1, 2]

    def test_exact_maximum_length_accepted(self):
        fn = length_between(1, 3)
        assert fn([1, 2, 3]) == [1, 2, 3]

    def test_too_short_raises(self):
        with pytest.raises(ValueError):
            length_between(2, 5)([1])

    def test_too_long_raises(self):
        with pytest.raises(ValueError):
            length_between(1, 3)([1, 2, 3, 4])

    def test_empty_list_accepted_when_min_is_zero(self):
        assert length_between(0, 5)([]) == []

    def test_empty_list_rejected_when_min_is_one(self):
        with pytest.raises(ValueError):
            length_between(1, 5)([])

    def test_none_lower_bound_accepts_empty_list(self):
        assert length_between(None, 5)([]) == []

    def test_none_upper_bound_accepts_long_list(self):
        lst = list(range(1000))
        assert length_between(1, None)(lst) is lst

    def test_both_bounds_none_accepts_any_list(self):
        fn = length_between(None, None)
        assert fn([]) == []
        assert fn(list(range(100))) == list(range(100))


# ─────────────────────────────────────────────────────────────────────────────
# Between10  (-10.0 … 10.0 inclusive)
# ─────────────────────────────────────────────────────────────────────────────

class TestBetween10:
    def test_zero_accepted(self):
        assert _B10(v=0.0).v == 0.0

    def test_lower_bound_accepted(self):
        assert _B10(v=-10.0).v == -10.0

    def test_upper_bound_accepted(self):
        assert _B10(v=10.0).v == 10.0

    def test_midpoint_accepted(self):
        assert _B10(v=5.5).v == 5.5

    def test_below_lower_bound_rejected(self):
        with pytest.raises(ValidationError):
            _B10(v=-10.1)

    def test_above_upper_bound_rejected(self):
        with pytest.raises(ValidationError):
            _B10(v=10.1)



# ─────────────────────────────────────────────────────────────────────────────
# Between10p  (0.0 … 10.0 inclusive)
# ─────────────────────────────────────────────────────────────────────────────

class TestBetween10p:
    def test_zero_accepted(self):
        assert _B10p(v=0.0).v == 0.0

    def test_upper_bound_accepted(self):
        assert _B10p(v=10.0).v == 10.0

    def test_midpoint_accepted(self):
        assert _B10p(v=5.0).v == 5.0

    def test_negative_rejected(self):
        with pytest.raises(ValidationError):
            _B10p(v=-0.1)

    def test_above_upper_bound_rejected(self):
        with pytest.raises(ValidationError):
            _B10p(v=10.1)



# ─────────────────────────────────────────────────────────────────────────────
# Percentage  (0.0 … 100.0 inclusive)
# ─────────────────────────────────────────────────────────────────────────────

class TestPercentage:
    def test_zero_accepted(self):
        assert _Pct(v=0.0).v == 0.0

    def test_hundred_accepted(self):
        assert _Pct(v=100.0).v == 100.0

    def test_midpoint_accepted(self):
        assert _Pct(v=50.0).v == 50.0

    def test_negative_rejected(self):
        with pytest.raises(ValidationError):
            _Pct(v=-0.1)

    def test_above_hundred_rejected(self):
        with pytest.raises(ValidationError):
            _Pct(v=100.1)



# ─────────────────────────────────────────────────────────────────────────────
# Count  (int ≥ 1)
# ─────────────────────────────────────────────────────────────────────────────

class TestCount:
    def test_one_accepted(self):
        assert _Count(v=1).v == 1

    def test_large_value_accepted(self):
        assert _Count(v=1_000_000).v == 1_000_000

    def test_zero_rejected(self):
        with pytest.raises(ValidationError):
            _Count(v=0)

    def test_negative_rejected(self):
        with pytest.raises(ValidationError):
            _Count(v=-1)

