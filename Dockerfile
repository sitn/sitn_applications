FROM python:3.12.5-slim-bookworm

RUN apt update && apt install --yes libgdal-dev libffi-dev gettext && apt-get clean

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt
