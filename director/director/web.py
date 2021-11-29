# noinspection PyUnresolvedReferences
import asyncio
import json
import logging
import os
import random
from typing import List
from typing import Optional

from quart import make_response
from quart import Quart, current_app
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from director import obs
from director.schedule import get_next_event
from director.tau import TauClient

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper



app = Quart(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "not-so-secret")

app.config["QUART_AUTH_COOKIE_SECURE"] = False
app.config["env"] = "development"
app.config["QUART_DEBUG"] = True
app.config["DEBUG"] = True
app.secret_key = os.environ.get("SECRET_KEY", "not-so-secret")

logging.basicConfig()
log = logging.getLogger(__name__)


@app.before_serving
async def start_bot():
    from director.bot import Bot
    tau_client = TauClient()
    await tau_client.connect()

    bot = Bot(
        # set up the bot
        irc_token=os.environ["TWITCH_BOT_TMI"],
        client_id="", #os.environ["CLIENT_ID"],
        nick=os.environ["TWITCH_BOT_NICK"],
        prefix="$",
        initial_channels=[os.environ["TWITCH_CHANNEL"]],
    )
    print("running bot!!!")
    log.info("Starting bot")
    asyncio.create_task(bot.start())

    # show = DevMattersShow()
    # show.start()
    current_app.obs = obs.Connection()
    #
    # async def next_prev():
    #     while True:
    #         await broadcast_to_clients(random.choice(["next", "prev"]))
    #         await asyncio.sleep(2)
    #
    # asyncio.create_task(next_prev())


async def broadcast_to_clients(event: str):
    log.info(f"Broadcasting to {len(app.clients)} clients")
    for client in app.clients:
        log.info(f"Putting on client: {id(client)}")
        client.put_nowait(
            dict(event=event)
        )


class ServerSentEvent:
    def __init__(
        self,
        data: str,
        *,
        event: Optional[str] = None,
        id: Optional[int] = None,
        retry: Optional[int] = None,
    ) -> None:
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry

    def encode(self) -> bytes:
        message = f"data: {json.dumps(self.data)}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        if self.id is not None:
            message = f"{message}\nid: {self.id}"
        if self.retry is not None:
            message = f"{message}\nretry: {self.retry}"
        message = f"{message}\r\n\r\n"
        return message.encode("utf-8")


app.clients = set()


@app.route("/health", methods=["GET"])
async def health():
    return "UP", 200

@app.route("/slides", methods=["GET"])
async def get_slides():
    event = get_next_event()

    return await render_template(
        f"slides/{event.slug}.html"
    )


@app.route("/lower", methods=["GET"])
async def lower_thirds():
    name = request.args.get("name")
    if name == "me":
        line_1 = "Don Brown"
        line_2 = "Co-founder/CTO Sleuth"
    else:
        line_1 = "Dylan Etkin"
        line_2 = "Co-founder/CEO Sleuth"
    return await render_template(
        "lower.html", line_1=line_1, line_2=line_2
    )


# @app.route("/button-click")
# async def clicked():
#     show_name = request.args.get('show')
#     scene_name = request.args.get('scene')
#     section_name = request.args.get('section')
#
#     show = load_show(show_name)
#
#     if scene_name:
#         current_app.obs.set_scene(scene_name)
#
#     if section_name:
#         section = show.sections[section_name]
#         current_app.obs.set_section(title=section.title, byline=section.byline, b_roll=section.b_roll)
#
#     return redirect(url_for('get_show', show_name=show.name))


@app.route("/sse")
async def sse():
    try:
        queue = asyncio.Queue()
        app.clients.add(queue)

        async def send_events():
            while True:
                try:
                    data = await queue.get()
                    log.info(f"Sending data: {data}")
                    event = ServerSentEvent(data)
                    yield event.encode()
                except:
                    log.exception("error sending")

        response = await make_response(
            send_events(),
            {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Transfer-Encoding": "chunked",
            },
        )
        response.timeout = None
        return response
    except:
        log.exception("bad error")
        return "", 500
