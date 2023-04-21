# Create docker image
```shell
make build
make push TAG=0.0.1
```

# Run container
```shell
make run TELEGRAM_API_TOKEN='' OUTLINE_API_URL='' AUTHORIZED_IDS=''
```

# Stop container
```shell
make stop
```