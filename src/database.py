import os
import reprlib
from re import sub
from sqlalchemy import create_engine
from sqlalchemy import exc

from xxhash import xxh64
import yaml

from progress import flush, write


with open('../config.yml') as fp:
    config = yaml.load(fp)

engine = create_engine(
    'mysql+pymysql://{}:{}@127.0.0.1:{}/hitokoto?charset=utf8'.format(
        config['mysql']['user'],
        config['mysql']['password'],
        config['mysql']['port']))


COUNTER = engine.execute("SELECT COUNT(id) FROM main;").fetchone()[0]


def get_name(url):
    return url.split('.')[1]


def clear():
    print()
    if COUNTER % 100 == 0:
        os.system("clear")


def fmt_data(c, url):
    hitokoto_tmp = c.get('hitokoto') or c.get('text') or c.get('HITO')
    source = c.get('source') or c.get('from') or c.get('SOURCE')
    hitokoto = sub(r'[\xa0-\xad]', '', hitokoto_tmp)
    origin = get_name(url)
    fmt_hitokoto = sub(r'[,，。.“” …！、\!\?：’；\\‘？「/」—-♬《》⋯『』（）]', '', hitokoto)
    id = xxh64(fmt_hitokoto).intdigest()
    if (source and origin):
        insert_data(id, hitokoto, source, origin)


def insert_data(*data):
    global COUNTER
    try:
        engine.execute("INSERT INTO main VALUES {};".format(data))
        COUNTER += 1
    except exc.IntegrityError:
        print('已重复（%d）：%s' %
              (COUNTER, reprlib.repr(str(data[0])+'，'+data[1])), end="")
    else:
        print('已插入（%d）：%s' %
              (COUNTER, reprlib.repr(str(data[0])+'，'+data[1])), end="")
    clear()
