PROJECT_NAME=outline-vpn-bot
IMAGE_NAME=outline-vpn-bot:latest
TAG=$(value TAG)
TELEGRAM_API_TOKEN=$(value TELEGRAM_API_TOKEN)
OUTLINE_API_URL=$(value OUTLINE_API_URL)
AUTHORIZED_IDS=$(value AUTHORIZED_IDS)
DOCKER_REPO=$(value DOCKER_REPO)

.PHONY: build
build:
	docker build -t $(IMAGE_NAME) -f ./Dockerfile .

.PHONY: push
push:
	docker image tag $(IMAGE_NAME) $(DOCKER_REPO)/$(PROJECT_NAME):$(TAG)
	docker image tag $(IMAGE_NAME) $(DOCKER_REPO)/$(PROJECT_NAME):latest
	docker image push --all-tags $(DOCKER_REPO)/$(PROJECT_NAME)

.PHONY: run
run:
	docker run -d --rm --name $(PROJECT_NAME) -e TELEGRAM_API_TOKEN=$(TELEGRAM_API_TOKEN) -e OUTLINE_API_URL=$(OUTLINE_API_URL) -e AUTHORIZED_IDS=$(AUTHORIZED_IDS) $(IMAGE_NAME)

.PHONY: stop
stop:
	docker stop $(PROJECT_NAME) && docker rm $(PROJECT_NAME)
