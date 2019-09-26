DOCKER_PORT=8487
DOCKER_TAG=demo
PROXY_PREFIX=/getitfixed

include Makefile

# Recreate .env with current user to allow docker to overwrite it.
docker-compose-env: ## Build docker-compose environment file
	rm -f .env
	touch .env
	sleep 0.1
	touch .env.mako
	$(DOCKER_MAKE_CMD) .env

# Pull images instead of building them, as we cannot build docker image on demo
# server due to installed docker version
.PHONY: docker-build-build
docker-build-build:
	docker pull ${DOCKER_BASE}-build:${DOCKER_TAG}
.PHONY: docker-build-getitfixed
docker-build-getitfixed:
	docker pull ${DOCKER_BASE}-getitfixed:${DOCKER_TAG}
