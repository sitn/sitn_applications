# sitn_applications

## Requirements

* PostgreSQL > 10 + PostGIS
* Python >= 3.6
* GDAL >= 2.4 (see instructions below to install it in your dev venv)

## Getting started

Fork and clone this repository. Make a copy of the `.env` file and adapt it to your environment settings:

```
cp .env.sample .env
```

and configure the different variables.

## Running in development mode

First, create a copy of the `env.sample` file called `env.dev`:

```
cp .env.sample .env.dev
```

Install the virual environment:

```
 .\utilities\activate_python_env.ps1
 python -m venv venv
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
