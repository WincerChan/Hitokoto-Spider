# Hitokoto-Spider

## 简介

采取 asyncio + aiohttp 异步爬取。

## 用法

新建 `config.yml` 文件，内容参考 `config_sample.yml` 填写，在 `urls` 一栏填入需爬取的网址，其中 `url` 的数量即为同时发起的连接数，如果是同一个 `url` 的话请填写多次。

**请一定控制好数量，避免对服务器发起 DOS 攻击。**

`pool_connection` 为连接池的总连接数，当这些连接数都 `timeout` 之后，程序可能会陷入`假死`状态：有两种解决方法：

1. 重新运行程序；
2. 将 `pool_connection` 设置为 0。