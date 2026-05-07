import datetime
import pytz
from typing import List, Dict


class TimeMatcher:
    WEEKDAY_MAP = {
        'mon': 0,
        'tue': 1,
        'wed': 2,
        'thu': 3,
        'fri': 4,
        'sat': 5,
        'sun': 6
    }

    def is_in_schedule(self, time_ranges: List[Dict], timezone: str) -> bool:
        tz = pytz.timezone(timezone)
        now = datetime.datetime.now(tz)
        today_weekday = now.weekday()
        current_time = now.time()

        for time_range in time_ranges:
            days = time_range.get("days", [])
            start_time = datetime.time.fromisoformat(time_range.get("start", "00:00"))
            end_time = datetime.time.fromisoformat(time_range.get("end", "23:59"))

            weekdays = [self.WEEKDAY_MAP.get(day.lower()) for day in days if day.lower() in self.WEEKDAY_MAP]
            
            if today_weekday not in weekdays:
                continue

            if start_time <= current_time <= end_time:
                return True

        return False