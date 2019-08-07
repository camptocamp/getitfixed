
# Customisable environment variables

DEVELOPMENT = TRUE
export DEVELOPMENT

DOCKER_BASE ?= camptocamp/getitfixed
DOCKER_TAG ?= latest
DOCKER_PORT ?= 8080
export DOCKER_BASE
export DOCKER_TAG
export DOCKER_PORT

PGHOST ?= postgresql
PGHOST_SLAVE ?= postgresql
PGPORT ?= 5432
PGDATABASE ?= getitfixed
PGUSER ?= getitfixed
PGPASSWORD ?= getitfixed
export PGHOST
export PGHOST_SLAVE
export PGPORT
export PGDATABASE
export PGUSER
export PGPASSWORD

VISIBLE_WEB_PROTOCOL ?= http
VISIBLE_WEB_HOST ?= localhost
VISIBLE_ENTRY_POINT ?= /
export VISIBLE_WEB_PROTOCOL
export VISIBLE_WEB_HOST
export VISIBLE_ENTRY_POINT

SMTP_USER ?= truite
SMTP_PASSWORD ?= brochet
export SMTP_USER
export SMTP_PASSWORD

# End of customisable environment variables

MO_FILES = $(addprefix getitfixed/locale/, fr/LC_MESSAGES/getitfixed.mo de/LC_MESSAGES/getitfixed.mo)

COMMON_DOCKER_RUN_OPTIONS ?= \
	--name="getitfixed-build" \
	--volume="${PWD}:/src" \
	--user=$(shell id -u) \
	${DOCKER_BASE}-build:${DOCKER_TAG}

DOCKER_MAKE_CMD = docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} make -f $(firstword $(MAKEFILE_LIST))

default: help

.PHONY: help
help: ## Display this help message
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@grep -Eh '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "    %-20s%s\n", $$1, $$2}'

.PHONY: meacoffe
meacoffe: ## Build, run and show logs
meacoffe: build initdb
	docker-compose up -d && docker-compose logs -f getitfixed

.PHONY: build
build: ## Build runtime files and docker images
build: \
		docker-build-postgresql \
		docker-build-getitfixed \
		docker-compose-env

.PHONY: docker-compose-env
docker-compose-env: ## Build docker-compose environment file
	$(DOCKER_MAKE_CMD) .env

.PHONY: initdb
initdb:
	docker-compose run --rm getitfixed initialize_getitfixed_db c2c://development.ini

.PHONY: check
check: ## Check the code with flake8
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} flake8 getitfixed

.PHONY: bash
bash: ## Open bash in build container
bash: docker-build-build
	docker run --rm -ti ${COMMON_DOCKER_RUN_OPTIONS} bash

.PHONY: test
test:
	docker-compose run --rm ${COMMON_DOCKER_RUN_OPTIONS} getitfixed pytest

.PHONY: clean
clean: ## Clean generated files
clean:
	rm -f $(MO_FILES)

.PHONY: cleanall
cleanall: ## Clean everything including docker containers and images
cleanall: clean
	docker-compose down
	docker rmi \
		${DOCKER_BASE}-postgresql:${DOCKER_TAG} \
		${DOCKER_BASE}-build:${DOCKER_TAG} \
		${DOCKER_BASE}-getitfixed:${DOCKER_TAG} || true

# Docker images

.PHONY: docker-build-postgresql
docker-build-postgresql:
	docker build -t ${DOCKER_BASE}-postgresql:${DOCKER_TAG} postgresql

.PHONY: docker-build-build
docker-build-build:
	docker build -t ${DOCKER_BASE}-build:${DOCKER_TAG} build

.PHONY: docker-build-getitfixed
docker-build-getitfixed: docker-build-build
	$(DOCKER_MAKE_CMD) compile-catalog
	docker build --build-arg GIT_HASH=${GIT_HASH} -t ${DOCKER_BASE}-getitfixed:${DOCKER_TAG} .

# Targets used inside docker build container

.PHONY: update-catalog
update-catalog:
	pot-create -c lingua.cfg --keyword _ -o getitfixed/locale/getitfixed.pot \
		getitfixed/models/ \
		getitfixed/views/ \
		getitfixed/templates/
	msgmerge --update getitfixed/locale/fr/LC_MESSAGES/getitfixed.po getitfixed/locale/getitfixed.pot
	msgmerge --update getitfixed/locale/de/LC_MESSAGES/getitfixed.po getitfixed/locale/getitfixed.pot

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

# .env depends on user makefile
.env: $(MAKEFILE_LIST)

# Rules

%.mo: %.po
	msgfmt $< --output-file=$@

%: %.mako
	c2c-template \
		--runtime-environment-pattern '$${{{}}}' \
		--vars vars.yaml \
		--engine mako \
		--files $<
