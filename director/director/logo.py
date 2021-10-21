import asyncio
from enum import Enum
from typing import Optional

from wled import WLED

LIGHT_IP = "wled-Sleuth.localdomain"


class Preset(Enum):
    DEFAULT = (6, 5)
    FIVE_COLORS = (2, 5)
    RANDOM = (3, 5)
    FOLLOW = (7, 5)
    SUBSCRIBE = (8, 10)
    RAID = (9, 20)
    FLASH = (3, 1)
    CHEER = (10, 5)

    def __init__(self, index: int, seconds: int):
        self.index = index
        self.seconds = seconds


class Color(Enum):
    blue = (0, 0, 255)
    red = (255, 0, 0)
    purple = (110, 0, 110)
    yellow = (255, 200, 0)
    green = (166, 255, 150)
    spacegray = (79, 91, 102)

    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue


async def flash(preset: Preset, length: Optional[int] = 0):
    async with WLED(LIGHT_IP) as led:
        await led.preset(preset.index)
        if length:
            await asyncio.sleep(length)
        else:
            await asyncio.sleep(preset.seconds)
        await led.preset(Preset.DEFAULT.index)


async def set_outer_color(color: Color):
    async with WLED(LIGHT_IP) as led:
        print(f"Turning {color.value}")
        await led.segment(1, color_primary=color.value)
