# -*- coding: utf-8 -*-
import asyncio
from aiohttp import web


@asyncio.coroutine
def index_handler(request):
    return web.Response(body=open('index.html', 'rb').read())


@asyncio.coroutine
def init(loop, port):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index_handler)

    server = yield from loop.create_server(app.make_handler(), '0.0.0.0', port)
    print("Listen: %d..." % port)
    return server


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, 8080))
    loop.run_forever()