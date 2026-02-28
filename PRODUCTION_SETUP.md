# 🚀 Vintique E-commerce - Production Setup Guide

## 📋 Prerequisites

- Docker & Docker Compose
- Domain name (for production)
- SSL certificates (optional but recommended)
- Cloudinary account for image storage

## 🏗️ Project Structure

```
vintique/
├── backend/                    # FastAPI backend
│   ├── Dockerfile             # Production backend image
│   ├── app/
│   ├── alembic/
│   └── requirements.txt
├── frontend/                   # Vite + React frontend
│   ├── Dockerfile.prod         # Production frontend image
│   ├── Dockerfile.dev          # Development frontend image
│   ├── nginx.conf              # Nginx configuration
│   └── src/
├── docker-compose.yml          # Current setup
├── docker-compose.prod.yml     # Production setup
├── docker-compose.dev.yml      # Development setup
├── scripts/
│   └── deploy.sh              # Deployment script
└── .env                       # Environment variables
```

## ⚙️ Environment Configuration

### 1. Setup Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

**Required Variables:**
```env
# Database
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=vintique_db
MYSQL_USER=vintique_user
MYSQL_PASSWORD=your_secure_user_password

# JWT
JWT_SECRET_KEY=your_super_secret_jwt_key_here_change_in_production

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# CORS (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🚀 Deployment Options

### Option 1: Using Deployment Script (Recommended)

```bash
# Development deployment
./scripts/deploy.sh development

# Production deployment
./scripts/deploy.sh production
```

### Option 2: Manual Docker Compose

#### Development
```bash
docker-compose -f docker-compose.dev.yml up --build -d
```

#### Production
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Option 3: Individual Services

```bash
# Build frontend
docker build -t vintique-frontend ./frontend -f ./frontend/Dockerfile.prod

# Build backend
docker build -t vintique-backend ./backend

# Run with production compose
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 Service Configuration

### Frontend (Nginx + Vite)
- **Port**: 80 (HTTP), 443 (HTTPS)
- **Build**: Multi-stage Docker build
- **Features**:
  - Static asset optimization
  - Gzip compression
  - Security headers
  - API proxy to backend
  - SPA routing support

### Backend (FastAPI + Gunicorn)
- **Port**: 8000 (internal)
- **Workers**: 3 (configurable)
- **Features**:
  - Production WSGI server
  - Health checks
  - CORS configuration
  - Request logging

### Database (MySQL 8.0)
- **Port**: 3306 (internal)
- **Features**:
  - Persistent storage
  - Optimized configuration
  - Health checks
  - Slow query logging

### Redis (Optional - Production)
- **Port**: 6379 (internal)
- **Features**:
  - Caching layer
  - Session storage
  - Memory optimization

## 🔧 Production Configuration

### 1. SSL/HTTPS Setup

```bash
# Create SSL directory
mkdir -p ssl

# Add your certificates
# ssl/cert.pem
# ssl/key.pem
```

### 2. Domain Configuration

Update `.env` for production:
```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production
```

### 3. Performance Optimization

Production docker-compose includes:
- Resource limits
- Health checks
- Optimized MySQL settings
- Redis caching
- Nginx optimization

## 🔍 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Health Checks
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Manual health check
curl http://localhost/health
curl http://localhost:8000/health
```

## 🗄️ Database Management

### Migrations
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create new migration
docker-compose -f docker-compose.prod.yml exec backend alembic revision --autogenerate -m "Description"

# Rollback
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

### Backups
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec db mysqldump -u root -p vintique_db > backup.sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T db mysql -u root -p vintique_db < backup.sql
```

## 🔒 Security Features

### Implemented
- Environment variable secrets
- Non-root Docker users
- Security headers
- CORS restrictions
- SSL/TLS support
- Rate limiting ready
- Input validation

### Additional Recommendations
- Set up fail2ban
- Configure firewall
- Use secrets management
- Regular security updates
- Monitor access logs

## 🚀 Scaling

### Horizontal Scaling
```bash
# Scale frontend
docker-compose -f docker-compose.prod.yml up --scale frontend=3

# Scale backend
docker-compose -f docker-compose.prod.yml up --scale backend=3
```

### Load Balancer Setup
For production, consider:
- Nginx load balancer
- HAProxy
- Cloud load balancer (AWS ALB, etc.)

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: ./scripts/deploy.sh production
```

## 🛠️ Troubleshooting

### Common Issues

1. **Frontend not loading**
   ```bash
   # Check nginx logs
   docker-compose logs frontend
   # Verify nginx config
   docker-compose exec frontend nginx -t
   ```

2. **Backend API errors**
   ```bash
   # Check backend logs
   docker-compose logs backend
   # Verify database connection
   docker-compose exec backend curl http://db:3306
   ```

3. **Database connection issues**
   ```bash
   # Check database status
   docker-compose ps db
   # Test connection
   docker-compose exec backend alembic current
   ```

### Reset Services
```bash
# Full reset
docker-compose -f docker-compose.prod.yml down -v
docker system prune -f
./scripts/deploy.sh production
```

## 📊 Performance Monitoring

### Metrics to Monitor
- Response times
- Error rates
- Database performance
- Memory usage
- CPU usage

### Tools
- Docker stats
- Application logs
- Database slow query log
- External monitoring (Prometheus, Grafana)

## 🎯 Production Checklist

Before going live:

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations run
- [ ] CORS origins set correctly
- [ ] Health checks passing
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Security review completed
- [ ] Load testing performed
- [ ] Documentation updated

## 📞 Support

For production issues:
1. Check logs: `docker-compose logs`
2. Verify environment: `docker-compose ps`
3. Review this documentation
4. Check GitHub issues

---

**🎉 Your Vintique e-commerce platform is now production-ready!**
