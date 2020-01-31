DOKCER_IMAGE_NAME := docker.pkg.github.com/quantumghost/ncov-channel-crawler/crawler
DOCKER_IMAGE_TAG := latest

.PHONY: build-image

build-image:
	docker build -f build/Dockerfile -t $(DOKCER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) .
