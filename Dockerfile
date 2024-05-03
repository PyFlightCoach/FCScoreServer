FROM python:3.12-slim-bookworm

LABEL maintainer "Thomas David, thomasdavid0@gmail.com"

WORKDIR /usr/src

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app app
COPY gunicorn_config.py .
COPY wsgi.py .
COPY main.py .

ARG TAG
ENV PUBLIC_VERSION $TAG
RUN echo "VERSION = $TAG"

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
