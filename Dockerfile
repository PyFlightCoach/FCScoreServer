FROM python:3.11.4-slim-buster

LABEL maintainer "Thomas David, thomasdavid0@gmail.com"

# set working directory in container
WORKDIR /usr/src

COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

COPY . . 

ARG SOURCE_COMMIT
ENV PUBLIC_VERSION $SOURCE_COMMIT
RUN echo "SOURCE_COMMIT = $PUBLIC_VERSION"

EXPOSE 5000
ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
