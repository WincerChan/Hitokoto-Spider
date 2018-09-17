import os
import reprlib
from re import sub

from pony.orm import (Database, PrimaryKey, Required,
                      TransactionIntegrityError, commit, db_session)
from xxhash import xxh64
from yaml import load as yaml_load

with open('./config.yml') as fp:
    config = yaml_load(fp)

db = Database()
db.bind(provider='mysql', host='127.0.0.1',
        user=config['mysql']['user'],
        passwd=config['mysql']['password'], db='hitokoto')
reprlib.aRepr.maxstring = 55


class Main(db.Entity):
    """
    ORM 中的表结构，这里的变量名即存放进数据库的列名
    不能为这个 class 重写 str 或 repr 方法
    因为 pony 存放的时候会调用这个方法
    """
    id = PrimaryKey(int, size=64, unsigned=True)
    hitokoto = Required(str)
    source = Required(str)
    origin = Required(str)


with db_session:
    db.generate_mapping()
    Helper = type('Helper', (object,), {
                  'amount': Main.select(lambda p: p.id).count()})


def fmt_data(c: dict, url: str)-> None:
    hitokoto_tmp = c.get('hitokoto') or c.get('text') or c.get('HITO')
    source = c.get('source') or c.get('from') or c.get('SOURCE')
    hitokoto = sub(r'[\xa0-\xad]', '', hitokoto_tmp)
    origin = url.split('.')[1]
    # 去除一些无用字符
    fmt_hitokoto = sub(r'[,，。.“” …！、\!\?：’；\\‘？「/」—-♬《》⋯『』（）]', '', hitokoto)
    id_ = xxh64(fmt_hitokoto).intdigest()
    if (source and origin):
        insert_data(id_, hitokoto, source, origin)


@db_session
def insert_data(*record):
    # 这里用事务包起来，方便错出后回退
    try:
        Main(id=record[0], hitokoto=record[1],
             source=record[2], origin=record[3])
        commit()
    except TransactionIntegrityError:
        fmt = '已重复（{}）：{}'
        print(reprlib.repr(fmt.format(Helper.amount, (record[0], record[1]))))
    except Exception as e:
        print(e)
    else:
        fmt = '已插入（{}）：{}'
        Helper.amount += 1
        print(reprlib.repr(fmt.format(Helper.amount, (record[0], record[1]))))
