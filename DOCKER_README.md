# Docker Setup cho Django Project

## Cấu trúc Files

- `Dockerfile` - Production Docker image
- `Dockerfile.dev` - Development Docker image  
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `entrypoint.sh` - Script khởi tạo container
- `nginx.conf` - Nginx configuration cho production
- `.dockerignore` - Files bỏ qua khi build Docker image

## Development Setup

### 1. Tạo file environment
```bash
cp env.example .env
# Chỉnh sửa các giá trị trong .env theo môi trường của bạn
```

### 2. Chạy development environment
```bash
# Build và start containers
docker-compose up --build

# Hoặc chạy background
docker-compose up -d --build
```

### 3. Truy cập ứng dụng
- Django app: http://localhost:8000
- Admin panel: http://localhost:8000/admin
- API docs: http://localhost:8000/swagger/

### 4. Các lệnh hữu ích
```bash
# Xem logs
docker-compose logs -f web

# Chạy Django commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Stop containers
docker-compose down

# Stop và xóa volumes
docker-compose down -v
```

## Production Setup

### 1. Chuẩn bị environment variables
Tạo file `.env` với các giá trị production:
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_NAME=your_prod_db
DATABASE_USER=your_prod_user
DATABASE_PASSWORD=your_prod_password
# ... các biến khác
```

### 2. Deploy production
```bash
# Build và start production containers
docker-compose -f docker-compose.prod.yml up --build -d

# Xem logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Truy cập production
- App: http://your-domain.com
- Admin: http://your-domain.com/admin

## Docker Commands

### Build image
```bash
# Production image
docker build -t object-backend .

# Development image
docker build -f Dockerfile.dev -t object-backend:dev .
```

### Run container
```bash
# Production
docker run -p 8000:8000 --env-file .env object-backend

# Development
docker run -p 8000:8000 --env-file .env -v $(pwd):/app object-backend:dev
```

## Troubleshooting

### Database connection issues
```bash
# Check database container
docker-compose exec db psql -U postgres -d object_db

# Reset database
docker-compose down -v
docker-compose up --build
```

### Permission issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Clear Docker cache
```bash
docker system prune -a
docker volume prune
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `True` |
| `SECRET_KEY` | Django secret key | Required |
| `DATABASE_NAME` | PostgreSQL database name | `object_db` |
| `DATABASE_USER` | PostgreSQL username | `postgres` |
| `DATABASE_PASSWORD` | PostgreSQL password | `postgres` |
| `DATABASE_HOST` | Database host | `db` (in Docker) |
| `DATABASE_PORT` | Database port | `5432` |
| `LOCAL_FE` | Local frontend URL | `http://localhost:3000` |
| `PROD_FE` | Production frontend URL | Required for production |
| `CC_NAME` | Cloudinary cloud name | Required |
| `CC_API_KEY` | Cloudinary API key | Required |
| `CC_API_SECRET` | Cloudinary API secret | Required |

## Security Notes

1. **Never commit `.env` files** - Chúng chứa thông tin nhạy cảm
2. **Use strong SECRET_KEY** trong production
3. **Set DEBUG=False** trong production
4. **Use HTTPS** trong production với proper SSL certificates
5. **Regularly update** base images và dependencies

