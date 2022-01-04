from __future__ import annotations
import sys
import time

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict

import yaml
from obswebsocket.base_classes import Baserequests
from obswebsocket.exceptions import ConnectionFailure

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
        self.started = False

        self.ws = obsws(host, port, password)

    def call(self, request: Baserequests) -> Optional[Baserequests]:
        self._ensure_connected()
        if self.started:
            return self.ws.call(request)
        else:
            print(f"OBS not connected, skipping call {request}")
            return None

    def _ensure_connected(self):
        if self.started:
            return

        try:
            self.ws.connect()
        except ConnectionFailure:
            print("ERROR: Connection refused for obs")
            return
        self.started = True


