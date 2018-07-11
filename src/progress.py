import time
import itertools
import sys
import asyncio


write, flush = sys.stdout.write, sys.stdout.flush
STYLE_START, STYLE_END = '\033[33;36m', '\033[?25l'
START = int(time.time())


async def display_progress(char):
    status = char + ' '
    fmt_status = '%s%s%s' % (STYLE_START, status, STYLE_END)
    elapsed = int(time.time()) - START
    m, s = divmod(elapsed, 60)
    h, m = divmod(m, 60)
    elapsed = "Elapsed: %02d:%02d:%02d" % (h, m, s)
    print(fmt_status + elapsed, end=""), flush()
    write('\x08' * len(elapsed + status))
    await asyncio.sleep(.15)


async def main():
    for char in itertools.cycle('⠼⠴⠦⠧⠇⠏⠋⠙⠹⠸'):
        await display_progress(char)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
