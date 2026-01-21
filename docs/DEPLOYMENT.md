# Deployment Guide

This guide covers deployment strategies for the Student Grading System.

## Prerequisites

- Python 3.10+
- MySQL 5.7+ or 8.x
- Server with sufficient resources (recommended: 2GB RAM, 2 CPU cores)
- Docker + Docker Compose (recommended)

## Recommended Deployment: Docker Compose

For most deployments, Docker Compose provides the simplest and most reproducible setup (API + MySQL).

### 1. Create `.env`

```bash
cp env.example .env
```

Update `.env` values for production (especially `SECRET_KEY` and `DATABASE_URL`).

### 2. Example `docker-compose.yml`

Create a `docker-compose.yml` in the project root:

```yaml
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: student_grading_db
      MYSQL_USER: grading_user
      MYSQL_PASSWORD: secure_password
      MYSQL_ROOT_PASSWORD: root_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### 3. Example `Dockerfile`

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. Run

```bash
docker compose up --build
```

API docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Production Environment Setup

This section describes a non-Docker installation (manual Python + MySQL). Use this if Docker is not an option.

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.10 python3-pip python3-venv -y

# Install MySQL server
sudo apt install mysql-server -y
```

### 2. Database Setup

```bash
# Login to MySQL
sudo mysql -u root -p

# Create database and user
CREATE DATABASE student_grading_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'grading_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON student_grading_db.* TO 'grading_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Application Deployment

```bash
# Clone repository
git clone <your-repo-url> /opt/student_grading_system
cd /opt/student_grading_system

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with production settings
cp env.example .env
nano .env  # Edit with production values
```

### 4. Environment Variables

Ensure your `.env` file contains:

```env
DATABASE_URL=mysql+mysqlconnector://grading_user:secure_password@localhost:3306/student_grading_db
SECRET_KEY=<generate-a-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=False
PROJECT_NAME=Student Grading System
API_V1_PREFIX=/api/v1
```

**Generate a secure SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 5. Database Migrations

```bash
# Run migrations (if using Alembic)
alembic upgrade head

# Or initialize database schema
python -m app.database.init_db
```

### 6. Create Upload Directory

```bash
mkdir -p uploads
chmod 755 uploads
```

## Running with Uvicorn

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

## Running as a Systemd Service

Create `/etc/systemd/system/student-grading.service`:

```ini
[Unit]
Description=Student Grading System API
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/student_grading_system
Environment="PATH=/opt/student_grading_system/.venv/bin"
ExecStart=/opt/student_grading_system/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable student-grading
sudo systemctl start student-grading
sudo systemctl status student-grading
```

## Nginx Reverse Proxy

Create `/etc/nginx/sites-available/student-grading`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/student_grading_system/uploads;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/student-grading /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/HTTPS Setup (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Docker Deployment (Alternative)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+mysqlconnector://user:password@db:3306/student_grading_db
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: student_grading_db
      MYSQL_USER: grading_user
      MYSQL_PASSWORD: secure_password
      MYSQL_ROOT_PASSWORD: root_password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

Run with:
```bash
docker-compose up -d
```

## Backup Strategy

### Database Backup

```bash
# Create backup script
cat > /opt/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
mysqldump -u grading_user -p student_grading_db > $BACKUP_DIR/backup_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/backup_db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /opt/backup_db.sh
```

### Upload Files Backup

```bash
# Backup uploads directory
tar -czf /opt/backups/uploads_$(date +%Y%m%d).tar.gz /opt/student_grading_system/uploads
```

## Monitoring

### Logs

- Application logs: Check systemd journal
  ```bash
  sudo journalctl -u student-grading -f
  ```

- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### Health Check Endpoint

The API should expose a health check endpoint:

```http
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Security Checklist

- [ ] Change default MySQL root password
- [ ] Use strong SECRET_KEY in production
- [ ] Set DEBUG=False in production
- [ ] Configure firewall (only allow ports 80, 443, 22)
- [ ] Enable SSL/HTTPS
- [ ] Regularly update system packages
- [ ] Set up automated backups
- [ ] Configure file upload size limits
- [ ] Implement rate limiting (if needed)
- [ ] Review and restrict CORS origins

## Troubleshooting

### Database Connection Issues
```bash
# Check MySQL status
sudo systemctl status mysql

# Test connection
mysql -u grading_user -p student_grading_db
```

### Permission Issues
```bash
# Fix upload directory permissions
sudo chown -R www-data:www-data /opt/student_grading_system/uploads
sudo chmod -R 755 /opt/student_grading_system/uploads
```

### Port Already in Use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>
```
