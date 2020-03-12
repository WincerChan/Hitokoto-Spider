import asyncio
import json

import aiohttp

from spider.database import fmt_data, config
from spider.progress import main as progress_main
from requests_html import AsyncHTMLSession, TimeoutError, HTMLResponse

MAX_CONNECTION = config.get('alive_connection')
ASS = AsyncHTMLSession(loop=asyncio.get_event_loop(), workers=MAX_CONNECTION)


async def down(url: str):
    timeout = aiohttp.ClientTimeout(connect=0.3)
    while True:
        try:
            resp: HTMLResponse = await ASS.get(url, timeout=timeout)
            conn = resp.json()
            fmt_data(conn, url)
        except TimeoutError:
            print("连接已超时，尝试新建另一连接。")


async def main():
    urls = config.get('urls')
    to_do = list()
    for item in urls:
        to_do.extend(
            [down(item.get('url'))
             for _ in range(item.get('connection', 1))]
        )
    # 这里需要把进度条也加入事件循环
    await asyncio.gather(*to_do, progress_main())
