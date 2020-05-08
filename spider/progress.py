import asyncio
import itertools
import time
from sys import stdout as o


class Progress:
    _STYLE_START = '\033[33;36m'
    _STYLE_END = '\033[?25l'
    _START_TIME = int(time.time())

    @classmethod
    async def show(cls):
        for char in itertools.cycle('⠼⠴⠦⠧⠇⠏⠋⠙⠹⠸'):
            await cls._display_char(char)

    @classmethod
    async def _display_char(cls, char: str):
        fmt_status = f'{cls._STYLE_START}{char} {cls._STYLE_END}'
        elapsed = int(time.time()) - cls._START_TIME
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        elapsed = f'Elapsed: {h:02}:{m:02}:{s:02}'
        o.write(fmt_status + elapsed), o.flush()
        o.write('\x08' * (len(elapsed) + 2))
        await asyncio.sleep(.15)


if __name__ == '__main__':
    try:
        asyncio.run(Progress.show())
    except KeyboardInterrupt:
        print("Good Bye!")
    finally:
        print("\33[?25h", end="")
