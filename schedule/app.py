import requests
import pytz
import yaml
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from dateutil import parser

token = os.environ.get("TWITCH_API_TOKEN")

@dataclass
class Event:
    start: datetime
    duration: timedelta
    title: str
    id: Optional[str] = None


def _parse_as_mst_timezone(value: str) -> datetime:
    parsed = parser.parse(value)
    return pytz.timezone('America/Denver').localize(parsed)


def get_scheduled_events() -> List[Event]:
    with open("schedule.yaml", "r") as stream:
        try:
            schedule = yaml.safe_load(stream)["schedule"]
        except yaml.YAMLError as exc:
            print(exc)
    
    default_data = schedule["defaults"]
    
    events: List[Event] = []
    for event_data in schedule["events"]:
        data = dict(default_data)
        data.update(event_data)
        events.append(Event(start=_parse_as_mst_timezone(data["start"]),
                            # todo: properly parse duration
                            duration=timedelta(hours=int(data["duration"][:-1])),
                            title=data["title"],
                    ))
    return events


def get_twitch_events() -> List[Event]:
    resp = requests.get("https://api.twitch.tv/helix/schedule?broadcaster_id=78371921", 
            headers={"authorization": f"Bearer {token}", "client-id": "5lhgwarlwdpq52732kvc5d076ddv97"})
    
    events: List[Event] = []
    resp_data = resp.json()
    segments = resp_data["data"]["segments"] if "data" in resp_data else []
    for segment in segments or []:
        events.append(Event(
            start=parser.parse(segment['start_time']),
            duration=parser.parse(segment['end_time'])-parser.parse(segment['start_time']),
            title=segment['title'],
            id=segment['id']))
    return events


def add_twitch_event(event: Event):
     resp = requests.post("https://api.twitch.tv/helix/schedule/segment?broadcaster_id=78371921", 
            headers={"authorization": f"Bearer {token}", "client-id": "5lhgwarlwdpq52732kvc5d076ddv97"},
            json={"start_time": event.start.isoformat(),
                  "timezone": "MST",
                  "is_recurring": False,
                  "duration": event.duration.total_seconds() / 60,
                  "title": event.title})
     print(f"resp: {resp.text}")
    
def update_twitch_event(existing_id: str, event: Event):
    resp = requests.patch(f"https://api.twitch.tv/helix/schedule/segment?broadcaster_id=78371921&id={existing_id}", 
           headers={"authorization": f"Bearer {token}", "client-id": "5lhgwarlwdpq52732kvc5d076ddv97"},
           json={"start_time": event.start.isoformat(),
                 "timezone": "America/Denver",
                 "is_recurring": False,
                 "duration": event.duration.total_seconds() / 60,
                 "title": event.title})
    print(f"resp: {resp.text}")
   
existing = get_twitch_events()
events = get_scheduled_events()

for event in events:
    for existing_event in existing:
        if existing_event.start == event.start:
            if existing_event.title != event.title:
                update_twitch_event(existing_event.id, event)
            break
    else:
        add_twitch_event(event)


#print(f"Existing: {existing}")
#print(f"Events: {events}")

#print(f"{resp.json()}")
# load the yaml file
# create the twitch client
# read the schedules
# see if the loaded events are there
# create missing loaded events
# exit
