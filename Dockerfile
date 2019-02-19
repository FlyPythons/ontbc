FROM python:3.5-alpine
COPY . /usr/src/ontbc

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

RUN set -ex \
        && cd /usr/src/ontbc \
        && chmod 755 ontbc.py

ENV PATH=$PATH:/usr/src/ontbc

CMD ontbc.py --help