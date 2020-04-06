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

.PHONY: docker-config
docker-config: ## Build config.yaml file
	rm -f config.yaml
	touch config.yaml
	sleep 0.1
	touch vars.yaml
	$(DOCKER_MAKE_CMD) config.yaml

.PHONY: demo
demo: ## Pull docker images, run composition and show logs
demo: docker-compose-env docker-config docker-pull
	docker-compose stop getitfixed
	docker-compose rm --force getitfixed
	docker-compose up -d
	make initdb
	docker-compose logs -f getitfixed
