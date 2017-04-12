FROM alpine:3.5

MAINTAINER Bolotin Dmitry <bolotin.dmitriy@gmail.com>

WORKDIR /opt

RUN apk add --update \
    git openjdk8 python py-yaml \
    python-dev wget zip bash perl \
    && rm -rf /var/cache/apk/*

RUN wget https://github.com/mikessh/migec/releases/download/1.2.6/migec-1.2.6.zip \
    && unzip migec-1.2.6.zip \
    && wget https://github.com/milaboratory/mixcr/releases/download/v2.1.1/mixcr-2.1.1.zip \
    && unzip mixcr-2.1.1.zip \
    && wget http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.5.zip \
    && unzip fastqc_v0.11.5.zip \
    && chmod +x /opt/FastQC/fastqc \
    && rm migec-1.2.6.zip mixcr-2.1.1.zip fastqc_v0.11.5.zip

COPY mibuddy mibuddy

ENV PATH /opt/migec-1.2.6:/opt/mixcr-2.1.1:/opt/FastQC:/opt/mibuddy:$PATH

