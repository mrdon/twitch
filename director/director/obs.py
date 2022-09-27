from __future__ import annotations
import sys
import time

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from obsws_python.baseclient import ObsClient

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


log = logging.getLogger(__name__)


FFMPEG_SOURCE = "ffmpeg_source"

logging.basicConfig(level=logging.INFO)


class Connection:

    def __init__(self):
        host = "localhost"
        port = 4444
        password = "sleuth"
        self.started = False

        self.ws = ObsClient(host=host, port=port, password=password)

    def call(self, param: str, data: Optional[dict] = None):
        self._ensure_connected()
        if self.started:
            return self.ws.req(param, data)
        else:
            print(f"OBS not connected, skipping call {param}")
            return None

    def _ensure_connected(self):
        if self.started:
            return

        try:
            self.ws.authenticate()
        except Exception:
            print("ERROR: Connection refused for obs")
            return
        self.started = True


