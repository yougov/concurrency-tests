#!/usr/bin/env python3
import asyncio
import signal
import socket

import uwsgi
from uvloop import EventLoopPolicy

from stacks.aiohttp_multi_loop import app


async def init(
        loop: asyncio.AbstractEventLoop, fd: int
) -> asyncio.AbstractServer:
    server = await loop.create_server(
        app.make_handler(),
        sock=socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
    )
    print(f'aiohttp server started on uWSGI {uwsgi.version}')
    return server


def destroy():
    print(f'Stopping worker {uwsgi.worker_id()}')
    exit()


def graceful_reload():
    print(f'Reloading worker {uwsgi.worker_id()}')
    exit()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, destroy)
    loop.add_signal_handler(signal.SIGHUP, graceful_reload)
    for fd in uwsgi.sockets:
        loop.run_until_complete(init(loop, fd))
    uwsgi.accepting()
    loop.run_forever()
