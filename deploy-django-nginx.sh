#!/usr/bin/env bash
set -euo pipefail

# -----------------------
# Thông tin cấu hình
# -----------------------
DOMAIN="your_domain"
EMAIL="your_email"     # Email nhận thông báo từ Let's Encrypt
PROJECT_NAME="Object"   # Thư mục chứa Django project
PROJECT_DIR="/root/Object_Backend/${PROJECT_NAME}"
VENV_DIR="/root/Object_Backend/env"
GUNICORN_SERVICE="gunicorn"

# -----------------------
# Cài đặt gói cần thiết
# -----------------------
echo "[1/6] Cài đặt gói cần thiết..."
sudo apt update
sudo apt install -y python3-venv python3-pip nginx certbot python3-certbot-nginx

# -----------------------
# Thiết lập virtualenv + gunicorn
# -----------------------
echo "[2/6] Tạo virtualenv và cài đặt Django + Gunicorn..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install -U pip django gunicorn
deactivate

# -----------------------
# Tạo systemd service cho Gunicorn
# -----------------------
echo "[3/6] Tạo systemd service cho Gunicorn..."
sudo tee /etc/systemd/system/${GUNICORN_SERVICE}.service > /dev/null <<EOF
[Unit]
Description=Gunicorn daemon for Django
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=${PROJECT_DIR}
ExecStart=${VENV_DIR}/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind 127.0.0.1:8000 \\
          ${PROJECT_NAME}.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now ${GUNICORN_SERVICE}

# -----------------------
# Cấu hình Nginx cho domain
# -----------------------
echo "[4/6] Tạo cấu hình nginx cho domain ${DOMAIN}..."
NGINX_CONF="/etc/nginx/sites-available/${DOMAIN}.conf"

sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/${DOMAIN}.conf"

sudo nginx -t
sudo systemctl reload nginx

# -----------------------
# Xin chứng chỉ SSL từ Let's Encrypt
# -----------------------
echo "[5/6] Xin chứng chỉ SSL từ Let's Encrypt..."
sudo certbot --nginx -d "${DOMAIN}" -m "${EMAIL}" --agree-tos --no-eff-email --redirect

# -----------------------
# Hoàn tất
# -----------------------
echo "[6/6] Hoàn tất triển khai Django + Nginx + HTTPS cho domain ${DOMAIN}"
echo "Kiểm tra bằng cách mở: https://${DOMAIN}"
