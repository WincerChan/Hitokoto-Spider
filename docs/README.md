# Hitokoto Spider

## 简介

采取 asyncio + aiohttp 异步爬取。此项目为[一言后端 API](https://github.com/WincerChan/DIEM-API)的数据库提供数据。

依赖使用 [Pipenv](https://github.com/pypa/pipenv) 管理，所以需要先安装 Pipenv。

## 用法

新建 `config.yml` 文件，内容参考 `config_sample.yml` 填写，在 `urls` 填入一言的接口地址（地址需返回 JSON 格式数据），重复填写地址可提高爬取速度。

> ⚠️：**`alive_connection` 为连接池的总连接数，请一定控制好数量，避免对服务器发起 DOS 攻击。**
