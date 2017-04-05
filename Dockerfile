FROM alpine:3.5

MAINTAINER Bolotin Dmitry <bolotin.dmitriy@gmail.com>

RUN apk add --update \
    git openjdk8 python \
    python-dev \
    && rm -rf /var/cache/apk/*


