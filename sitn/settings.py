import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env', override=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEVELOPMENT_MODE = False

IS_INTRANET = True if os.environ.get("IS_INTRANET") == "True" else False

if 'DEVELOPMENT_MODE' in os.environ and os.environ['DEVELOPMENT_MODE'] == "True":
    DEVELOPMENT_MODE = True
    GDAL_PATH = os.environ.get('GDAL_PATH')
    GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')
    GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
else:
    if IS_INTRANET:
        # Allows cross origin cookies for PEGGI trying to reach secured sitnintra endpoints
        # Only in production otherwise cookies will not be set on localhost because not HTTPS
        CSRF_COOKIE_SECURE = True
        SESSION_COOKIE_SECURE = True
        CSRF_COOKIE_SAMESITE = 'None'
        SESSION_COOKIE_SAMESITE = 'None'
        CORS_ALLOW_CREDENTIALS = True

DEBUG = DEVELOPMENT_MODE

# Application definition

# List of apps that must not be visible on internet
INTRANET_ONLY_APPS = [
    'cats',
    'parcel_historisation',
    'intranet_proxy',
    'ecap_intra'
]

INTERNET_ONLY_APPS = [
    'stationnement',
    'forest_forpriv',
    'health',
    'ecap',
    'action_sociale',
]

INSTALLED_APPS = [
    'sitn',
    'cadastre',
    "corsheaders",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_gis',
    'drf_spectacular',
    'drf_spectacular_sidecar'
]

if IS_INTRANET:
    INSTALLED_APPS = INTRANET_ONLY_APPS + INSTALLED_APPS
else:
    INSTALLED_APPS = INTERNET_ONLY_APPS + INSTALLED_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if IS_INTRANET:
    MIDDLEWARE.append('sitn.middleware.RemoteSitnMiddleware')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
]

SERIALIZATION_MODULES = {
    "geojson": "django.contrib.gis.serializers.geojson", 
 }

ROOT_URLCONF = 'sitn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'sitn/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ["PGDATABASE"],
        'USER': os.environ["PGUSER"],
        'HOST': os.environ["PGHOST"],
        'PORT': os.environ["PGPORT"],
        'PASSWORD': os.environ["PGPASSWORD"],
        'OPTIONS': {
            'options': '-c search_path=' + os.environ["PGSCHEMA"] + ',public'
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'fr-ch'

TIME_ZONE = 'Europe/Zurich'

USE_I18N = True

USE_TZ = True

# CORS, CSRF AND SSL

ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

CORS_DEV_ORIGINS = [
    "http://localhost:4200",
    "http://localhost:4300",
    "https://localhost:4200",
    "https://localhost:4300",
    "http://localhost:5173"
]

CORS_ALLOWED_ORIGINS = CORS_DEV_ORIGINS + list(map(str.rstrip, os.environ["CORS_ALLOWED_ORIGINS"].split(",")))

CSRF_USE_SESSIONS = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_DOMAIN = os.environ["CSRF_COOKIE_DOMAIN"]
CSRF_TRUSTED_ORIGINS = []
for host in CORS_ALLOWED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(host)

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

FORCE_SCRIPT_NAME = os.environ.get('ROOTURL', '')

STATIC_URL = FORCE_SCRIPT_NAME + '/assets/'

STATIC_ROOT = os.path.join(BASE_DIR, 'assets')

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

WHITENOISE_STATIC_PREFIX = "/assets/"

DEFAULT_FROM_EMAIL = 'no-reply@ne.ch'

if DEVELOPMENT_MODE:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "emails_sent"
else:
    EMAIL_HOST = os.environ["EMAIL_HOST"]


NEARCH2_CONSULTATION = os.environ.get('NEARCH2_CONSULTATION')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {module} {filename} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOGGING_LEVEL', 'ERROR'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('LOGGING_LEVEL', 'ERROR'),
            'propagate': False,
        },
        # Unncomment this for SQL logs
        #"django.db.backends": {
        #    "handlers": ["console"],
        #    "level": "DEBUG",
        #},
    },
}

INTRANET_PROXY = {
    'geoshop_user': os.getenv('GEOSHOP_USER', ''),
    'geoshop_password': os.getenv('GEOSHOP_PASSWORD', ''),
    'geoshop_url': os.getenv('GEOSHOP_URL', 'https://sitn.ne.ch/geoshop2_api/'),
    'test_url': 'metadata/at701_potentiel_sda',
    'vcron_url': os.getenv('VCRON_URL'),
    'vcron_user': os.getenv('VCRON_USER'),
    'vcron_password': os.getenv('VCRON_PASSWORD'),
    'infolica_api_url': os.getenv('INFOLICA_API_URL'),
}

HEALTH = {
    'front_url': os.getenv('DOCTORS_URL', 'http://localhost:5173/edit/')
}

# Be aware that by changing the PAGE_SIZE parameter, you will have to
# adjust the client page pagination parameter (limit) as well, like as in 
# parcel_historisation\static\parcel_historisation\parcel_historisation.js
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PAGE_SIZE': 20
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Sitn REST API',
    'DESCRIPTION': 'Home of SITN REST Services',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

DEFAULT_SRID = 2056

