import reprlib
from re import sub
from typing import Dict

from pony.orm import (Database, Json, PrimaryKey, Required,
                      TransactionIntegrityError, commit, db_session)
from xxhash import xxh64

from spider.config import FrozenConfig

reprlib.aRepr.maxstring = 55


class DataFactory:
    _INT64 = 2 ** 63 - 1
    _config = FrozenConfig()
    _db = Database()
    _db.bind(provider='postgres', host=_config.postgres.host,
             port=_config.postgres.port,
             user=_config.postgres.user,
             passwd=_config.postgres.password,
             database='api')
    print("1fdjkfafa")

    class Hitokoto(_db.Entity):
        """
        ORM 中的表结构，这里的变量名即存放进数据库的列名
        不能为这个 class 重写 str 或 repr 方法
        因为 pony 存放的时候会调用这个方法
        """
        id = PrimaryKey(int, size=64)
        length = Required(int)
        info = Required(Json)
        origin = Required(str)

    _db.generate_mapping(create_tables=True)
    with db_session:
        _amount = Hitokoto.select(lambda p: p.id).count()

    @classmethod
    @db_session
    def _insert(cls, id_: int, hitokoto: str, source: str, origin: str):
        try:
            cls.Hitokoto(id=id_, info=dict(hitokoto=hitokoto, source=source),
                         length=len(hitokoto), origin=origin)
            commit()
        except TransactionIntegrityError:
            has_duplicated = f'已重复（{cls._amount}）：{id_, hitokoto}'
            print(reprlib.repr(has_duplicated))
        except Exception as e:
            import traceback
            traceback.print_exc()
        else:
            has_inserted = f'已插入（{cls._amount}）：{id_, hitokoto}'
            cls._amount += 1
            print(reprlib.repr(has_inserted))

    @classmethod
    def fmt_data(cls, c: Dict[str, str], url: str) -> None:
        hitokoto_tmp = c.get('hitokoto') or c.get('text') or c.get('HITO')
        source = c.get('source') or c.get('from') or c.get('SOURCE')
        hitokoto = sub(r'[\xa0-\xad]', '', hitokoto_tmp)
        origin = url.split('.')[1]
        # 去除一些无用字符，避免无用字符对计算 hash 产生的影响
        fmt_hitokoto = sub(
            r'[,，。.“” …！、!?：’；\\‘？「/」—-♬《》⋯『』（）]', '', hitokoto)
        id_ = xxh64(fmt_hitokoto).intdigest() - cls._INT64
        source and origin and cls._insert(id_, hitokoto, source, origin)
