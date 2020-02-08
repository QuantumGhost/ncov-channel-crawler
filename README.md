# nCov-News-Crawler

- [配置](#%e9%85%8d%e7%bd%ae)
- [简单方式](#%e7%ae%80%e5%8d%95%e6%96%b9%e5%bc%8f)
- [复杂方式](#%e5%a4%8d%e6%9d%82%e6%96%b9%e5%bc%8f)
- [Docker 镜像构建](#docker-%e9%95%9c%e5%83%8f%e6%9e%84%e5%bb%ba)

部署此爬虫需要

- 一个 Telegram 帐号
- [Telegram developer app](https://core.telegram.org/api/obtaining_api_id)，注册完之后
  记录 api_id 和 api_hash

在本地部署还需要一个代理

## 配置

本项目使用环境变量保存配置信息，参考 [示例](./env.sample)。

- API_ID: 从 Telegram 获得的 api_id
- API_HASH：从 Telegram 获得的 api_hash
- TG_SESSION: session 文件名，会以 `$TG_SESION.sesion` 文件名写入 `$(pwd)`
- PROXY: 可选，代理设置

Telegram Session 会以文件形式保存在 `$(pwd)` （对于 Docker 镜像是 `/data`）。

## 简单方式

使用 Docker 部署，参考 [docker-compose.yaml](./docker-compose.yaml)，把配置信息写入
`crawler.env`。

如果你需要 HTTPS，请参考 [Caddyfile](./etc/Caddyfile) 进行修改并部署。

如果你不需要 HTTPS，请去掉 Compose 文件中 Caddy 相关的部分

- `docker-compose up -d`
- `docker-compose exec crawler bash`
- `python /src/login.py`
- 输入用户名和密码，然后看到正常拉取数据之后按 Ctrl-C 中断
- `docker-compose restart crawler`
- 检查日志拉取正常，即部署成功了

## 复杂方式

确保执行之前你的本地环境里已经有配置相关的环境变量（
你可以用 [forego](https://github.com/ddollar/forego) 来从 .env 文件读取）

```bash
pip install -r requirements.txt
python login.py
# 拉取成功之后按 Ctrl-C 退出
python asgi.py
```

## Docker 镜像构建

执行 `make build-image` 既可
