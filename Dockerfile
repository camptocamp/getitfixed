FROM camptocamp/c2cwsgiutils:3
LABEL maintainer Camptocamp "info@camptocamp.com"

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install --assume-yes --no-install-recommends 'nodejs' && \
    apt-get clean && \
    rm --recursive --force /var/lib/apt/lists/*

RUN pip3 install pydevd  # For development

RUN mkdir /app

COPY package.json /app
RUN cd app && npm install

COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt

COPY * /app/
WORKDIR /app

RUN pip3 install --no-deps -e .
