import asyncio
import string

import aiohttp

from database import fmt_data
from progress import main as progress_main

MAX_CONNECTION = 4


async def down(url):
    timeout = aiohttp.ClientTimeout(total=0.5)
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=MAX_CONNECTION)) as session:
        while True:
            try:
                resp = await session.get(url, timeout=timeout,
                                         proxy='http://124.193.37.5:8888')
                cont = await resp.text()
                await asyncio.sleep(.5)
                fmt_data(eval(cont), url)
            except (asyncio.TimeoutError, aiohttp.ClientError):
                print('The connect is timeout, try a new connect.')
                continue


def main(urls):
    loop = asyncio.get_event_loop()
    to_do = [down(url) for url in urls]
    to_do.append(progress_main())
    wait_coro = asyncio.wait(to_do)
    res, _ = loop.run_until_complete(wait_coro)
    loop.close()
    return len(res)


if __name__ == '__main__':
    urls = [

    ]
    try:
        if urls:
            main(urls)
        else:
            print("请填入网址。")
    except KeyboardInterrupt:
        print("Good Bye!\033[?25l")
