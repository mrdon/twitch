import logging
from functools import wraps
from string import digits

from quart import current_app
from twitchio import Context
from twitchio.ext import commands

from director.obs import DevMattersShow

log = logging.getLogger(__name__)


def require_mod(func):
    @wraps(func)
    async def inner(self, ctx: Context, *args, **kwargs):
        if not ctx.author.is_mod:
            await ctx.send(f'Not a mod!')
            return
        return await func(self, ctx, *args, **kwargs)

    return inner


class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def event_ready(self):
        print("ready")
        log.info(f"Ready | {self.nick}")

    # Commands use a different decorator
    @commands.command(name='quote')
    @require_mod
    async def my_command(self, ctx: Context):
        arg_line = ctx.content[(len(ctx.prefix) + len(ctx.command.name)):].strip()
        message = sized_truncate(arg_line, 19)
        if message:
            current_app.obs.set_section(byline=f'"{message}"')
        # await ctx.send(f'{ctx.author.is_mod} - {arg_line}!')


def sized_truncate(content, length, suffix='...'):
    words = content.split(" ")
    result = ""
    for word in words:
        old_result = result
        if result:
            result += f" {word}"
        else:
            result = word

        new_length = get_approximate_arial_string_width(result)
        if new_length > length:
            return old_result + f" {suffix}"

    return result


def get_approximate_arial_string_width(st):
    size = 0  # in milinches
    for s in st:
        if s in 'lij|\' ':
            size += 37
        elif s in '![]fI.,:;/\\t':
            size += 50
        elif s in '`-(){}r"':
            size += 60
        elif s in '*^zcsJkvxy':
            size += 85
        elif s in 'aebdhnopqug#$L+<>=?_~FZT' + digits:
            size += 95
        elif s in 'BSPEAKVXY&UwNRCHD':
            size += 112
        elif s in 'QGOMm%W@':
            size += 135
        else:
            size += 50
    return size * 6 / 1000.0  # Convert to picas
