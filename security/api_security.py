
import os
import jwt
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Union
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

# JWT Secret Key - in production, load from secure location
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-for-jwt")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

# API Key header security
api_key_header = APIKeyHeader(name="X-API-Key")

# Bearer token security
token_auth_scheme = HTTPBearer()

# API Key store - in production, use a database
API_KEYS = {
    # Format: "api_key": {"client_id": "client1", "scopes": ["read", "write"], "rate_limit": 100}
}

# Rate limiting store
RATE_LIMITS = {
    # Format: "client_id": {"count": 0, "reset_at": timestamp}
}

class APISecurityManager:
    """Manages API security including authentication, authorization, and rate limiting"""

    @staticmethod
    def generate_api_key(client_id: str, scopes: List[str], rate_limit: int = 100) -> str:
        """Generate a new API key for a client"""
        # Create a random API key
        api_key = secrets.token_hex(16)

        # Store API key info
        API_KEYS[api_key] = {
            "client_id": client_id,
            "scopes": scopes,
            "rate_limit": rate_limit
        }

        return api_key

    @staticmethod
    def verify_api_key(api_key: str = Security(api_key_header)):
        """Verify API key and apply rate limiting"""
        if api_key not in API_KEYS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "APIKey"},
            )

        # Get client info
        client_info = API_KEYS[api_key]
        client_id = client_info["client_id"]

        # Apply rate limiting
        now = int(time.time())

        # Initialize rate limit tracking if needed
        if client_id not in RATE_LIMITS:
            # Reset window is 1 hour
            RATE_LIMITS[client_id] = {"count": 0, "reset_at": now + 3600}

        # Check if the window has expired and reset if needed
        if now > RATE_LIMITS[client_id]["reset_at"]:
            RATE_LIMITS[client_id] = {"count": 0, "reset_at": now + 3600}

        # Check rate limit
        rate_limit = client_info["rate_limit"]
        if RATE_LIMITS[client_id]["count"] >= rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again after {RATE_LIMITS[client_id]['reset_at'] - now} seconds.",
            )

        # Increment request count
        RATE_LIMITS[client_id]["count"] += 1

        # Return client info for further use
        return client_info

    @staticmethod
    def create_jwt_token(client_id: str, scopes: List[str]) -> str:
        """Create a JWT token for authentication"""
        expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)

        payload = {
            "sub": client_id,
            "scopes": scopes,
            "exp": expiration
        }

        # Create JWT token
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(token_auth_scheme)):
        """Verify JWT token and extract claims"""
        token = credentials.credentials

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

            # Check expiration
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has no expiration",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload

        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def check_scope(required_scope: str, token_scopes: List[str]) -> bool:
        """Check if token has the required scope"""
        return required_scope in token_scopes

# Dependency for scope-based authorization
def require_scope(required_scope: str):
    """Dependency that checks if a token has the required scope"""
    def _require_scope(payload: Dict = Depends(APISecurityManager.verify_jwt_token)):
        scopes = payload.get("scopes", [])
        if not APISecurityManager.check_scope(required_scope, scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {required_scope}",
            )
        return payload
    return _require_scope
