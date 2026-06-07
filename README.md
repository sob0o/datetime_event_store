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
├── .github/
│   └── workflows/
│       └── ci.yml
└── example.py
```

## How it works

### 1. Storing events in memory

Events are stored in two parallel sorted lists that always stay synchronized :

- `_keys` → list of timestamps (float) — used for searching
- `_events` → list of Event objects at the same index

```
_keys   = [ 1jan,  15jun,  20jun,  1aout ]
_events = [ event1, event2, event3, event4 ]
            index 0  index 1  index 2  index 3
```

The same index in both lists always refers to the same event.

### 2. Why bisect ?

When storing a new event, we need to insert it at the right position to keep the list sorted chronologically. This is where `bisect` comes in.

`bisect` uses binary search to find the correct index in O(log n) instead of scanning the entire list :

```
_keys = [ 1jan, 15jun, 1aout ]
I insert 20jun → bisect returns index 2

_keys = [ 1jan, 15jun, 20jun, 1aout ]  ✅ still sorted
```

The same index is then used to insert the Event object in `_events`, keeping both lists in sync.

When querying with `get_events`, `bisect` is used again to find the start and end positions of the range directly, without scanning the full list :

```
get_events(start=1jun, end=1juil)

bisect finds lo = 1  (first event >= 1jun)
bisect finds hi = 3  (first event >= 1juil)

_events[1:3] = [ event(15jun), event(20jun) ]  ✅
```

### 3. Persisting events in JSON

Events are saved in `data/events.json` after every `store_event` call. When the store is initialized, it automatically reloads all events from the file.

This means events survive between program restarts :

```json
[
  {
    "at": "2024-06-15T00:00:00",
    "data": "meeting"
  },
  {
    "at": "2024-06-20T00:00:00",
    "data": "deployment"
  }
]
```

A duplicate check prevents storing the same event (same datetime + same data) twice.

## Usage

```python
import datetime
from storage import DatetimeEventStore

store = DatetimeEventStore()

store.store_event(at=datetime.datetime(2024, 6, 15), data="meeting")
store.store_event(at=datetime.datetime(2024, 6, 20), data="deployment")

for event in store.get_events(
    start=datetime.datetime(2024, 6, 1),
    end=datetime.datetime(2024, 7, 1),
):
    print(event)

# Event(at=datetime.datetime(2024, 6, 15, 0, 0), data='meeting')
# Event(at=datetime.datetime(2024, 6, 20, 0, 0), data='deployment')
```

## API

### `store_event(at, data)`

Stores an event at the given datetime.

- `at` → `datetime.datetime` (raises `TypeError` if wrong type)
- `data` → any Python object

### `get_events(start, end)`

Returns all events in `[start, end)` in ascending order.

- `start` → inclusive
- `end` → exclusive
- Raises `ValueError` if `start >= end`

## Design choices

| Topic | Choice | Reason |
|-------|--------|--------|
| Data structure | Sorted list + `bisect` | O(log n) insert and range query, no dependencies |
| Persistence | JSON file | Simple, human-readable, no database needed |
| Range semantics | `[start, end)` | Standard Python convention |
| Event wrapper | Frozen dataclass | Immutable, readable, no raw tuples |
| Duplicate check | by `(at, data)` | Same event at same datetime is not stored twice |

## CI with GitHub Actions

Every push and pull request on `main` triggers an automated test run via GitHub Actions inside a Python 3.11 container.

This guarantees that the code works correctly in a clean environment on every change :

```
push to main
    │
    ▼
GitHub Actions starts a Python 3.11 container
    │
    ▼
pip install pytest
    │
    ▼
pytest tests/ -v
    │
    ├── all passed ✅ → green
    └── any failed ❌ → red, blocked
```

The workflow is defined in `.github/workflows/ci.yml`.

## Run tests locally

```bash
pip install pytest
pytest tests/ -v
```
