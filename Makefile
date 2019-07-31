INSTANCE_ID ?= main
APACHE_ENTRY_POINT ?= /

MO_FILES = $(addprefix getitfixed/locale/, fr/LC_MESSAGES/getitfixed.mo de/LC_MESSAGES/getitfixed.mo)

ifneq (,$(findstring CYGWIN, $(shell uname)))
PYTHON3 =
VENV_BIN = .build/venv/Scripts
PIP_UPGRADE = python.exe -m pip install --upgrade pip setuptools
else
PYTHON3 = -p python3
VENV_BIN = .build/venv/bin
PIP_UPGRADE = pip install --upgrade pip==9.0.1 setuptools==36.5.0
endif

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo
	@echo "- build                   Install getitfixed"
	@echo "- initdb                  (Re-)initialize the database"
	@echo "- serve                   Run the dev server"
	@echo "- check                   Check the code with flake8"
	@echo "- modwsgi                 Create files for Apache mod_wsgi"
	@echo "- test                    Run the unit tests"
	@echo "- dist                    Build a source distribution"
	@echo "- update-catalog          Update message catalog"
	@echo "- compile-catalog         Compile message catalog"
	@echo

.PHONY: build
build: \
		.build/requirements.timestamp \
		.build/node_modules.timestamp \
		compile-catalog

.PHONY: initdb
initdb: .build/requirements.timestamp
	$(VENV_BIN)/initialize_getitfixed_db development.ini

.PHONY: serve
serve: build
	$(VENV_BIN)/pserve --reload development.ini

.PHONY: check
check: flake8

.PHONY: flake8
flake8: .build/requirements-dev.timestamp
	$(VENV_BIN)/flake8 getitfixed

.PHONY: modwsgi
modwsgi: build .build/getitfixed.wsgi .build/apache.conf

.PHONY: test
test: build .build/requirements-dev.timestamp
	$(VENV_BIN)/pytest

.PHONY: update-catalog
update-catalog: .build/requirements.timestamp
	$(VENV_BIN)/pot-create -c lingua.cfg --keyword _ -o getitfixed/locale/getitfixed.pot \
	    getitfixed/models/ \
	    getitfixed/views/ \
	    getitfixed/templates/
	msgmerge --update getitfixed/locale/fr/LC_MESSAGES/getitfixed.po getitfixed/locale/getitfixed.pot
	msgmerge --update getitfixed/locale/de/LC_MESSAGES/getitfixed.po getitfixed/locale/getitfixed.pot

.PHONY: compile-catalog
compile-catalog: $(MO_FILES)

.PHONY: dist
dist: .build/venv.timestamp compile-catalog
	$(VENV_BIN)/python setup.py sdist

%.mo: %.po
	msgfmt $< --output-file=$@

.build/node_modules.timestamp: package.json
	npm install
	touch $@

.build/venv.timestamp:
	# Create a Python virtual environment.
	virtualenv $(PYTHON3) .build/venv
	# Upgrade packaging tools.
	$(VENV_BIN)/$(PIP_UPGRADE)
	touch $@

.build/requirements.timestamp: .build/venv.timestamp requirements.txt
	$(VENV_BIN)/pip install -r requirements.txt -e .
	touch $@

.build/requirements-dev.timestamp: .build/venv.timestamp requirements-dev.txt
	$(VENV_BIN)/pip install -r requirements-dev.txt > /dev/null 2>&1
	touch $@

.build/getitfixed.wsgi: getitfixed.wsgi
	sed 's#\[DIR\]#$(CURDIR)#' $< > $@
	chmod 755 $@

.build/apache.conf: apache.conf .build/venv.timestamp
	sed -e 's#\[PYTHONPATH\]#$(shell $(VENV_BIN)/python -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_lib())")#' \
        -e 's#\[WSGISCRIPT\]#$(abspath .build/getitfixed.wsgi)#' \
        -e 's#\[INSTANCE_ID\]#$(INSTANCE_ID)#' \
        -e 's#\[APACHE_ENTRY_POINT\]#$(APACHE_ENTRY_POINT)#' $< > $@

.PHONY: clean
clean:
	rm -f .build/venv/getitfixed.wsgi
	rm -f .build/apache.conf
	rm -f $(MO_FILES)

.PHONY: cleanall
cleanall:
	rm -rf .build
	rm -rf node_modules
