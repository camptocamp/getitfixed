DOCKER_PORT=8487
DOCKER_TAG=demo
PROXY_PREFIX=/getitfixed

include Makefile

docker-compose-env: ## Build docker-compose environment file
	rm -f .env
	touch .env
	sleep 0.1
	touch .env.mako
	$(DOCKER_MAKE_CMD) .env
