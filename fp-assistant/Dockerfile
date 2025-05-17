FROM python:3.9-alpine AS builder

WORKDIR /app

ARG BUILD_DEPS="build-base gcc libffi-dev openssl-dev"

RUN apk add --no-cache ${BUILD_DEPS} \
&& python -m venv .venv \
&& .venv/bin/pip install --no-cache-dir -U pip setuptools

ADD requirements.txt requirements.txt

RUN .venv/bin/pip install --no-cache-dir -r /app/requirements.txt \
&& find /app/.venv \
\( -type d -a -name test -o -name tests \) \
-o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
-exec rm -rf '{}' \+


FROM python:3.9-alpine

ARG RUNTIME_DEPS="libressl"

RUN apk update \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache openjdk8-jre

ENV JAVAHOME="/usr/lib/jvm/java-1.8-openjdk/bin/java"

RUN apk add --no-cache ${RUNTIME_DEPS}

COPY --from=builder /app /app

ADD /app /app

ADD .env .env

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "/app/main.py"]
