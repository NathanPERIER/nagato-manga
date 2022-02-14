FROM alpine:latest

RUN apk update  \
 && apk upgrade \
 && apk add python3 py3-pip bash

RUN mkdir /opt/nagato-api
WORKDIR /opt/nagato-api

COPY . ./

RUN pip3 install -r requirements.txt

VOLUME /data

ENV NAGATO_PORT=8090

ENTRYPOINT gunicorn --config default-config/gunicorn.conf.py nagato-api:app
