#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import os
import cgi
import json
import uuid
import asyncio
from aiohttp import web

status = {'loaded': 0}


@asyncio.coroutine
def index_handler(request):
    return web.Response(body=open('index.html', 'rb').read())


@asyncio.coroutine
def upload_handler(request):
    length = int(request.headers['CONTENT-LENGTH'])
    
    buff = io.BytesIO()
    if request.content.is_eof():
        data = yield from request.content.read()
        buff.write(data)
        status['loaded'] = 100
    else:
        total = 0
        chunk_size = 100
        while not request.content.is_eof():
            data = yield from request.content.read(chunk_size)
            buff.write(data)
            total += chunk_size
            status['loaded'] = int((total * 100) / length)

    buff.seek(0)
    _, pdict = cgi.parse_header(request.headers['CONTENT-TYPE'])
    pdict['boundary'] = pdict['boundary'].encode()
    multipart = cgi.parse_multipart(buff, pdict)

    filename = uuid.uuid4().hex
    with open('static/' + filename, 'wb') as f:
        f.write(multipart['file'][0])
    
    return web.Response(body=json.dumps({
        'url': '/static/' + filename
    }).encode())


@asyncio.coroutine
def status_handler(request):
    return web.Response(body=json.dumps(status).encode())


@asyncio.coroutine
def init(loop, port):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index_handler)
    app.router.add_route('POST', '/upload', upload_handler)
    app.router.add_route('GET', '/status', status_handler)
    app.router.add_static('/static', './static/')

    server = yield from loop.create_server(app.make_handler(), '0.0.0.0', port)
    print("Listen: %d..." % port)
    return server


if __name__ == '__main__':
    if not os.path.exists('static'):
        os.mkdir('static')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, 8080))
    loop.run_forever()