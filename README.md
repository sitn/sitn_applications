# sitn_applications

Apps and custom webservices from SITN. This app can run in two different contexts: internet or intranet.
Depending on the context, some apps will not be installed when deploying.

## Requirements

* PostgreSQL >= 11 + PostGIS
* Python >= 3.10
* GDAL (if running without docker)

## Getting started

Fork and clone this repository. Make a copy of the `.env.sample` file and adapt it to your environment settings:

```
cp .env.sample .env.dev
```

and configure the different variables.

### Database

A database with a schema named according to your .env file is required.

## Running in development mode, without docker

First, create a copy of the `.env.sample` file called `.env.dev`:

```
cp .env.sample .env.dev
```

Install the virual environment:

```
python -m venv venv
.\utilities\activate_python_env.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

In order for the application to load the environment variables, you should start the dev server using
the dedicated Powershell script:

```
cd utilities
.\run_dev_server.ps1
```

## Running locally on Docker

First, create a copy of the `env.sample` file called `env.<context>.<instance>`:

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
