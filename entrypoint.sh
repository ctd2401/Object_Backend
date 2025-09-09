#!/bin/sh


# while ! nc -z db 5432; do
#   sleep 0.1
# done

# echo "PostgreSQL started"

# # Apply migrations
# python manage.py migrate

# # Khởi động server
# python manage.py runserver 0.0.0.0:8000



echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 1
done

echo "PostgreSQL started"


echo "makemigrations"
python manage.py makemigrations

echo "Apply migrations"
python manage.py migrate

# Khởi động server
echo "Starting server"
exec python manage.py runserver 0.0.0.0:8000
