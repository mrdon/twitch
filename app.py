from quart import Quart, websocket, render_template
import asyncio

app = Quart(__name__)

@app.route('/')
async def hello():
    return await render_template('index.html', name="Makoa!!!")

@app.websocket('/ws')
async def ws():
    x = 0
    while True:
        x += 1
        asyncio.sleep(10)
        await websocket.send(f'hello {x}')

app.run(debug=True, use_reloader=True)
