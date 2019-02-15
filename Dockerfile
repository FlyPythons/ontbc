FROM python:3.5-alpine

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ARG ONTBC_VERSION=1.1
RUN set -ex \
        && wget https://github.com/FlyPythons/ontbc/archive/v${ONTBC_VERSION}.tar.gz \
        && tar xzf v${ONTBC_VERSION}.tar.gz \
        && rm -rf v${ONTBC_VERSION}.tar.gz \
        && mv ontbc-${ONTBC_VERSION} ontbc \
        && cd ontbc \
        && chmod 755 ontbc.py

ENV PATH=$PATH:/usr/src/app/ontbc

CMD ontbc.py --help