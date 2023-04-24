# Outline-vpn-bot
## Overview
This bot can manage OutlineVPN users through telegram
## Bot commands
- Create new VPN key: `/newkey <keyname>`
- List existed keys: `/showkeys`
- Delete key: `/delkey <keyid>`

## Run container
```shell
docker run -d -e TELEGRAM_API_TOKEN='aa123' -e OUTLINE_API_URL='https://abc:9000/acb' -e AUTHORIZED_IDS='123,324' ksastan/outline-vpn-bot:latest
```

# Developing guide
## Create docker image
```shell
make build
```

## Run container
```shell
make run TELEGRAM_API_TOKEN='' OUTLINE_API_URL='' AUTHORIZED_IDS=''
```

## Stop container
```shell
make stop
```

## Push docker image
```shell
make push TAG=0.0.1 DOCKER_REPO=''
```
