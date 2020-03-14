import asyncio
from typing import List, Dict

from spider.database import fmt_data, config
from spider.progress import main as progress_main
from requests.exceptions import ReadTimeout, ConnectTimeout
from requests_html import AsyncHTMLSession, TimeoutError, HTMLResponse

MAX_CONNECTION = config.get('alive_connection')
ASS = AsyncHTMLSession()


async def down(url: str):
    while True:
        try:
            resp: HTMLResponse = await ASS.get(url, timeout=0.3)
            conn = resp.json()
            fmt_data(conn, url)
        except (TimeoutError, ReadTimeout, ConnectTimeout):
            print("连接已超时，尝试新建另一连接。")


async def main(urls: List[Dict[str, int]]):
    # 这里必须重新使用 loop 初始化 ASS
    global ASS
    ASS = AsyncHTMLSession(loop=asyncio.get_event_loop(), workers=MAX_CONNECTION)
    to_do = list()
    for item in urls:
        to_do.extend(
            [down(item.get('url'))
             for _ in range(item.get('connection', 1))]
        )
    # 这里需要把进度条也加入事件循环
    await asyncio.gather(*to_do, progress_main())
