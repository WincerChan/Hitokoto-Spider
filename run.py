import asyncio

from spider.config import FrozenConfig
from spider.download import Download

if __name__ == '__main__':
    urls = FrozenConfig().urls
    try:
        if urls and urls[0]:
            asyncio.run(Download())
        else:
            print("请在配置文件中填入网址。")
    except KeyboardInterrupt:
        print("Good Bye!\033[?25h")
    finally:
        print("\33[?25h", end="")
