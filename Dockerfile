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
ENV PATH="/app/venv/bin:$PATH"

COPY . ./
RUN chmod +x startup.sh

RUN IS_INTRANET=True python manage.py collectstatic --noinput && \
    IS_INTRANET=False python manage.py collectstatic --noinput && \
    python manage.py compilemessages --locale=fr

CMD ["./startup.sh"]
