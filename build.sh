#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Change to the project directory where manage.py is located
cd StayEase

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
