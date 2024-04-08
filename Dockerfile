FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.4

RUN apt-get update --fix-missing
RUN apt-get install gettext python3-pip libcairo2-dev build-essential python3-dev \
    pipenv python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info libpq-dev -y


# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal


COPY ./requirements.txt /app/requirements.txt
WORKDIR /app


ENV PYTHONUNBUFFERED 1
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . ./

ARG ENV_FILE
RUN mv ${ENV_FILE} .env

RUN export $(egrep -v '^#' .env | xargs) && \
    python manage.py collectstatic --noinput && \
    python manage.py compilemessages --locale=fr
