FROM alpine:latest

RUN apk update  \
 && apk upgrade \
 && apk add python3 py3-pip bash

RUN mkdir /opt/nagato-api
WORKDIR /opt/nagato-api

COPY . ./

RUN pip3 install -r requirements.txt

ENV NAGATO_API_PORT=8090

LABEL version=1.0

ENTRYPOINT gunicorn --config default-config/gunicorn.conf.py nagato-api:app
