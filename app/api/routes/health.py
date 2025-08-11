"""
Health check endpoints for Kansofy-Trade
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, test_database_connection
from app.core.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "kansofy-trade",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with database connectivity"""
    
    # Test database connection
    db_healthy = await test_database_connection()
    
    # Check upload directory
    upload_dir_exists = settings.upload_path.exists()
    upload_dir_writable = settings.upload_path.is_dir() and settings.upload_path.stat().st_mode & 0o200
    
    # Overall health status
    overall_healthy = all([
        db_healthy,
        upload_dir_exists,
        upload_dir_writable
    ])
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "kansofy-trade",
        "version": "1.0.0",
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "connection": db_healthy
            },
            "storage": {
                "status": "healthy" if (upload_dir_exists and upload_dir_writable) else "unhealthy",
                "upload_dir_exists": upload_dir_exists,
                "upload_dir_writable": upload_dir_writable,
                "upload_dir_path": str(settings.upload_path)
            }
        },
        "configuration": {
            "database_path": settings.database_path,
            "max_file_size": settings.max_file_size,
            "allowed_extensions": settings.allowed_extensions,
            "debug_mode": settings.debug
        }
    }


@router.get("/health/readiness")
async def readiness_check() -> Dict[str, Any]:
    """Kubernetes-style readiness probe"""
    db_healthy = await test_database_connection()
    
    if not db_healthy:
        return {"status": "not_ready", "reason": "database_unavailable"}
    
    return {"status": "ready"}


@router.get("/health/liveness")
async def liveness_check() -> Dict[str, Any]:
    """Kubernetes-style liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}