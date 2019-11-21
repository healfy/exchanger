ARG docker_repository=''
FROM ${docker_repository}bonum-base-python:3.6

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

RUN apt-get clean; \
    apt-get update; \
    pip install --upgrade pip; \
    rm -rf /tmp/*; \
    apt-get clean; \
    rm -rf /var/log/*
ENV LANG ru_RU.UTF-8

RUN mkdir /app
WORKDIR /app
ADD ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
CMD run.sh
