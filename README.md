# 🛍️ Vintique E-commerce Platform

A modern, production-ready e-commerce platform for vintage items built with FastAPI backend, vanilla JavaScript frontend, and Docker containerization.

## ✨ Features

- 🛒 **Complete E-commerce Flow** - Product catalog, shopping cart, checkout, and order management
- 👤 **User Management** - Secure JWT authentication with role-based access control
- 💳 **Payment Integration** - Paystack payment gateway with webhook handling
- 🖼️ **Cloud Storage** - Cloudinary integration for product images
- 🛠️ **Admin Panel** - Inventory management and order oversight
- 🐳 **Docker Ready** - Multi-stage containerized deployment
- 📱 **Responsive Design** - Mobile-first Tailwind CSS styling
- 🔒 **Security First** - Password hashing, CORS, input validation
- 📊 **Monitoring** - Health checks, structured logging, performance tracking

## 🏗️ Architecture

```
vintique/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # PostgreSQL connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── schemas/           # Pydantic validation
│   │   ├── core/              # Authentication & security
│   │   └── utils/             # Cloudinary integration
│   ├── alembic/              # Database migrations
│   ├── Dockerfile            # Multi-stage container
│   └── gunicorn.conf.py     # Production server config
├── frontend/                  # Vanilla JavaScript frontend
│   ├── index.html            # Homepage
│   ├── products.html         # Product catalog
│   ├── cart.html            # Shopping cart
│   ├── login.html           # User authentication
│   ├── admin.html           # Admin panel
│   ├── js/                 # JavaScript modules
│   ├── src/                # Tailwind CSS
│   └── public/             # Static assets
├── docker-compose.yml         # Development setup
├── docker-compose.prod.yml    # Production setup
└── scripts/                 # Deployment utilities
```

## 🗄️ Database Schema

### Core Models

#### **Users & Authentication**
- **User**: Email, username, hashed password, shipping address, admin status
- **Account**: User wallet balance for future payment methods
- **Guest**: Anonymous cart support with UUID tracking

#### **Products & Inventory**
- **Product**: Name, description, price, stock, Cloudinary image URL
- **Soft Deletes**: Products marked as deleted rather than removed

#### **Shopping & Orders**
- **Cart**: User/guest cart items with quantity tracking
- **Order**: Product orders with status tracking (pending, completed, etc.)
- **Transaction**: Paystack payment records with full transaction details

### **Relationships**
```
User 1:1 Account
User 1:N Cart
User 1:N Orders
Product 1:N Cart
Product 1:N Orders
Order 1:N Transactions
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Cloudinary account (for image uploads)
- Paystack account (for payments)

### Development Setup

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd vintique
   cp .env.example .env
   ```

2. **Configure environment variables**
   Edit `.env` file with your actual values:
   ```env
   # Database
   DATABASE_URL=postgresql+psycopg2://vintique_user:vintique_password@db:5432/vintique_db
   
   # JWT
   JWT_SECRET_KEY=your_super_secret_jwt_key_here
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   
   # Paystack
   PAYSTACK_SECRET_KEY=your_paystack_secret_key
   PAYSTACK_PUBLIC_KEY=your_paystack_public_key
   PAYMENT_CALLBACK_URL=http://localhost:8000/api/payments/webhook
   ```

3. **Start development environment**
   ```bash
   docker-compose up --build
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

### Access Points

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:8080
- **Health Check**: http://localhost:8000/health

## 🌐 Production Deployment

### Build & Deploy

1. **Build production images**
   ```bash
   # Build frontend
   docker build -t vintique-frontend ./frontend -f ./frontend/Dockerfile.prod
   
   # Build backend
   docker build -t vintique-backend ./backend
   ```

2. **Deploy with production compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Production Services

#### Frontend (Nginx + Static Files)
- **Port**: 80 (HTTP), 443 (HTTPS)
- **Features**:
  - Static asset optimization
  - Gzip compression
  - Security headers
  - API proxy to backend
  - SPA routing support

#### Backend (FastAPI + Gunicorn)
- **Port**: 8000 (or dynamic PORT from environment)
- **Workers**: Configurable Gunicorn workers
- **Features**:
  - Production logging
  - Health checks
  - Request timing
  - Error handling
  - Dynamic port binding for cloud platforms

#### Database (PostgreSQL)
- **Port**: 5432
- **Features**:
  - Connection pooling
  - Automated backups
  - Health monitoring

## 📚 API Documentation

### Public Routes
- `GET /products` - List all products
- `GET /products/{id}` - Get product details
- `POST /cart/add` - Add item to cart (guest support)
- `PATCH /cart/update-qty/{id}` - Update cart quantity

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT)

### Protected Routes (JWT Required)
- `GET /orders/history` - User order history
- `GET /orders/{id}` - Get specific order
- `POST /checkout` - Create order
- `GET /cart` - Get cart contents

### Admin Routes (Admin Only)
- `GET /admin/orders` - All orders
- `GET /admin/users` - All users
- `POST /inventory/product` - Create product (with image)
- `PUT /inventory/product/{id}` - Update product
- `DELETE /inventory/product/{id}` - Delete product

### Payment Routes
- `POST /payments/webhook` - Paystack webhook handler

## 🔐 Security Features

- **JWT Authentication** with configurable expiration
- **Password Hashing** using bcrypt
- **Admin Role Management** with protected endpoints
- **CORS Configuration** for cross-origin requests
- **Input Validation** using Pydantic schemas
- **SQL Injection Prevention** via SQLAlchemy ORM
- **HMAC Signature Verification** for payment webhooks

## 🛠️ Development

### Local Development

1. **Install dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Start services locally**
   ```bash
   # Database only
   docker-compose up db pgadmin
   
   # Backend development
   cd backend
   python -m app.main
   
   # Frontend development
   cd frontend
   npm run dev
   ```

### Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

## 📊 Monitoring & Performance

### Health Checks
- **Backend**: `/health` endpoint
- **Database**: PostgreSQL health checks
- **Containers**: Docker health monitoring

### Logging
- **Structured Logging** with configurable levels
- **Request Timing** middleware
- **Error Handling** with proper HTTP status codes

### Performance
- **Gunicorn + Uvicorn Workers** for concurrent requests
- **Database Connection Pooling** via SQLAlchemy
- **Optimized Docker Images** with multi-stage builds
- **CDN Integration** via Cloudinary for images

## 🎨 Frontend Technology

### Stack
- **Vanilla JavaScript** (ES6+) - No framework dependencies
- **Tailwind CSS v4** - Utility-first styling
- **Responsive Design** - Mobile-first approach
- **Modular Architecture** - Separated concerns

### Features
- **Product Gallery** with image previews
- **Shopping Cart** with local storage persistence
- **User Authentication** with JWT tokens
- **Admin Panel** for inventory management
- **Form Validation** and error handling

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `JWT_SECRET_KEY` | JWT signing secret | ✅ |
| `CLOUDINARY_*` | Cloudinary credentials | ✅ |
| `PAYSTACK_*` | Paystack payment credentials | ✅ |
| `ENVIRONMENT` | development/production | ✅ |
| `CORS_ORIGINS` | Allowed CORS origins | ✅ |

### Docker Configuration

- **Multi-stage builds** for optimized images
- **Health checks** for all services
- **Volume mounting** for persistent data
- **Network isolation** for security

## 📈 Scalability

The application is designed to be horizontally scalable:
- **Stateless API** design
- **External PostgreSQL** database
- **Cloud-based image** storage
- **Load balancer ready** architecture
- **Container orchestration** compatible

## 🚀 Production Server Configuration

### Gunicorn Settings
The backend uses Gunicorn with Uvicorn workers for production:

- **Dynamic Port Binding**: Supports cloud platforms like Render via `PORT` environment variable
- **Worker Processes**: Configurable number of workers (default: 3)
- **Worker Class**: Uvicorn for async support
- **Connection Management**: 1000 connections per worker
- **Timeout Settings**: Configurable timeout and keepalive
- **Graceful Shutdown**: 30-second graceful timeout
- **Logging**: Structured access and error logs

### Production Optimizations
- **Preload App**: Reduces memory usage per worker
- **Request Limits**: 1000 requests per worker before restart
- **Health Monitoring**: Built-in health checks
- **Performance Headers**: Request timing information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the [API Documentation](http://localhost:8000/docs)
- Review the [Production Setup Guide](./PRODUCTION_SETUP.md)
- Open an issue on GitHub

---

**Built with ❤️ for the vintage community**
