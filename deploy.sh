#!/bin/sh

# Exit immediately on error
set -e

# echo "Apply Migrations.."
# python manage.py makemigrations

# echo "Applying Migrations.."
# python manage.py migrate

# echo "Create Superadmin"
# python manage.py createsuperadmin

echo "deploy.py"
python deploy.py

# echo "Starting Server.."
# python manage.py runserver 0.0.0.0:8000

# echo "Run deploy.py"
# python deploy.py