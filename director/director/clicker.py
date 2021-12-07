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


def get_section_title(obs) -> str:
    element = obs.call(requests.GetTextFreetype2Properties("Interview bottom title"))
    return element.getText()


async def new_section(obs, title, byline):
    obs.call(requests.SetSceneItemRender("[Scene] Interview - lower third", False))
    obs.call(requests.SetTextFreetype2Properties("Interview bottom title", text=title))
    obs.call(requests.SetTextFreetype2Properties("Interview bottom title line 2", text=byline))
    obs.call(requests.SetSceneItemRender("[Scene] Interview - lower third", True))


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
        obs.call(requests.SetCurrentScene("Coding - Green screen"))
    elif code == ecodes.KEY_PLAYPAUSE:
        obs.call(requests.SetCurrentScene("Coding - Green screen (zoom)"))
    elif code == ecodes.KEY_COMPOSE:
        obs.call(requests.SetCurrentScene("Coding - Green screen (raw)"))
    elif code == ecodes.KEY_BACK:
        obs.call(requests.SetCurrentScene("Interview - me"))

    # elif code == ecodes.KEY_F5:
    #     obs.call(requests.SetCurrentScene("Interview - me (zoom)"))
    #     continue
    # elif code == ecodes.KEY_ESC:
    #     obs.call(requests.SetCurrentScene("Interview - me"))
    #     continue
    # elif code == ecodes.KEY_DOT:
    #     scene = obs.call(requests.GetCurrentScene())
    #     if scene.getName() == "Interview - me (firefox)":
    #         obs.call(requests.SetCurrentScene("Interview - me"))
    #     else:
    #         print(f"scene: {scene.getName()}")
    #         obs.call(requests.SetCurrentScene("Interview - me (firefox)"))
    #     continue
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
        await new_section(obs, event.title, "!quote to change this")

    device = find_device("FC,LTD Mic Device Keyboard")
    with device.grab_context():
        print("grabbed context")
        async for event in device.async_read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:
                try:
                    await _process_event(obs, event.code)
                except Exception as e:
                    print(f"Exception processing event: {e}")
                
