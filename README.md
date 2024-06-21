# sitn_applications

Apps and custom webservices from SITN. This app can run in two different contexts: internet or intranet.
Depending on the context, some apps will not be installed when deploying.

## Requirements

* PostgreSQL >= 11 + PostGIS
* Python >= 3.10
* GDAL (if running without docker)
* GNU gettext https://www.gnu.org/software/gettext/

## Getting started

Fork and clone this repository. Make a copy of the `.env.sample` file and adapt it to your environment settings:

```
cp .env.sample .env
```

and configure the different variables.

## Running in development mode, without docker

First, create a copy of the `.env.sample` file called `.env`:

```
cp .env.sample .env
```

Install the virual environment:

```sh
python -m venv venv
./venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Activate your venv:

```
venv/Scripts/activate
```

Create a local database:

```shell
python manage.py createdb
```

Run migrations

```shell
python manage.py migrate
```

Dump some fresh data from prod database

```shell
python manage.py getdata
```

You're now ready to go:

```shell
python manage.py collectstatic
python manage.py compilemessages --locale=fr
python manage.py runserver
```

### Switching between the Internet & Intranet instances

If developping on the Internet instance, then you should define a new environment variable
in the `.env.dev.` file:

```
IS_INTRANET=False
```

## Running locally on Docker

First, create a copy of the `env.sample` file called `env.<context>.local`:

```
cp .env.sample .env.intranet.local
```

Then you'll be able to deploy locally on docker:

```
python deploy intranet local
```

## Deploying on production

First, create a copy of the `env.sample` file called `env.<context>.<instance>`, example:

```
cp .env.sample .env.intranet.prod
```

Then you'll be able to deploy your instance with `python deploy <context> <instance>`

```
python deploy intranet prod
```


## Tests

Running tests will require a database for testing.

```sh
python manage.py testdb
```

then you can run tests

```sh
python manage.py test --keepdb
```

## Translations

Prepare translation files

```sh
django-admin makemessages -l fr
```

then compile them

```sh
python manage.py compilemessages --locale=fr
```

## Starting a new app

```python
python manage.py startapp myapp
```

Then:

1. Put something in `urls.py` in your app folder
2. Import your urls in `sitn/urls.py`
3. Install the app in `settings.py`
4. 