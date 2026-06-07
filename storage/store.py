import bisect
import datetime
import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Event:
    at: datetime.datetime
    data: Any


DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")


class DatetimeEventStore:
    def __init__(self):
        self._keys = []
        self._events = []
        self._load()

    def _load(self):
        with open(DATA_FILE, "r") as f:
            raw = json.load(f)
        for item in raw:
            at = datetime.datetime.fromisoformat(item["at"])
            data = item["data"]
            event = Event(at=at, data=data)
            ts = at.timestamp()
            idx = bisect.bisect_right(self._keys, ts)
            self._keys.insert(idx, ts)
            self._events.insert(idx, event)

    def _save(self):
        raw = [{"at": e.at.isoformat(), "data": e.data} for e in self._events]
        with open(DATA_FILE, "w") as f:
            json.dump(raw, f, indent=2)

    def store_event(self, at: datetime.datetime, data: Any) -> Event:
        if not isinstance(at, datetime.datetime):
            raise TypeError(f"'at' must be a datetime, got: {type(at).__name__}")

        # duplicate check
        ts = at.timestamp()
        if ts in self._keys:
            existing_idx = self._keys.index(ts)
            if self._events[existing_idx].data == data:
                return self._events[existing_idx]

        event = Event(at=at, data=data)

        idx = bisect.bisect_right(self._keys, ts)
        self._keys.insert(idx, ts)
        self._events.insert(idx, event)

        self._save()
        return event

    def get_events(self, start: datetime.datetime, end: datetime.datetime):
        if not isinstance(start, datetime.datetime):
            raise TypeError(f"'start' must be a datetime, got: {type(start).__name__}")
        if not isinstance(end, datetime.datetime):
            raise TypeError(f"'end' must be a datetime, got: {type(end).__name__}")
        if start >= end:
            raise ValueError(f"'start' must be before 'end'")

        ts_start = start.timestamp()
        ts_end = end.timestamp()

        lo = bisect.bisect_left(self._keys, ts_start)
        hi = bisect.bisect_left(self._keys, ts_end)

        yield from self._events[lo:hi]