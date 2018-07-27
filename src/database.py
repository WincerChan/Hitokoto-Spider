import os
import reprlib
from re import sub

from sqlalchemy import create_engine, exc, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, exc as orm_exc
from xxhash import xxh64
from yaml import load as yaml_load

from progress import flush, write

with open('../config.yml') as fp:
    config = yaml_load(fp)

engine = create_engine(
    'mysql+pymysql://{}:{}@127.0.0.1:{}/hitokoto?charset=utf8'.format(
        config['mysql']['user'],
        config['mysql']['password'],
        config['mysql']['port']))


Base = declarative_base()

DBsession = sessionmaker(bind=engine)


class HitokotoInfo(Base):
    __tablename__ = 'main'

    id = Column(Integer, primary_key=True)
    hitokoto = Column(String(300))
    source = Column(String(64))
    origin = Column(String(12))

    def __repr__(self):
        t = tuple(vars(self).values())
        fmt = '<Hitokoto(id={}, hitokoto={}, source={}, origin={})>'
        return fmt.format(*t)

    def __str__(self):
        reprlib.aRepr.maxstring = 55
        return reprlib.repr(self.__repr__())


session = DBsession()
AMOUNT = session.query(HitokotoInfo.id).count()


def fmt_data(c, url):
    hitokoto_tmp = c.get('hitokoto') or c.get('text') or c.get('HITO')
    source = c.get('source') or c.get('from') or c.get('SOURCE')
    hitokoto = sub(r'[\xa0-\xad]', '', hitokoto_tmp)
    origin = url.split('.')[1]
    # 去除一些无用的字符
    fmt_hitokoto = sub(r'[,，。.“” …！、\!\?：’；\\‘？「/」—-♬《》⋯『』（）]', '', hitokoto)
    id_ = xxh64(fmt_hitokoto).intdigest()
    if (source and origin):
        record = HitokotoInfo(id=id_, hitokoto=hitokoto,
                              source=source, origin=origin)
        insert_data(record)


def insert_data(record):
    global AMOUNT

    def clear():
        print()
        if AMOUNT % 100 == 0:
            os.system("clear")

    try:
        session.add(record)
        session.commit()
    except orm_exc.FlushError:
        fmt = '已重复（{}）:{}'
        print(fmt.format(AMOUNT, record))
        session.rollback()
    except exc.IntegrityError:
        fmt = '已重复（{}）:{}'
        print(fmt.format(AMOUNT, record))
        session.rollback()
    except Exception as e:
        print(e)
        exit()
    else:
        fmt = '已插入（{}）：{}'
        print(fmt.format(AMOUNT, record))
    clear()
