.PHONY: build-image


build-image:
	docker build -f build/Dockerfile .
