# HeartMark EC2 deployment

This directory contains templates for an Ubuntu EC2 deployment using Nginx and
Gunicorn. The expected application directory is `/home/ubuntu/HeartMark` and the
virtual environment directory is `venv`.

Production secrets belong in `/home/ubuntu/HeartMark/.env`. Never commit that
file. Before starting the service, run migrations and collect static files:

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Install the service templates after reviewing the domain and paths:

```bash
sudo cp deploy/heartmark.service /etc/systemd/system/heartmark.service
sudo cp deploy/nginx-heartmark.conf /etc/nginx/sites-available/heartmark
sudo ln -s /etc/nginx/sites-available/heartmark /etc/nginx/sites-enabled/heartmark
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload
sudo systemctl enable --now heartmark
sudo nginx -t
sudo systemctl reload nginx
```
