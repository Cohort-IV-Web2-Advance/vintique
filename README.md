# Vintique E-commerce API

A scalable, production-ready e-commerce API built with Python 3.11+, FastAPI, MySQL 8, SQLAlchemy, and Docker.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **MySQL 8** - Production-grade relational database
- **SQLAlchemy ORM** - Powerful SQL toolkit and ORM
- **Alembic** - Database migration tool
- **JWT Authentication** - Secure token-based authentication
- **Gunicorn + Uvicorn** - Production WSGI server
- **Docker** - Multi-stage containerized deployment
- **Cloudinary** - Cloud image management
- **phpMyAdmin** - Database management UI

## Architecture

The project follows clean architecture principles with modular design:

```
vintique/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection and session
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── core/                # Authentication & security
│   └── utils/               # Utilities (Cloudinary)
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Development & production setup
├── gunicorn.conf.py       # Production server configuration
└── .env.example           # Environment variables template
```

## Database Schema

### Users
- `id` (PK)
- `email` (unique)
- `username` (unique)
- `password` (hashed)
- `shipping_address`
- `is_admin` (Boolean)
- `created_at`, `updated_at`

### Accounts
- `id` (PK)
- `user_id` (FK → Users)
- `balance`
- `created_at`, `updated_at`

### Products
- `id` (PK)
- `name`
- `description`
- `price`
- `stock_quantity`
- `image_url` (Cloudinary)
- `created_at`, `updated_at`

### Cart
- `id` (PK)
- `user_id` (FK → Users, nullable for guest)
- `product_id` (FK → Products)
- `quantity`
- `created_at`, `updated_at`

### Orders
- `id` (PK)
- `product_id` (FK → Products)
- `user_id` (FK → Users)
- `amount`
- `quantity`
- `unit_price`
- `order_status`
- `created_at`, `updated_at`

### Transactions
- `id` (PK)
- `order_id` (FK → Orders)
- `payment_id`
- `created_at`, `updated_at`

## API Endpoints

### Public Routes
- `GET /products` - List all products
- `GET /products/{id}` - Get product details
- `POST /cart/add` - Add item to cart
- `PATCH /cart/update-qty/{id}` - Update cart quantity

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT)

### Protected Routes (JWT Required)
- `POST /checkout` - Create order
- `GET /orders/history` - User order history
- `GET /orders/{id}` - Get specific order

### Admin Routes (Admin Only)
- `GET /admin/orders` - All orders
- `GET /admin/users` - All users
- `GET /admin/products` - All products

### Inventory Management (Admin Only)
- `POST /inventory/product` - Create product (with image)
- `PUT /inventory/product/{id}` - Update product (replace image)
- `DELETE /inventory/product/{id}` - Delete product

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Cloudinary account (for image uploads)

### Setup

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
   DATABASE_URL=mysql+pymysql://vintique_user:vintique_password@db:3306/vintique_db
   
   # JWT
   JWT_SECRET_KEY=your_super_secret_jwt_key_here
   
   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

### Access Points

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **phpMyAdmin**: http://localhost:8080
- **Health Check**: http://localhost:8000/health

## Development

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start MySQL locally** or use Docker:
   ```bash
   docker-compose up db phpmyadmin
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start development server**
   ```bash
   python -m app.main
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

## Production Deployment

### Environment Variables
Ensure all sensitive data is set via environment variables in production:

- `DATABASE_URL` - MySQL connection string
- `JWT_SECRET_KEY` - Strong secret for JWT tokens
- `CLOUDINARY_*` - Cloudinary credentials
- `ENVIRONMENT=production`

### Docker Production
```bash
# Build and start production containers
docker-compose -f docker-compose.yml up --build -d

# Run migrations
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app
```

### Scaling
The application is designed to be horizontally scalable:
- Stateless API design
- External MySQL database
- Cloud-based image storage
- Load balancer ready

## Security Features

- **JWT Authentication** with configurable expiration
- **Password Hashing** using bcrypt
- **Admin Role Management** with protected endpoints
- **CORS Configuration** for cross-origin requests
- **Input Validation** using Pydantic schemas
- **SQL Injection Prevention** via SQLAlchemy ORM

## Monitoring & Logging

- **Structured Logging** with configurable levels
- **Health Check Endpoint** for monitoring
- **Request Timing** middleware
- **Error Handling** with proper HTTP status codes
- **Docker Health Checks** for container monitoring

## Performance

- **Gunicorn + Uvicorn Workers** for concurrent requests
- **Database Connection Pooling** via SQLAlchemy
- **Optimized Docker Images** with multi-stage builds
- **CDN Integration** via Cloudinary for images

## License

This project is licensed under the MIT License.
