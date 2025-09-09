# Sử dụng image Python chính thức
FROM python:3.11-slim

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Cài các gói cần thiết
# RUN apt-get update && apt-get install -y netcat gcc libpq-dev
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        netcat-openbsd \
        gcc \
        libpq-dev \
        build-essential \
        libffi-dev \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Tạo thư mục app và chuyển vào đó
WORKDIR /app

# Copy toàn bộ mã nguồn vào image
COPY . /app

# Cài đặt các dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Mở port (nếu chạy bằng runserver)
EXPOSE 8000

# Mặc định chạy lệnh này (có thể thay đổi)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
