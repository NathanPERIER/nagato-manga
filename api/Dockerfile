FROM alpine:latest

RUN mkdir /opt/nagato-api
WORKDIR /opt/nagato-api

COPY . ./

RUN apk update  \
 && apk upgrade \
 && apk add python3 py3-pip bash jpeg-dev zlib-dev libjpeg \
 && apk add --virtual build-deps gcc python3-dev musl-dev  \
 && pip3 install -r requirements.txt \
 && apk del build-deps

ENV NAGATO_API_PORT=8090

LABEL version=1.0

ENTRYPOINT gunicorn --config default-config/gunicorn.conf.py nagato-api:app
