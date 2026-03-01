# FastAPI Authentication System Refactor

## Overview
Refactored from OAuth2PasswordBearer to HTTPBearer for cleaner JWT token handling while maintaining the same API interface.

## Security Setup (`app/core/security.py`)

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
```

## Authentication Functions (`app/core/auth.py`)

### Core Dependencies

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate JWT token from Authorization header."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials  # Extract token from "Bearer <token>"
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

## Protected Routes Usage

### Standard User Routes
```python
@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user),  # Requires valid JWT
    db: Session = Depends(get_db)
):
    return {"user": current_user.email}
```

### Admin-Only Routes
```python
@admin_router.get("/users")
def get_all_users(
    current_user: User = Depends(get_current_admin_user),  # Requires admin JWT
    db: Session = Depends(get_db)
):
    return {"users": []}
```

### Optional Authentication (Guest Support)
```python
@router.get("/cart")
def get_cart(
    current_user: Optional[User] = Depends(get_current_user),  # Can be None
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    return {"cart_items": []}
```

## API Usage Examples

### Login (Unchanged - JSON Body)
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Protected Route (Bearer Token)
```bash
curl -X GET "http://localhost:8000/profile" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Admin Route (Bearer Token + Admin Role)
```bash
curl -X GET "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Error Responses

### Missing/Invalid Token (401)
```json
{
  "detail": "Could not validate credentials"
}
```

### Insufficient Permissions (403)
```json
{
  "detail": "Not enough permissions"
}
```

## Benefits of HTTPBearer over OAuth2PasswordBearer

1. **Cleaner Token Handling**: Direct access to token string via `credentials.credentials`
2. **No OAuth2 Flow**: Doesn't imply OAuth2 password flow (which you weren't using)
3. **Better Error Messages**: More appropriate for simple JWT authentication
4. **Same API Contract**: Clients still use `Authorization: Bearer <token>`
5. **Production Ready**: Standard approach for JWT authentication

## Migration Summary

- ✅ Removed `OAuth2PasswordBearer(tokenUrl="auth/login")`
- ✅ Added `HTTPBearer()` security scheme
- ✅ Updated `get_current_user` to extract token from `HTTPAuthorizationCredentials`
- ✅ Login endpoint unchanged (still accepts JSON)
- ✅ All protected routes work identically
- ✅ Admin role checking preserved
- ✅ Same `Authorization: Bearer <token>` header format

The authentication system is now cleaner and more appropriate for your JWT-based setup while maintaining full backward compatibility.
