#!/bin/sh
. venv/bin/activate
gunicorn wsgi --preload -b :8000 --threads=10 --workers=4 --timeout=60 --max-requests=1000 --log-level 'warn'