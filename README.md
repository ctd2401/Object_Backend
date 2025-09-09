Step to deploy ( Ubuntu/Linux )
- Clone code
- Install PostgreSQL
    -  sudo apt install postgresql postgresql-contrib
    -  sudo systemctl start postgresql.service
    -  sudo -i -u postgres
    -  pqsl
    -  createdb Object
- sudo apt-get update
- sudo apt-get install -y libpq-dev gcc python3-dev
- install virtual enviroment ( python -m venv env )
- python3 manage.py runserver 0.0.0.0:8000

- for production
- sudo apt update
- sudo apt install -y python3-pip python3-venv python3-dev libpq-dev gcc nginx
- gunicorn --bind 0.0.0.0:8000 Object.wsgi:application
- sudo nano /etc/systemd/system/myproject.service


