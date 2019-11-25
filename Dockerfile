
# We need to compile c2cgeoform l10n files
FROM ubuntu:18.04 AS c2cgeoform

RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends \
        ca-certificates \
        gettext \
        git \
        nodejs \
        npm \
        make

RUN mkdir -p /src && \
    git clone https://github.com/camptocamp/c2cgeoform.git /opt/c2cgeoform && \
    cd /opt/c2cgeoform && \
    mkdir .build/ && \
    git checkout 5fda87acc14ff0f59380c5a5e0f14abf580406d4 && \
    make c2cgeoform/static/dist/index.js compile-catalog



FROM camptocamp/c2cwsgiutils:3 AS build

RUN \
  . /etc/os-release && \
  echo "deb https://deb.nodesource.com/node_10.x ${VERSION_CODENAME} main" > /etc/apt/sources.list.d/nodesource.list && \
  curl --silent https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends \
    'nodejs=10.*' \
    gettext git make openjdk-8-jre-headless python-pip python-setuptools unzip wget && \
  echo "Keep apt cache for now"
  #apt-get clean && \
  #rm --recursive --force /var/lib/apt/lists/*

RUN \
  pip3 install --disable-pip-version-check --no-cache-dir \
    babel \
    black==18.6b1 \
    c2c.template \
    flake8==3.7.8 \
    lingua \
 && \
  # for mypy
  # touch /usr/local/lib/python3.6/dist-packages/zope/__init__.py && \
  # touch /usr/local/lib/python3.6/dist-packages/c2c/__init__.py && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*

RUN mkdir /opt/getitfixed

COPY package.json /opt/getitfixed
RUN cd /opt/getitfixed && npm install

# We need to install getitfixed to get custom lingua_extractor
COPY requirements.txt /opt/getitfixed
RUN pip3 install -r /opt/getitfixed/requirements.txt
COPY . /opt/getitfixed
RUN pip3 install --no-deps -e /opt/getitfixed

RUN mkdir /src
WORKDIR /src

CMD ["make"]



FROM camptocamp/c2cwsgiutils:3 AS getitfixed
LABEL maintainer Camptocamp "info@camptocamp.com"

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install --assume-yes --no-install-recommends 'nodejs' && \
    apt-get clean && \
    rm --recursive --force /var/lib/apt/lists/*

# For development
RUN pip3 install waitress pydevd pyramid_ipython ipdb webtest ipython==5.8.0

RUN mkdir /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt

# Install c2cgeoform from getitfixed branch
COPY --from=c2cgeoform /opt/c2cgeoform /opt/c2cgeoform
RUN pip3 install -e /opt/c2cgeoform

COPY . /app/
WORKDIR /app

RUN pip3 install --no-deps -e .

ENV PROXY_PREFIX=
