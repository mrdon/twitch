
import sys
import time

import logging
from typing import Optional

from obswebsocket.base_classes import Baserequests

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


def set_episode(ws: Connection, title: str, byline: str, guest_1_title, guest_2_title: Optional[str] = None, b_roll: Optional[str] = None):

    ws.call(requests.SetTextFreetype2Properties("Interview bottom title", text=title or ""))
    ws.call(requests.SetTextFreetype2Properties("Interview bottom title line 2", text=byline or ""))
    ws.call(requests.SetTextFreetype2Properties("Interview - lower third guest 1", text=guest_1_title or ""))
    ws.call(requests.SetTextFreetype2Properties("Interview - lower third guest 2", text=guest_2_title or ""))


if __name__ == "__main__":
    conn = Connection()
    conn.connect()
    set_episode(
        ws=conn,
        title="TEST",
        byline="Are two Daniels two too many?",
        guest_1_title="Daniel - Taipe Designs",
        guest_2_title="",
        b_roll="/home/mrdon/Videos/slideshow.mp4",
    )
