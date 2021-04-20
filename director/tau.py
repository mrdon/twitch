import json
import aiohttp
import os
import asyncio

from dotenv import load_dotenv

load_dotenv()

async def main():
    print(f" token: {os.getenv('TAU_TOKEN')[0:3]}")
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(
        'http://localhost:8085/ws/twitch-events/')
    
    print("sending token")
    await ws.send_str(json.dumps(dict(token=os.getenv("TAU_TOKEN"))))
    print("token sent")
    while True:
        msg = await ws.receive()
        print("got msg")
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
               await ws.close()
               break
            else:
               ws.send_str(msg.data + '/answer')
        elif msg.tp == aiohttp.MsgType.closed:
            break
        elif msg.tp == aiohttp.MsgType.error:
            break

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
