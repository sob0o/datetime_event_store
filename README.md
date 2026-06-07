# DatetimeEventStore

A lightweight Python package to store and query events associated with datetimes.

## Structure

```
datetime_event_store/
├── storage/
│   ├── __init__.py
│   └── store.py
├── tests/
│   └── test_store.py
├── data/
│   └── events.json
└── example.py
```

## How it works

Events are stored in two parallel sorted lists :

- `_keys` → timestamps (float) used for binary search
- `_events` → Event objects at the same index

Insertion and range queries use Python's `bisect` module for efficiency. Events are persisted in `data/events.json` and reloaded automatically on startup.

## Usage

```python
import datetime
from storage import DatetimeEventStore

store = DatetimeEventStore()

store.store_event(at=datetime.datetime(2024, 6, 15), data="meeting")

for event in store.get_events(
    start=datetime.datetime(2024, 6, 1),
    end=datetime.datetime(2024, 7, 1),
):
    print(event)
```

## API

### `store_event(at, data)`

Stores an event at the given datetime.

- `at` → `datetime.datetime`
- `data` → any Python object

### `get_events(start, end)`

Returns all events in `[start, end)` in ascending order.

- `start` → inclusive
- `end` → exclusive

## Run tests

```bash
pip install pytest
pytest tests/ -v
```
