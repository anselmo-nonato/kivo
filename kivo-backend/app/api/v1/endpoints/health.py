from fastapi import APIRouter
import redis.asyncio as aioredis
from app.core.config import settings

router = APIRouter()

@router.get("/health", summary="Health Check do Sistema")
async def health_check():
    """
    Verifica a disponibilidade da API e conectividade com o Redis.
    """
    redis_status = "unknown"
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pong = await r.ping()
        if pong:
            redis_status = "connected"
        await r.aclose()
    except Exception as e:
        redis_status = f"unreachable: {str(e)}"

    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {
            "api": "online",
            "redis": redis_status
        }
    }
