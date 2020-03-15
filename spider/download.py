import asyncio
from typing import List, Dict
from functools import reduce

from spider.database import fmt_data, config
from spider.progress import main as progress_main
from requests.exceptions import ReadTimeout, ConnectTimeout
from requests_html import AsyncHTMLSession, TimeoutError, HTMLResponse

MAX_CONNECTION = config.get('alive_connection')
ASS = AsyncHTMLSession()


class Download:
    max_connection = config.get('alive_connection')
    session = AsyncHTMLSession()
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    @classmethod
    async def _do_down(cls, url: str):
        while True:
            try:
                resp: HTMLResponse = await cls.session.get(url, timeout=0.3)
                conn = resp.json()
                fmt_data(conn, url)
            except (TimeoutError, ReadTimeout, ConnectTimeout):
                print("连接已超时，尝试新建另一连接。")

    @classmethod
    def _copy_urls(cls, item: Dict[str, int]):
        url, connections = item.get('url'), item.get('connection', 1)
        return [cls._do_down(url) for _ in range(connections)]

    @classmethod
    async def __call__(cls, urls: List[Dict[str, int]]):
        # 这里由于 cls.session 初始化是在 import 的时候就初始化了，并非在 asyncio.run 的时候
        # 因此需要在这里重新初始化 loop
        cls.session = AsyncHTMLSession(loop=asyncio.get_event_loop(), workers=cls.max_connection)
        todo = reduce(lambda c1, c2: c1 + c2, [cls._copy_urls(item) for item in urls])
        await asyncio.gather(*todo, progress_main())

# async def down(url: str):
#     while True:
#         try:
#             resp: HTMLResponse = await ASS.get(url, timeout=0.3)
#             conn = resp.json()
#             fmt_data(conn, url)
#         except (TimeoutError, ReadTimeout, ConnectTimeout):
#             print("连接已超时，尝试新建另一连接。")

#
# def copy_urls(item: Dict[str, int]):
#     url, connections = item.get('url'), item('connection', 1)
#     return [down(url) for _ in range(connections)]

#
# async def main(urls: List[Dict[str, int]]):
#     # 这里必须重新使用 loop 初始化 ASS
#     global ASS
#     ASS = AsyncHTMLSession(loop=asyncio.get_event_loop(), workers=MAX_CONNECTION)
#     todo = reduce(lambda c1, c2: c1 + c2, [copy_urls(item) for item in urls])
#     # 这里需要把进度条也加入事件循环
#     await asyncio.gather(*todo, progress_main())
