FROM camptocamp/c2cwsgiutils:3

# To be removed at sometime
RUN \
  . /etc/os-release && \
  apt-get update && \
  # To be removed at sometime
  apt-get install --assume-yes --no-install-recommends apt-file && apt-file update

RUN \
  . /etc/os-release && \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends \
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

RUN mkdir /src

WORKDIR /src

CMD ["make"]
