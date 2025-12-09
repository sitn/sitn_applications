# sitn_applications

Apps and custom webservices from SITN. This app can run in two different contexts: internet or intranet.
Depending on the context, some apps will not be installed when deploying.

## Requirements

* PostgreSQL >= 11 + PostGIS
* Python >= 3.10
* GDAL, GEOS (if running without docker on Windows, install OSGEO4W and add its bin directory to the Path)
* GNU gettext https://www.gnu.org/software/gettext/

## Getting started

Fork and clone this repository. Make a copy of the `.env.sample` file and adapt it to your environment settings:

```
cp .env.sample .env
```

and configure the different variables.

The paths related to GDAL et GEOS can either point to existing installations on the system, e.g.:

```
# Path to the folder containing all GDAL/GEOS DLLs
GDAL_PATH="C:/Program Files/GDAL/"

# Full path to the GDAL DLL
GDAL_LIBRARY_PATH="C:/Program Files/GDAL/gdal.dll"

# Full path to GEOS C API DLL
GEOS_LIBRARY_PATH="C:/Program Files/PostgreSQL/16/bin/libgeos_c.dll"
```

Alternatively, you can install GDAL (and its GEOS and PROJ dependencies), using the geospatial python wheels provided here:

* [geospatial-wheels](https://github.com/cgohlke/geospatial-wheels/releases)

Download the appropriate version, then install it in the venv using pip, e.g.:

```sh
pip install .\gdal-3.11.4-cp314-cp314-win_amd64.whl
```

Then configure the GDAL paths in the .env file to point to the ressources in the venv, e.g.:

```
# Path to the folder containing all GDAL/GEOS DLLs
GDAL_PATH="C:/Projects/sitn_applications/venv/Lib/site-packages/osgeo/"

# Full path to the GDAL DLL
GDAL_LIBRARY_PATH="C:/Projects/sitn_applications/venv/Lib/site-packages/osgeo/gdal.dll"

# Full path to GEOS C API DLL
GEOS_LIBRARY_PATH="C:/Projects/sitn_applications/venv/Lib/site-packages/osgeo/geos_c.dll"
```

You should also have PostgreSQL with PostGIS installed, and the path to PostgreSQL's `bin` directory should be defined in the `Path` variable in your Windows system environment variables (e.g. C:\Program Files\PostgreSQL\18\bin).

## Running in development mode, without docker

First, create a copy of the `.env.sample` file called `.env`:

```
cp .env.sample .env
```

Install and activate the virtual environment:

```sh
python -m venv venv
./venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements-lock.txt
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

You might want to create an admin user:

```shell
python manage.py createsuperuser
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


## Upgrading packages

In your venv:

1. Update the versions manually in requirements.in
2. `pip-compile requirements.in --output-file=requirements-lock.txt`
3. `pip install -r requirements-lock.txt`
