FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update && apt install --yes --no-install-recommends build-essential libpq-dev libgdal-dev && apt-get clean

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip3 install -r /app/requirements.txt
