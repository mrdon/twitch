import os
import sys
from dataclasses import dataclass
from datetime import datetime
from os import path
from pathlib import Path
from typing import Optional

import evdev
import psutil
import yaml
from dateutil import parser
from evdev import UInput, ecodes, AbsInfo
from evdev import ecodes as e
from obswebsocket import obsws, requests
from pynput.mouse import Controller
from yaml import Loader


def connect_obs():
    obs = obsws("localhost", 4444, "sleuth")
    obs.connect()
    return obs


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


def get_talking_points():
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
    print(f"Found for today: {sections}")
    return sections


def new_section(obs, title, byline):
    obs.call(requests.SetTextFreetype2Properties("Section title", text=title))
    obs.call(requests.SetTextFreetype2Properties("Section byline", text=byline))


# When power button pressed:
# - Start obs if not already started
# - Open obs preview window and move to teleprompter, make always on top, resize
# - Open Twitch chat in firefox, hide sidebar, move to teleprompter, maximize
# - Start Tau


@dataclass
class State:
    obs_pid: Optional[int] = None


def run():
    obs = connect_obs()
    device = find_device("FC,LTD Mic Device Keyboard")
    mouse = evdev.InputDevice("/dev/input/event6")
    sections = get_talking_points()
    current_section_idx = 0
    state = State()

    # print(f"mouse: {mouse}")
    # with mouse.grab_context():
    #     ui = UInput.from_device(mouse)
    #     print("reading")
    #     for event in mouse.read_loop():
    #         print(f"event: {event}")
    #         ui.write_event(event)


    with device.grab_context():
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:
                if event.code == ecodes.KEY_POWER:
                    try:
                        process: psutil.Process = next(p for p in psutil.process_iter() if p.name() == "obs")
                        state.obs_pid = process.pid
                        print(f"Process: {process.pid}")
                    except StopIteration:
                        # todo: start obs!
                        pass

                    # ui = UInput.from_device(mouse)
                    # # print(f"evdev: {ui.capabilities(verbose=True).keys()}")
                    # ui.write(ecodes.EV_REL, ecodes.REL_X, -10)
                    # ui.write(ecodes.EV_REL, ecodes.REL_Y, -10)
                    # # ui.write(e.EV_ABS, e.ABS_X, 20)
                    # # ui.write(e.EV_ABS, e.ABS_Y, 20)
                    # ui.syn()
                    # ui.close()

                    import pygetwindow as gw
                    for window in gw.getAllWindows():
                        print(f"window: {window}")
                    #
                    # mouse = Controller()
                    # mouse.position = (10, 20)


                if event.code == ecodes.KEY_PAGEDOWN:
                    # current_section_idx += 1
                    # if len(sections) == current_section_idx:
                    #     current_section_idx = 0
                    obs.call(requests.SetCurrentScene("Coding - Green screen"))

                elif event.code == ecodes.KEY_PAGEUP:
                    # current_section_idx -= 1
                    # if len(sections) < 0:
                    #     current_section_idx = len(sections) - 1
                    obs.call(requests.SetCurrentScene("Coding - Green screen (zoom)"))
                # elif event.code == ecodes.KEY_F5:
                #     obs.call(requests.SetCurrentScene("Interview - me (zoom)"))
                #     continue
                # elif event.code == ecodes.KEY_ESC:
                #     obs.call(requests.SetCurrentScene("Interview - me"))
                #     continue
                # elif event.code == ecodes.KEY_DOT:
                #     scene = obs.call(requests.GetCurrentScene())
                #     if scene.getName() == "Interview - me (firefox)":
                #         obs.call(requests.SetCurrentScene("Interview - me"))
                #     else:
                #         print(f"scene: {scene.getName()}")
                #         obs.call(requests.SetCurrentScene("Interview - me (firefox)"))
                #     continue
                else:
                    print(f"Unknown key: {event.code}")
                    continue

                # section = sections[current_section_idx]
                # new_section(obs, "", "")
                # obs.call(requests.SetCurrentScene("Interview - me (title)"))
                # new_section(obs, section["title"], section["byline"])


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass


