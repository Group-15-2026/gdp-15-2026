import json

from utils import get_top_dir, get_weekly_dir, get_monthly_dir, get_range_dir

TOP_CODE = "D"
WEEKLY_CODE = "W"
MONTHLY_CODE = "M"
RANGE_CODE = "R"
BY_CATEGORY_CODE = "C"
BY_SOURCE_CODE = "S"
BY_TOPIC_CODE = "T"

class _Index:
    def __init__(self, dir, code, time_dt):
        self._code = code
        self._dir = dir
        self._time_id = self._to_time_id(time_dt)
        self._topic = None

    def _to_time_id(self, time_dt):
        return time_dt.strftime("%Y%m%d")

    def set_topic(self, topic):
        self._topic = topic

    def get_topic(self):
        return self._topic

    def get_time_id(self):
        return self._time_id

    def get_file_id(self):
        return f"{self._time_id}-{self._code}"

    def get_file_path(self):
        file_name = f"{self.get_file_id()}.txt"
        return self._dir / file_name

    def save(self, articles):
        file_path = self.get_file_path()
        with open(file_path, "w") as f:
            json.dump(articles, f)
        return file_path

class _IndexRange(_Index):
    def __init__(self, code, start_dt, end_dt):
        self._code = code
        self._dir = get_range_dir()
        self._time_id = self._set_time_id(start_dt, end_dt)

    def _set_time_id(self, start_dt, end_dt):
        from_str = super()._to_time_id(start_dt)
        to_str = super()._to_time_id(end_dt)
        return f"{from_str}-{to_str}"

def index_top_by_category(time_dt):
    dir = get_top_dir()
    code = TOP_CODE + BY_CATEGORY_CODE
    return _Index(dir, code, time_dt)

def index_top_by_source(time_dt):
    dir = get_top_dir()
    code = TOP_CODE + BY_SOURCE_CODE
    return _Index(dir, code, time_dt)

def index_weekly_by_topic(topic, time_dt):
    dir = get_weekly_dir()
    code = WEEKLY_CODE + BY_TOPIC_CODE + topic
    return _Index(dir, code, time_dt)

def index_range_by_topic(topic, start_time_dt, end_time_dt):
    code = RANGE_CODE + BY_TOPIC_CODE + topic
    index = _IndexRange(code, start_time_dt, end_time_dt)
    index.set_topic(topic)
    return index