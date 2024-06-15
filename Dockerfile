FROM python:3.12-slim-bookworm

LABEL maintainer "Thomas David, thomasdavid0@gmail.com"

WORKDIR /usr/src

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD fcscore ./fcscore
COPY logging.conf .
COPY config.py .
COPY main.py .
RUN mkdir logs

ARG TAG
ENV PUBLIC_VERSION $TAG
RUN echo "VERSION = $TAG"

EXPOSE 8000
CMD [ "gunicorn", "-c", "config.py", "main:app", "--log-config", "logging.conf"]

