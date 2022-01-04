import asyncio
from dataclasses import dataclass
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import evdev
import psutil
import yaml
from dateutil import parser
from evdev import ecodes
from obswebsocket import obsws, requests
from quart import current_app
from yaml import Loader

from director.obs import Connection
from director.schedule import get_next_event


def find_device(name):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if device.name == name:
            print(f"Found device: {device.path}")
            break
    else:
        print("Can't find clicker, skipping")
        exit(0)
    return device


def get_section_title(obs: Connection) -> str:
    element = obs.call(requests.GetTextFreetype2Properties("Section title"))
    return element.getText() if element else None


async def new_section(obs, title, byline):
    obs.call(requests.SetSceneItemRender("Section title", False))
    obs.call(requests.SetSceneItemRender("Section byline", False))
    obs.call(requests.SetTextFreetype2Properties("Section title", text=title))
    obs.call(requests.SetTextFreetype2Properties("Section byline", text=byline))
    obs.call(requests.SetSceneItemRender("Section title", True))
    obs.call(requests.SetSceneItemRender("Section byline", True))


async def _process_event(obs: Connection, code):
    from director.web import broadcast_to_clients

    if code == ecodes.KEY_RIGHT:
        # current_section_idx += 1
        # if len(sections) == current_section_idx:
        #     current_section_idx = 0
        await broadcast_to_clients("next")
    elif code == ecodes.KEY_LEFT:
        await broadcast_to_clients("prev")

    elif code == ecodes.KEY_POWER:
        obs.call(requests.SetCurrentScene("Slides - Green screen"))
    elif code == ecodes.KEY_PLAYPAUSE:
        obs.call(requests.SetCurrentScene("Slides - Green screen (zoom)"))
    elif code == ecodes.KEY_COMPOSE:
        obs.call(requests.SetCurrentScene("Slides - Firefox"))
    elif code == ecodes.KEY_BACK:
        obs.call(requests.SetCurrentScene("Coding - Webcam"))
    elif code == ecodes.KEY_UP:
        obs.call(requests.SetSceneItemRender("Window chat", True))
    elif code == ecodes.KEY_DOWN:
        obs.call(requests.SetSceneItemRender("Window chat", False))
    elif code == ecodes.KEY_VOLUMEUP:
        obs.call(requests.SetCurrentScene("Slides - Video"))
    else:
        print(f"Unknown key: {code}")

    # section = sections[current_section_idx]
    # new_section(obs, "", "")
    # obs.call(requests.SetCurrentScene("Interview - me (title)"))
    # new_section(obs, section["title"], section["byline"])


async def run():
    obs = current_app.obs
    event = get_next_event()
    if event:
        await new_section(obs, event.title, "$quote to change this")

    device = find_device("FC,LTD Mic Device Keyboard")
    with device.grab_context():
        print("grabbed context")
        async for event in device.async_read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:
                try:
                    await _process_event(obs, event.code)
                except Exception as e:
                    print(f"Exception processing event: {e}")
                
