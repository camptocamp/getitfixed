
# Customisable environment variables

DEVELOPMENT = TRUE
export DEVELOPMENT

DOCKER_BASE ?= camptocamp/getitfixed
DOCKER_TAG ?= latest
DOCKER_PORT ?= 8080
export DOCKER_BASE
export DOCKER_TAG
export DOCKER_PORT

PGHOST ?= db
PGHOST_SLAVE ?= db
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

PROXY_PREFIX ?=
export PROXY_PREFIX

# End of customisable environment variables

JS_LIBS_FOLDER = getitfixed/static/lib
JS_LIBS = \
	bootstrap/dist/css/bootstrap.min.css \
	bootstrap/dist/fonts/glyphicons-halflings-regular.ttf \
	bootstrap/dist/fonts/glyphicons-halflings-regular.woff2 \
	bootstrap/dist/js/bootstrap.min.js \
	bootstrap-table/dist/bootstrap-table.min.css \
	bootstrap-table/dist/bootstrap-table.min.js \
	bootstrap-table/dist/bootstrap-table-locale-all.js \
	jquery/dist/jquery.min.js \
	jquery.scrollintoview/jquery.scrollintoview.js

MO_FILES = $(addprefix getitfixed/locale/, fr/LC_MESSAGES/getitfixed.mo de/LC_MESSAGES/getitfixed.mo)

COMMON_DOCKER_RUN_OPTIONS ?= \
	--name="getitfixed-build" \
	--volume="${PWD}:/app" \
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

.PHONY: meadeca
meadeca: ## Build, run init_db and show logs
meadeca: up
	make initdb-with-data
	docker-compose logs -f getitfixed

.PHONY: meacoffee
meacoffee: ## Build, run and show logs
meacoffee: up
	make initdb
	docker-compose logs -f getitfixed

.PHONY: up
up: ## docker-compose up
up: build
	docker-compose rm --stop --force getitfixed
	docker-compose up -d

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
	docker-compose exec getitfixed initialize_getitfixed_db getitfixed://development.ini#app --with-data=1

.PHONY: initdb-with-data
initdb-with-data:
	docker-compose exec getitfixed initialize_getitfixed_db getitfixed://development.ini#app

.PHONY: reinitdb
reinitdb: ## Drop schema and regenerate it with development dataset
	docker-compose run --rm getitfixed initialize_getitfixed_db getitfixed://development.ini#app --force=1 --with-data=1

.PHONY: black
black: docker-build-build
black: ## Format Python code with black
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} black getitfixed setup.py

.PHONY: check
check: ## Check the code with black and flake8
check: docker-build-build
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} black --check getitfixed setup.py || ( \
		echo 'Please run "make black" to format your Python code' && \
		false \
	)
	docker run --rm ${COMMON_DOCKER_RUN_OPTIONS} flake8 getitfixed

.PHONY: test
test: ## Run tests
test:
	docker-compose -f docker-compose-test.yaml run --rm test

.PHONY: clean
clean: ## Clean generated files
clean:
	rm -f $(MO_FILES)

.PHONY: cleanall
cleanall: ## Clean everything including docker containers and images
cleanall: clean
	docker-compose down --remove-orphans
	rm -f .env
	docker rmi \
		${DOCKER_BASE}-postgresql:${DOCKER_TAG} \
		${DOCKER_BASE}-build:${DOCKER_TAG} \
		${DOCKER_BASE}-getitfixed:${DOCKER_TAG} || true

# Development tools

.PHONY: bash
bash: ## Open bash in build container
bash: docker-build-build
	docker run --rm -ti ${COMMON_DOCKER_RUN_OPTIONS} bash

.PHONY: psql
psql: ## Launch psql in postgres image
psql:
	docker-compose exec -u postgres db psql getitfixed

.PHONY: psqldocs
psqldocs: ## Launch psql in postgres image
psqldocs:
	docker-compose exec -u postgres db postgresql-autodoc getitfixed

.PHONY: pshell
pshell: ## Launch getitfixed pshell
pshell:
	docker-compose run --rm getitfixed pshell getitfixed://development.ini

.PHONY: update-catalog
update-catalog: ## Update the source localisation files (*.po)
	$(DOCKER_MAKE_CMD) update-catalog-internal


# Docker images

.PHONY: docker-build-postgresql
docker-build-postgresql:
	docker build -t ${DOCKER_BASE}-postgresql:${DOCKER_TAG} postgresql

.PHONY: docker-build-build
docker-build-build:
	docker build --target=build -t ${DOCKER_BASE}-build:${DOCKER_TAG} .

.PHONY: docker-build-getitfixed
docker-build-getitfixed: docker-build-build
	$(DOCKER_MAKE_CMD) jslibs compile-catalog config.yaml
	docker build --target=getitfixed --build-arg GIT_HASH=${GIT_HASH} -t ${DOCKER_BASE}-getitfixed:${DOCKER_TAG} .

.PHONY: docker-push
docker-push: ## Push docker images on docker hub
	docker push ${DOCKER_BASE}-build:${DOCKER_TAG}
	docker push ${DOCKER_BASE}-getitfixed:${DOCKER_TAG}

.PHONY: docker-pull
docker-pull: ## Pull docker images from docker hub
	docker pull ${DOCKER_BASE}-build:${DOCKER_TAG}
	docker pull ${DOCKER_BASE}-getitfixed:${DOCKER_TAG}

.PHONY: docker-compile-catalog
docker-compile-catalog: docker-build-build
	$(DOCKER_MAKE_CMD) compile-catalog config.yaml

# Targets used inside docker build container

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

update-catalog-internal:
	pot-create -c lingua.cfg --keyword _ -o getitfixed/locale/getitfixed.pot \
		getitfixed/models/ \
		getitfixed/views/ \
		getitfixed/templates/ \
		config.yaml && \
	msgmerge --update getitfixed/locale/fr/LC_MESSAGES/getitfixed.po getitfixed/locale/getitfixed.pot && \
	msgmerge --update getitfixed/locale/de/LC_MESSAGES/getitfixed.po getitfixed/locale/getitfixed.pot

# .env depends on user makefile
.env: $(MAKEFILE_LIST)

.PHONY: jslibs
jslibs: $(addprefix $(JS_LIBS_FOLDER)/,$(JS_LIBS))

# Rules

$(JS_LIBS_FOLDER)/%: /opt/getitfixed/node_modules/%
	mkdir -p $(dir $@)
	cp $< $@

%.mo: %.po
	msgfmt $< --output-file=$@

%: %.mako
	c2c-template \
		--runtime-environment-pattern '$${{{}}}' \
		--vars vars.yaml \
		--engine mako \
		--files $<

config.yaml: vars.yaml
	c2c-template --vars vars.yaml --get-config config.yaml project smtp getitfixed
