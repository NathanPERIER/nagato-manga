FROM alpine:latest

RUN apk update  \
 && apk upgrade \
 && apk add python3 py3-pip bash

RUN mkdir /opt/nagato-api
WORKDIR /opt/nagato-api

COPY . ./

RUN pip3 install -r requirements.txt

VOLUME /data

ENTRYPOINT gunicorn --config default-config/gunicorn.conf.py nagato-api:app
