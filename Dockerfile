FROM ghcr.io/osgeo/gdal:ubuntu-small-3.12.1

RUN apt-get update --fix-missing && apt-get upgrade --assume-yes \
    && apt-get install --assume-yes --no-install-recommends gettext python3-pip python3-venv

COPY ./requirements-lock.txt /app/requirements-lock.txt
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1
RUN python3 -m venv venv && . venv/bin/activate && python -m pip install --upgrade pip \
    && pip install -r requirements-lock.txt \
    && pip install gunicorn

COPY . ./

ARG ENV_FILE
RUN mv ${ENV_FILE} .env && chmod +x startup.sh

# Run migrations to create model permissions here
RUN export $(egrep -v '^#' .env | xargs) && \
    . venv/bin/activate && \
    python manage.py collectstatic --noinput && \
    python manage.py compilemessages --locale=fr && \
    python manage.py migrate
