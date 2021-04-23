from __future__ import annotations
import sys
import time

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict

import yaml
from obswebsocket.base_classes import Baserequests

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


log = logging.getLogger(__name__)


FFMPEG_SOURCE = "ffmpeg_source"

logging.basicConfig(level=logging.INFO)

from obswebsocket import obsws, requests  # noqa: E402


class Connection:

    def __init__(self):
        host = "localhost"
        port = 4444
        password = "sleuth"

        self.ws = obsws(host, port, password)

    def connect(self):
        self.ws.connect()

    def call(self, request: Baserequests) -> Baserequests:
        return self.ws.call(request)

    def disconnect(self):
        self.ws.disconnect()


shows = {}


def load_show(show_name: str):
    if show_name not in shows:
        shows[show_name] = Show(show_name)

    return shows[show_name]


class Show:

    def __init__(self, show_name: str):
        self.name = show_name
        started = datetime.now()
        with open(f"shows/{show_name}.yml", "r") as f:
            data = yaml.load(f, Loader=Loader)["show"]

        self.sections: Dict[str, Section] = {}
        for key, sdata in data["sections"].items():
            self.sections[key] = Section(title=sdata["title"],
                                    byline=sdata["byline"],
                                    b_roll=sdata.get("b_roll"))

        self.scenes: List[Scene] = []
        for sdata in data["scenes"]:
            self.scenes.append(Scene(label=sdata["label"], obs_name=sdata["obs_name"]))

        elapsed = (datetime.now() - started).total_seconds()
        log.info(f"Took {elapsed} second(s) ")


@dataclass
class Section:
    title: str
    byline: str
    b_roll: str = None


@dataclass
class Scene:
    label: str
    obs_name: str


class DevMattersShow:

    def __init__(self):
        self.conn = Connection()
        self.sections = {
            "intro": Section(
                title="How NOT to go from side project to startup",
                byline="Dylan Etkin | @detkin",
            ),
            "types": Section(
                title="Which side projects make terrible startups?",
                byline="Hint: your game engine is one",
                b_roll="/home/mrdon/dev/twitch/interview/B-ROLL/s1e03/Side Project Broll 1 NEW.webm"
            ),
            "sleuth-story": Section(
                title="The Sleuth story",
                byline="Where did Dylan mess up? :)",
                b_roll="/home/mrdon/dev/twitch/interview/B-ROLL/s1e03/Side Project Sleuth Story.webm"
            ),
            "lessons-learned": Section(
                title="Lessons learned",
                byline="Tips for your side project",
                b_roll="/home/mrdon/dev/twitch/interview/B-ROLL/s1e03/Side Project Broll 2 NEW.webm"
            ),
            "questions": Section(
                title="Open Questions",
                byline="Ok Twitch, what are your questions?",
            )
        }

    def start(self):
        self.conn.connect()

    def end(self):
        self.conn.disconnect()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.end()

    def set_scene(self, name: str):
        if "(b-roll)" in name:
            self.conn.call(requests.PlayPauseMedia("b-roll", False))
        else:
            self.conn.call(requests.PlayPauseMedia("b-roll", True))

        self.conn.call(requests.SetCurrentScene(name))

    def set_section(self, title: Optional[str] = None, byline: Optional[str] = None,
                    guest_1_title: Optional[str] = None, guest_2_title: Optional[str] = None, b_roll: Optional[str] = None):
        if title is not None:
            self.conn.call(requests.SetTextFreetype2Properties("Interview bottom title", text=title or ""))
    
        if byline is not None:
            self.conn.call(requests.SetTextFreetype2Properties("Interview bottom title line 2", text=byline or ""))
    
        if guest_1_title is not None:
            self.conn.call(requests.SetTextFreetype2Properties("Interview - lower third guest 1", text=guest_1_title or ""))
    
        if guest_2_title is not None:
            self.conn.call(requests.SetTextFreetype2Properties("Interview - lower third guest 2", text=guest_2_title or ""))
    
        if b_roll:
            self.conn.call(requests.SetSourceSettings(sourceName="b-roll", sourceType=FFMPEG_SOURCE, sourceSettings=dict(
                                              setVisible=True,
                                              local_file=b_roll,
                                          )))
