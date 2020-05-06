import asyncio
from typing import List, Dict

from spider.download import main as download
from spider.database import config

if __name__ == '__main__':
    urls: List[Dict[str, int]] = config.get('urls')
    try:
        if urls:
            asyncio.run(download(urls))
        else:
            print("请在配置文件中填入网址。")
    except KeyboardInterrupt:
        print("Good Bye!\033[?25h")
