import asyncio
import json
import logging
import os

import aiohttp
from aiohttp import ClientWebSocketResponse, WSMsgType, ClientConnectionError
from dotenv import load_dotenv

from director import logo
from director.logo import Preset, Color

load_dotenv()


log = logging.getLogger(__name__)


class TauClient:
    def __init__(self):
        self.tau_token = os.getenv("TAU_TOKEN")
        self.tau_url = os.getenv("TAU_URL")
        self._running = False

    async def connect(self):
        session = aiohttp.ClientSession()
        while True:
            try:
                ws = await session.ws_connect(
                    f'{self.tau_url}/ws/twitch-events/')
                break
            except ClientConnectionError as e:
                print(f"Waiting for tau to start... : {e}")
                await asyncio.sleep(5)

        print("sending token")
        await ws.send_str(json.dumps(dict(token=self.tau_token)))
        print("token sent")
        asyncio.create_task(self._loop(ws))

    async def disconnect(self):
        log.info("Disconnecting from Tau")
        self._running = False

    async def _loop(self, ws: ClientWebSocketResponse):
        self._running = True
        while self._running:
            msg = await ws.receive()
            if not msg:
                continue

            log.info(f"got msg: {msg.type}")
            if msg.type == WSMsgType.TEXT:
                data = msg.json()
                event_type = data["event_type"]
                log.info(f"Got event: {event_type}")
                if event_type == "channel-channel_points_custom_reward_redemption-add":
                    redemption_id = data["event_data"]["reward"]["id"]
                    if redemption_id == "6393c69c-8b3f-4364-ae45-065383e04a44":
                        color_str = data["event_data"]["user_input"].strip().casefold()
                        try:
                            color = Color[color_str]
                            print(f'Turning {color_str}')
                            await logo.set_outer_color(color)
                        except ValueError:
                            print(f"Invalid color: {color_str}")
                    else:
                        log.warning(f"Unknown redemption: {redemption_id}")
                elif event_type == "channel-follow":
                    await logo.flash(Preset.FOLLOW)
                elif event_type == "channel-subscribe":
                    plan = data["event_data"]["data"]["message"]["sub_plan"]
                    if plan == "3000":
                        length = 30
                    elif plan == "2000":
                        length = 20
                    elif plan in ("1000", "prime"):
                        length = 10
                    else:
                        log.error(f"Unknown sub type: {plan}")
                        length = 5

                    await logo.flash(Preset.SUBSCRIBE, length=length)
                elif event_type == "channel-raid":
                    await logo.flash(Preset.RAID)
                elif event_type == "channel-cheer":
                    bits = int(data["event_data"]["bits"])
                    seconds = int(bits/100) * 5
                    await logo.flash(Preset.CHEER, length=seconds)

                print(f"Got text: {msg.json()}")
                pass
            elif msg.type == WSMsgType.closed:
                log.info("Closing TAU connection")
                if self._running:
                    log.info("Should be running so let's reconnect")
                    await self.connect()
                break
            elif msg.type == WSMsgType.error:
                log.info("Error with TAU connection")
                break
