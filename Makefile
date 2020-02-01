DOKCER_IMAGE_NAME := docker.pkg.github.com/quantumghost/ncov-channel-crawler/crawler
DOCKER_IMAGE_TAG := latest
DOCKER_STABLE_TAG := stable

.PHONY: build-image

build-image:
	docker build -f build/Dockerfile -t $(DOKCER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) .

release:
	docker tag $(DOKCER_IMAGE_NAME):latest $(DOKCER_IMAGE_NAME):$(DOCKER_STABLE_TAG)
