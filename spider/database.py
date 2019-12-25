import os
import reprlib
from re import sub
from typing import Any, Dict, Optional, Tuple

from pony.orm import (Database, Json, PrimaryKey, Required,
                      TransactionIntegrityError, commit, core, db_session,
                      dbapiprovider)
from xxhash import xxh64
from yaml import SafeLoader
from yaml import load as yaml_load

with open('./config.yml') as fp:
    config = yaml_load(fp, Loader=SafeLoader)

db = Database()
Entity: core.EntityMeta = db.Entity

db.bind(provider='postgres', host='127.0.0.1',
        user=config['postgres']['user'],
        passwd=config['postgres']['password'], database='api')

reprlib.aRepr.maxstring = 55

PGINT64 = 2 ** 63 - 1


class Helper:
    amount = 0


class Hitokoto(Entity):
    """
    ORM 中的表结构，这里的变量名即存放进数据库的列名
    不能为这个 class 重写 str 或 repr 方法
    因为 pony 存放的时候会调用这个方法
    """
    id = PrimaryKey(int, size=64)
    length = Required(int)
    info = Required(Json)
    origin = Required(str)


# 初始化数据库，如果表不存在就建表，存在就拿到数据条数
db.generate_mapping(create_tables=True)
with db_session:
    Helper.amount = Hitokoto.select(lambda p: p.id).count()


def fmt_data(c: Dict[str, str], url: str) -> None:
    hitokoto_tmp = c.get('hitokoto', '') or c.get(
        'text', '') or c.get('HITO', '')
    source = c.get('source') or c.get('from') or c.get('SOURCE')
    hitokoto = sub(r'[\xa0-\xad]', '', hitokoto_tmp)
    origin = url.split('.')[1]
    # 去除一些无用字符，避免无用字符对计算 hash 产生的影响
    fmt_hitokoto = sub(
        r'[,，。.“” …！、\!\?：’；\\‘？「/」—-♬《》⋯『』（）]', '', hitokoto)
    id_ = xxh64(fmt_hitokoto).intdigest() - PGINT64
    source and origin and insert_data(id_, hitokoto, source, origin)


@db_session
def insert_data(*record: Tuple[int, str, str, str]) -> None:
    # 这里用事务包起来，方便错出后回退
    try:
        Hitokoto(id=record[0], info=dict(hitokoto=record[1], source=record[2]),
                 length=len(record[1]), origin=record[3])
        commit()
    except TransactionIntegrityError:
        has_duplicated = f'已重复（{Helper.amount}）：{record[0], record[1]}'
        print(reprlib.repr(has_duplicated))
    except Exception as e:
        print(e)
    else:
        has_inserted = f'已插入（{Helper.amount}）：{record[0], record[1]}'
        Helper.amount += 1
        print(reprlib.repr(has_inserted))
