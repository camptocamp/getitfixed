
# We need to compile c2cgeoform l10n files
FROM ubuntu:18.04 AS c2cgeoform

RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends \
        ca-certificates \
        gettext \
        git \
        make

RUN mkdir -p /src && \
    git clone -b getitfixed https://github.com/camptocamp/c2cgeoform.git /opt/c2cgeoform && \
    cd /opt/c2cgeoform && \
    git checkout 237d4f849501a3120eab802d6fa54a9249a3db20 && \
    make compile-catalog


FROM camptocamp/c2cwsgiutils:3
LABEL maintainer Camptocamp "info@camptocamp.com"

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install --assume-yes --no-install-recommends 'nodejs' && \
    apt-get clean && \
    rm --recursive --force /var/lib/apt/lists/*

# For development
RUN pip3 install pydevd pyramid_ipython ipdb webtest ipython==5.8.0

RUN mkdir /app

COPY package.json /app
RUN cd app && npm install

COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt

# Install c2cgeoform from getitfixed branch
COPY --from=c2cgeoform /opt/c2cgeoform /opt/c2cgeoform
RUN pip3 install -e /opt/c2cgeoform

COPY . /app/
WORKDIR /app

RUN pip3 install --no-deps -e .

ENV PROXY_PREFIX=
