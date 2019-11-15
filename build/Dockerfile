FROM camptocamp/c2cwsgiutils:3

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

COPY requirements.txt /tmp/

RUN \
  cd /tmp && \
  pip3 install --disable-pip-version-check --no-cache-dir --requirement requirements.txt && \
  # for mypy
  # touch /usr/local/lib/python3.6/dist-packages/zope/__init__.py && \
  # touch /usr/local/lib/python3.6/dist-packages/c2c/__init__.py && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*

RUN mkdir /opt/getitfixed
COPY package.json /opt/getitfixed
RUN cd /opt/getitfixed && npm install

RUN mkdir /src

WORKDIR /src

CMD ["make"]
