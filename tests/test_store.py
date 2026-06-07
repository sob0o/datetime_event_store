import datetime
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from storage import DatetimeEventStore

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")

def reset():
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def test_store_and_retrieve():
    reset()
    store = DatetimeEventStore()
    store.store_event(at=datetime.datetime(2024, 6, 15), data="réunion")
    store.store_event(at=datetime.datetime(2024, 6, 20), data="déploiement")
    store.store_event(at=datetime.datetime(2024, 8, 1),  data="vacances")

    results = list(store.get_events(
        start=datetime.datetime(2024, 6, 1),
        end=datetime.datetime(2024, 7, 1),
    ))

    assert len(results) == 2
    assert results[0].data == "réunion"
    assert results[1].data == "déploiement"


def test_start_is_inclusive():
    reset()
    store = DatetimeEventStore()
    store.store_event(at=datetime.datetime(2024, 6, 1), data="exactement au début")

    results = list(store.get_events(
        start=datetime.datetime(2024, 6, 1),
        end=datetime.datetime(2024, 7, 1),
    ))

    assert len(results) == 1


def test_end_is_exclusive():
    reset()
    store = DatetimeEventStore()
    store.store_event(at=datetime.datetime(2024, 7, 1), data="exactement à la fin")

    results = list(store.get_events(
        start=datetime.datetime(2024, 6, 1),
        end=datetime.datetime(2024, 7, 1),
    ))

    assert len(results) == 0


def test_mauvais_type_leve_erreur():
    reset()
    store = DatetimeEventStore()

    try:
        store.store_event(at="2024-06-01", data="test")
        assert False, "aurait dû lever une TypeError"
    except TypeError:
        pass