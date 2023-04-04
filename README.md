# sitn_applications

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

## Running in development mode

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

First, create a copy of the `env.sample` file called `env.local`:

```
cp .env.sample .env.local
```

Then you should use the deployment script and use the `local` choice:

```
 .\utilities\deploy.ps1
```

-> Then choose `local`

## Deploying on production

First, create a copy of the `env.sample` file called `env.`:

```
cp .env.sample .env.
```

Then you should use the deployment script and use the `prod` choice:

```
 .\utilities\deploy.ps1
```

-> Then choose `prod`
