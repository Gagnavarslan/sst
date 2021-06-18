FROM themattrix/tox

RUN apt-get update
RUN apt-get install -y xvfb

COPY . /app

WORKDIR /app
