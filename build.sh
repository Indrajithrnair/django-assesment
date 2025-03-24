#!/usr/bin/env bash

# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Make sure we have gettext for translations
apt-get update && apt-get install -y gettext

# Compile translation files if gettext is available
if command -v msgfmt &> /dev/null; then
    echo "Compiling translation files..."
    django-admin compilemessages
else
    echo "Warning: gettext not available, skipping translation compilation"
fi

# Configure the app for production
export DJANGO_SETTINGS_MODULE=assessment.settings
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=".onrender.com"

# Collect static files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
