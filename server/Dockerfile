FROM python:2.7.14-alpine3.6

MAINTAINER info@thingforward.io

WORKDIR /usr/src/app
COPY *.py ./

RUN pip install Flask requests

EXPOSE 8081

CMD [ "python", "./trashfox.py" ]
