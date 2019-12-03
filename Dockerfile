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
RUN pip3 install waitress pydevd pyramid_ipython ipdb webtest ipython==5.8.0 pytest==5.1.3 mock

RUN mkdir /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt

COPY . /app/
WORKDIR /app

RUN pip3 install --no-deps -e .

ENV PROXY_PREFIX=
