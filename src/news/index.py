from datetime import datetime
import json

from utils import get_top_dir, get_weekly_dir, get_monthly_dir

TOP_CODE = "D"
WEEKLY_CODE = "W"
MONTHLY_CODE = "M"
BY_CATEGORY_CODE = "C"
BY_SOURCE_CODE = "S"
BY_TOPIC_CODE = "T"

class _Index:
    def __init__(self, dir, code):
        self._code = code
        self._dir = dir

    def _get_time_id(self, time_dt):
        return time_dt.strftime("%Y%m%d")

    def get_file_id(self, time_dt):
        time_str = self._get_time_id(time_dt)
        return f"{time_str}-{self._code}"

    def get_file_path(self, time_dt):
        file_name = f"{self.get_file_id(time_dt)}.txt"
        return self._dir / file_name

    def save(self, articles, time_dt):
        file_path = self.get_file_path(time_dt)
        with open(file_path, "w") as f:
            json.dump(articles, f)
        return file_path

def index_top_by_category():
    dir = get_top_dir()
    code = TOP_CODE + BY_CATEGORY_CODE
    return _Index(dir, code)

def index_top_by_source():
    dir = get_top_dir()
    code = TOP_CODE + BY_SOURCE_CODE
    return _Index(dir, code)

def index_weekly_by_topic(topic):
    dir = get_weekly_dir()
    code = WEEKLY_CODE + BY_TOPIC_CODE + topic
    return _Index(dir, code)
