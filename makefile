PROJECT_NAME=outline-vpn-bot
IMAGE_NAME=outline-vpn-bot:latest
TAG=$(value TAG)
TELEGRAM_API_TOKEN=$(value TELEGRAM_API_TOKEN)
OUTLINE_API_URL=$(value OUTLINE_API_URL)
AUTHORIZED_IDS=$(value AUTHORIZED_IDS)

.PHONY: build
build:
	docker build -t $(IMAGE_NAME) -f ./Dockerfile .

.PHONY: push
push:
	docker image tag $(IMAGE_NAME) ksastan/$(PROJECT_NAME):$(TAG)
	docker image tag $(IMAGE_NAME) ksastan/$(PROJECT_NAME):latest
	docker image push --all-tags ksastan/$(PROJECT_NAME)

.PHONY: run
run:
	docker run -d --name $(PROJECT_NAME) -e TELEGRAM_API_TOKEN=$(TELEGRAM_API_TOKEN) -e OUTLINE_API_URL=$(OUTLINE_API_URL) -e AUTHORIZED_IDS=$(AUTHORIZED_IDS) $(IMAGE_NAME)

.PHONY: stop
stop:
	docker stop $(PROJECT_NAME) && docker rm $(PROJECT_NAME)
