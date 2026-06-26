# lyrica-server
server-side for lyrica

# Installation:

--on server:
git clone https://github.com/lyrable/lyrica-server
cd lyrica-server

--venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

--.env
cp .env.example .env
nano .env
! fill in DATABASE_URL, WORKER_SECRET, WORKER_URL !

--systemcmd launcher
sudo nano /etc/systemd/system/lyrica.service

--fill in:
[Unit]
Description=LyricApp FastAPI Server
After=network.target

[Service]
User=your_unix_user
WorkingDirectory=/home/your_unix_user/lyrica-server
EnvironmentFile=/home/your_unix_user/lyrica-server/.env
ExecStart=/home/your_unix_user/lyrica-server/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

--launch:
sudo systemctl daemon-reload
sudo systemctl enable lyrica
sudo systemctl start lyrica
sudo systemctl status lyrica

--nginx setup
sudo apt install nginx
sudo nano /etc/nginx/sites-available/lyrica

--fill in:
server {
    listen 80;
    server_name -your-domain;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # for future websocket (WIP)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

--next:
sudo ln -s /etc/nginx/sites-available/lyrica /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.ru

sudo apt install python3-venv python3-pip nginx certbot python3-certbot-nginx

# Usage:
curl -X POST https://api.yourdomain.ru/tracks/get \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "password": "mypassword", "slug": "author_name"}'