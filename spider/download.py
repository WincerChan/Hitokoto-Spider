import asyncio
from typing import List

from requests.exceptions import ReadTimeout, ConnectTimeout
from requests_html import AsyncHTMLSession, TimeoutError, HTMLResponse

from spider.database import DataFactory
from spider.config import FrozenConfig
from spider.progress import Progress


class Download:
    _config = FrozenConfig()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.urls = cls._config.urls
        return cls._instance.__call__()

    async def _do_down(self, url: str) -> None:
        while True:
            try:
                resp: HTMLResponse = await self.session.get(url, timeout=1.3)
                conn = resp.json()
                DataFactory.fmt_data(conn, url)
            except (TimeoutError, ReadTimeout, ConnectTimeout):
                import traceback
                traceback.print_exc()
                print("连接已超时，尝试新建另一连接。")

    async def __call__(self):
        self.session = AsyncHTMLSession(
            loop=asyncio.get_event_loop(),
            workers=self._config.alive_connection
        )
        todo = [self._do_down(url) for url in self.urls]
        await asyncio.gather(*todo, Progress.show())
