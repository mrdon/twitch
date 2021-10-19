import os
import sys
from datetime import datetime
from os import path
from pathlib import Path

import evdev
import yaml
from dateutil import parser
from obswebsocket import obsws, requests
from yaml import Loader

obs = obsws("localhost", 4444, "sleuth")
obs.connect()


devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if device.name == "Logitech USB Receiver":
        print(f"Found device: {device.path}")
        break
else:
    print("Can't find clicker, skipping")
    exit(0)


with open(f"../schedule/schedule.yaml", "r") as f:
    events = yaml.load(f, Loader=Loader)["schedule"]["events"]
    for event in events:
        start = parser.parse(event["start"])
        if start.date() == datetime.today().date():
            today_event = event
            break
    else:
        print("No events found for today, skipping")
        exit(0)

sections = today_event.get("sections", [])


def new_section(title, byline):
    obs.call(requests.SetTextFreetype2Properties("Interview bottom title", text=title))
    obs.call(requests.SetTextFreetype2Properties("Interview bottom title line 2", text=byline))


def run():
    current_section_idx = 0

    with device.grab_context():
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                if event.code == evdev.ecodes.KEY_PAGEDOWN:
                    current_section_idx += 1
                    if len(sections) == current_section_idx:
                        current_section_idx = 0

                elif event.code == evdev.ecodes.KEY_PAGEUP:
                    current_section_idx -= 1
                    if len(sections) < 0:
                        current_section_idx = len(sections) - 1

                section = sections[current_section_idx]
                new_section("", "")
                obs.call(requests.SetCurrentScene("Interview - me (title)"))
                new_section(section["title"], section["byline"])


run()


