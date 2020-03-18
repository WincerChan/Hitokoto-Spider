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
    def __new__(cls, urls: List[Dict[str, int]], *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.urls = urls
        return cls._instance.__call__()

    async def _do_down(self, url: str):
        while True:
            try:
                resp: HTMLResponse = await self.session.get(url, timeout=0.3)
                conn = resp.json()
                fmt_data(conn, url)
            except (TimeoutError, ReadTimeout, ConnectTimeout):
                print("连接已超时，尝试新建另一连接。")

    def _copy_urls(self, item: Dict[str, int]):
        url, connections = item.get('url'), item.get('connection', 1)
        return [self._do_down(url) for _ in range(connections)]

    async def __call__(self):
        self.session = AsyncHTMLSession(
            loop=asyncio.get_event_loop(),
            workers=config.get('alive_connection')
        )
        todo = reduce(lambda c1, c2: c1 + c2, [self._copy_urls(item) for item in self.urls])
        await asyncio.gather(*todo, progress_main())
