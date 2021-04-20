import sys
import time

import logging
from dataclasses import dataclass
from typing import Optional

from obswebsocket.base_classes import Baserequests

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


@dataclass
class Section:
    title: str
    byline: str
    b_roll: str = None


class DevMattersShow:

    def __init__(self):
        self.conn = Connection()
        self.sections = {
            "intro": Section(
                title="Can devs and designers get along?",
                byline="Guest: Ben Sanders",
            ),
            "design-overview": Section(
                title="Can devs and designers get along?",
                byline="What does a designer do?",
                b_roll="/home/mrdon/dev/twitch/interview/B-ROLL/What does a designer do.webm"
            ),
            "get-along": Section(
                title="Can devs and designers get along?",
                byline="Guest: Ben Sanders",
                b_roll="/home/mrdon/dev/twitch/interview/B-ROLL/Can devs and designers get along.webm"
            ),
            "strategies": Section(
                title="Strategies",
                byline="What strategies would you recommend?",
                b_roll="/home/mrdon/dev/twitch/interview/B-ROLL/Strategies.webm"
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
