import datetime
from storage import DatetimeEventStore

store = DatetimeEventStore()

store.store_event(at=datetime.datetime(2024, 6, 15), data="meeting")
store.store_event(at=datetime.datetime(2024, 6, 20), data="deployment")
store.store_event(at=datetime.datetime(2024, 8, 1),  data="vacation")

for event in store.get_events(
    start=datetime.datetime(2024, 6, 1),
    end=datetime.datetime(2024, 7, 1),
):
    print(event)