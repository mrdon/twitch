from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List

import yaml
import pytz
from dateutil import parser
from slugify import slugify


@dataclass
class Event:
    start: datetime
    duration: timedelta
    title: str
    sections: List[Section]
    id: Optional[str] = None

    @property
    def slug(self):
        return slugify(self.title)


@dataclass
class Section:
    title: str
    byline: str


def get_scheduled_events() -> List[Event]:
    with open("../schedule/schedule.yaml", "r") as stream:
        try:
            schedule = yaml.safe_load(stream)["schedule"]
        except yaml.YAMLError as exc:
            print(exc)

    default_data = schedule["defaults"]

    events: List[Event] = []
    for event_data in schedule["events"]:
        data = dict(default_data)
        data.update(event_data)
        sections = []
        if "sections" in data:
            sections = [Section(title=s["title"], byline=s["byline"]) for s in data["sections"]]
        events.append(Event(start=_parse_as_mst_timezone(data["start"]),
                            # todo: properly parse duration
                            duration=timedelta(hours=int(data["duration"][:-1])),
                            title=data["title"],
                            sections=sections,
                            ))
    return events


def get_next_event() -> Optional[Event]:
    now = pytz.timezone('America/Denver').localize(datetime.now())
    next_event = None
    for event in get_scheduled_events():
        if event.start < now:
            continue

        if next_event is None or next_event.start > event.start:
            next_event = event

    return next_event


def _parse_as_mst_timezone(value: str) -> datetime:
    parsed = parser.parse(value)
    return pytz.timezone('America/Denver').localize(parsed)