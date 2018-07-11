import os
import reprlib
from re import sub
from sqlite3 import IntegrityError
from sqlite3 import connect as sql_conn

from xxhash import xxh64

from progress import flush, write

cursor = sql_conn('../tmp.db')
COUNTER = cursor.execute("SELECT COUNT(1) FROM MAIN;").fetchone()[0]

TYPE = {
}


def clear():
    print()
    if COUNTER % 100 == 0:
        os.system("clear")


def fmt_data(c, url):
    hitokoto = c.get('hitokoto') or c.get('text') or c.get('HITO')
    source = c.get('source') or c.get('from') or c.get('SOURCE')
    origin = TYPE.get(url, 'cn')
    fmt_hitokoto = sub(r'[,，。.“” …！、\!\?：’；‘？「」—-♬《》⋯『』（）]', '', hitokoto)
    id = xxh64(fmt_hitokoto).intdigest() - 9223372036854775808
    if (source and origin):
        insert_data(id, hitokoto, source, origin)


def insert_data(*data):
    global COUNTER
    try:
        cursor.execute("INSERT INTO MAIN VALUES {};".format(data))
        COUNTER += 1
    except IntegrityError:
        print('已重复（%d）：%s' % (COUNTER, reprlib.repr(data[1])), end="")
        cursor.commit()
    else:
        cursor.commit()
        print('已插入（%d）：%s' % (COUNTER, reprlib.repr(data[1])), end="")
    clear()
