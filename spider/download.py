import asyncio
import string

import aiohttp
import json

from spider.database import fmt_data, config
from spider.progress import main as progress_main


MAX_CONNECTION = config.get('alive_connection')


async def down(url):
    timeout = aiohttp.ClientTimeout(connect=0.3)
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=MAX_CONNECTION)) as session:
        while True:
            try:
                resp = await session.get(url, timeout=timeout)
                cont = await resp.text()
                fmt_data(json.loads(cont), url)
            except (asyncio.TimeoutError, aiohttp.ClientError):
                print('连接已超时，尝试新建另一连接。')
                continue


async def main(urls):
    urls = config.get('urls')
    to_do = list()
    for item in urls:
        to_do.extend(
            [down(item.get('url'))
             for _ in range(item.get('connection', 1))]
        )
    # 这里需要把进度条也加入事件循环
    await asyncio.gather(*to_do, progress_main())
