from fastapi import APIRouter
from datetime import datetime

health_router = APIRouter()

@health_router.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "vintique-backend"
    }
