##########################################
# Common base for build/test and runtime #
##########################################
FROM python:3.12-slim AS base

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --disable-pip-version-check --no-cache-dir -r /app/requirements.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*


########################
# Build and test image #
########################
FROM base AS build

RUN apt-get update && apt-get install -y \
    curl \
    gettext \
    gnupg \
    make

RUN \
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
  apt-get install --assume-yes --no-install-recommends \
    nodejs \
  && \
  apt-get clean && \
  rm --recursive --force /var/lib/apt/lists/*

COPY package.json /opt/getitfixed/
RUN cd /opt/getitfixed && npm install

COPY requirements-dev.txt /tmp/
RUN pip3 install --disable-pip-version-check --no-cache-dir -r /tmp/requirements-dev.txt && \
  rm --recursive --force /tmp/* /var/tmp/* /root/.cache/*

WORKDIR /app
COPY . /app/
RUN pip3 install --no-deps -e .

CMD ["make"]


#################
# Runtime image #
#################
FROM base AS getitfixed
LABEL maintainer="Camptocamp <info@camptocamp.com>"

COPY --from=build /opt/getitfixed/ /opt/getitfixed/
ENV NODE_PATH=/opt/thinkhazard/node_modules

WORKDIR /app
COPY --from=build /app/ /app/
RUN pip install --no-deps -e .

ENV PROXY_PREFIX=
