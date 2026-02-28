# Vintique E-commerce Platform - Deployment Guide

## 📁 Project Structure

```
vintique/
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── routes/
│   │   ├── utils/
│   │   ├── core/
│   │   └── health.py
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── gunicorn.conf.py
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── src/
│   ├── public/
│   └── dist/
├── docker-compose.yml
├── .env
└── logs/
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js (for local frontend development)
- Python 3.11+ (for local backend development)

### Environment Setup
1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your values:
   ```env
   # Database
   MYSQL_ROOT_PASSWORD=your_secure_root_password
   MYSQL_DATABASE=vintique_db
   MYSQL_USER=vintique_user
   MYSQL_PASSWORD=your_secure_user_password

   # JWT
   JWT_SECRET_KEY=your_super_secret_jwt_key_here_change_in_production
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret

   # Gunicorn
   GUNICORN_WORKERS=3
   GUNICORN_TIMEOUT=120
   GUNICORN_KEEPALIVE=2
   ```

### Running the Application

#### Option 1: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Option 2: Individual Services
```bash
# Start database only
docker-compose up -d db

# Start backend
cd backend && docker-compose up --build backend

# Start frontend
cd frontend && docker-compose up --build frontend
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **phpMyAdmin**: http://localhost:8080 (localhost only)

## 📊 Service Architecture

### Frontend Service
- **Port**: 3000
- **Technology**: Vite + Vanilla JavaScript
- **Web Server**: Nginx (in production)
- **Environment**: VITE_API_URL=http://localhost:8000

### Backend Service
- **Port**: 8000
- **Technology**: FastAPI + Python
- **Web Server**: Gunicorn
- **Database**: MySQL 8.0
- **File Storage**: Cloudinary

### Database Service
- **Port**: 3306
- **Technology**: MySQL 8.0
- **Persistence**: Docker volume
- **Health Checks**: Enabled

## 🔧 Development Workflow

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Database Migrations
```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade (if needed)
alembic downgrade -1
```

## 🐳 Docker Services

### Service Dependencies
```
frontend → backend → db
phpmyadmin → db
```

### Health Checks
All services include health checks:
- Frontend: Nginx response check
- Backend: `/health` endpoint
- Database: MySQL ping
- phpMyAdmin: Web interface check

### Volumes
- `mysql_data`: Persistent database storage
- `logs`: Application logs

## 🔒 Security Features

- **Environment Variables**: All secrets in `.env`
- **phpMyAdmin**: Localhost only access
- **CORS**: Configured for frontend
- **Input Validation**: Comprehensive validation on all endpoints
- **Authentication**: JWT-based auth with proper expiration
- **Authorization**: Role-based access control

## 📝 Environment Variables

### Required Variables
- `MYSQL_ROOT_PASSWORD`: Database root password
- `MYSQL_DATABASE`: Database name
- `MYSQL_USER`: Database user
- `MYSQL_PASSWORD`: Database user password
- `JWT_SECRET_KEY`: JWT signing secret
- `CLOUDINARY_CLOUD_NAME`: Cloudinary cloud name
- `CLOUDINARY_API_KEY`: Cloudinary API key
- `CLOUDINARY_API_SECRET`: Cloudinary API secret

### Optional Variables
- `GUNICORN_WORKERS`: Number of worker processes (default: 3)
- `GUNICORN_TIMEOUT`: Request timeout in seconds (default: 120)
- `GUNICORN_KEEPALIVE`: Keep-alive timeout (default: 2)

## 🚦 Production Deployment

### Pre-deployment Checklist
- [ ] Update all environment variables
- [ ] Set strong passwords
- [ ] Configure Cloudinary credentials
- [ ] Set up SSL certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting

### Deployment Commands
```bash
# Production build
docker-compose -f docker-compose.yml --env-file .env up --build -d

# Scale services (if needed)
docker-compose up --scale backend=3 --scale frontend=2

# Update services
docker-compose pull && docker-compose up -d
```

## 🔍 Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Health Monitoring
- Backend health: `curl http://localhost:8000/health`
- Database health: `docker-compose ps`
- Resource usage: `docker stats`

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database is running: `docker-compose ps`
   - Verify environment variables
   - Check database logs: `docker-compose logs db`

2. **Frontend Can't Reach Backend**
   - Verify backend is running
   - Check CORS settings
   - Verify API URL in frontend

3. **Image Upload Failed**
   - Check Cloudinary credentials
   - Verify file size limits
   - Check network connectivity

4. **Migration Failed**
   - Check database connection
   - Verify migration file syntax
   - Rollback if needed: `alembic downgrade -1`

### Reset Services
```bash
# Stop and remove all containers
docker-compose down -v

# Remove all images
docker system prune -a

# Rebuild and start
docker-compose up --build -d
```

## 📞 Support

For issues and questions:
1. Check logs: `docker-compose logs`
2. Verify environment variables
3. Check service health: `docker-compose ps`
4. Review this documentation

---

**Note**: This setup is optimized for development and can be easily adapted for production deployment with additional security and monitoring configurations.
