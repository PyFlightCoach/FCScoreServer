FROM python:3.12-slim-bookworm

LABEL maintainer "Thomas David, thomasdavid0@gmail.com"

WORKDIR /usr/src

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD fcscore ./fcscore
COPY logging.conf .
COPY gunicorn.conf.py .
COPY main.py .
RUN mkdir logs
RUN touch logs/gunicorn.access.log
RUN touch logs/gunicorn.error.log
RUN touch logs/gunicorn.root.log

ARG TAG
ENV PUBLIC_VERSION $TAG
RUN echo "VERSION = $TAG"

EXPOSE 5000
CMD [ "gunicorn", "main:app"]

