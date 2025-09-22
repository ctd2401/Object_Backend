Step to deploy ( Ubuntu/Linux )
- Clone code ( into /var/www )
- Install PostgreSQL
    -  sudo apt install postgresql postgresql-contrib
    -  sudo systemctl start postgresql.service
    -  sudo -i -u postgres
    -  pqsl
    -  createdb Object
- sudo apt-get update
- sudo apt-get install -y libpq-dev gcc python3-dev
- install virtual enviroment ( python -m venv env )
- pip install -r requirements.txt
- run deploy-nginx-django.sh file ( chmod +x deploy-nginx-django.sh & ./deploy-nginx-django.sh)
- sudo -u www-data /var/www/Object_Backend/env/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 Object.wsgi:application



