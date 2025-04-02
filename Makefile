ifneq (,$(wildcard .env))
    include .env
    export
endif

IMAGE_NAME=utf8_converter

build:
	docker build -t $(IMAGE_NAME) .


run:
	docker run --rm \
		-v $(INPUT_DIR):/app/input \
		-v $(OUTPUT_DIR):/app/output \
		-e INPUT_DIR=input \
		-e OUTPUT_DIR=output \
		$(IMAGE_NAME)


clean:
	docker rmi $(IMAGE_NAME)
