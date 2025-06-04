from fastapi import Security, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import secrets
import time
from datetime import datetime, timedelta
import threading

# Simulated API key store (in production, use a secure database)
API_KEYS = {
    "test-key": {
        "client_id": "test-client",
        "rate_limit": 100,  # requests per minute
        "expires": datetime.now() + timedelta(days=30)
    }
}

# Rate limiting storage (in production, use Redis or similar)
RATE_LIMITS = {}
rate_limit_lock = threading.Lock()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_api_key(api_key: str = Security(api_key_header)) -> dict:
    """Validate API key and return client info"""
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    client_info = API_KEYS[api_key]
    if client_info["expires"] < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    return client_info

def check_rate_limit(client_id: str, rate_limit: int) -> None:
    """Check if client has exceeded their rate limit"""
    current_time = time.time()
    minute_ago = current_time - 60
    
    with rate_limit_lock:
        # Initialize or clean up old requests
        if client_id not in RATE_LIMITS:
            RATE_LIMITS[client_id] = []
        
        # Remove requests older than 1 minute
        RATE_LIMITS[client_id] = [t for t in RATE_LIMITS[client_id] if t > minute_ago]
        
        # Check rate limit
        if len(RATE_LIMITS[client_id]) >= rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {rate_limit} requests per minute."
            )
        
        # Add current request
        RATE_LIMITS[client_id].append(current_time)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Dependency for verifying API key and rate limits"""
    client_info = get_api_key(api_key)
    check_rate_limit(client_info["client_id"], client_info["rate_limit"])
    return client_info 