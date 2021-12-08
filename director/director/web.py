# noinspection PyUnresolvedReferences
import asyncio
import json
import logging
import os
import random
from typing import List
from typing import Optional

from bs4 import BeautifulSoup, PageElement
from quart import make_response
from quart import Quart, current_app
from quart import redirect
from quart import render_template
from quart import request
from quart import url_for

from director import obs, clicker
from director.clicker import new_section, get_section_title
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

    print(f"joining: {os.environ['TWITCH_CHANNEL']}")
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
    current_app.bot = bot

    # show = DevMattersShow()
    # show.start()
    current_app.obs = obs.Connection()
    asyncio.create_task(clicker.run())
    print("started")
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


@app.route("/", methods=["GET"])
async def get_slide_index():
    slug = request.args.get("slug")
    if slug:
        app.slide_slug = slug

    dir = os.path.join(os.path.dirname(__file__), "templates/slides")
    return await render_template(
        f"slides_index.html",
        slugs=[t[:-5] for t in os.listdir(dir)],
        slide_slug=getattr(app, "slide_slug")
    )


@app.route("/slides", methods=["GET"])
async def get_slides():
    slug = getattr(app, "slide_slug", None)
    if not slug:
        slug = get_next_event().slug

    return await render_template(
        f"slides/{slug}.html"
    )


@app.route("/slide", methods=["POST"])
async def post_current_slide():
    event = get_next_event()
    form = await request.form
    if not form.get("html"):
        print("No html?")
        return "", 204

    html = BeautifulSoup(form.get("html"), 'html.parser')
    title: PageElement = html.find("h2") or html.find("h3")
    current_section_title = get_section_title(current_app.obs)
    if title and event:
        for section in event.sections:
            if section.title == title.text and current_section_title != section.title:
                await new_section(current_app.obs, section.title, section.byline)
                links = html.find_all("a")
                link: PageElement
                for link in links:
                    await current_app.bot.send(f"{link.text} - {link['href']}")

    return "ok", 204


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
