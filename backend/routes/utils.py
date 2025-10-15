import jwt
import os
from fastapi import Header, HTTPException, status
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


async def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify Supabase JWT token from Authorization header
    
    Args:
        authorization: Bearer token from header
    
    Returns:
        Decoded token payload with user info
    
    Raises:
        HTTPException: If token is invalid or missing
    """
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        # Get Supabase JWT secret
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        if not jwt_secret:
            # If JWT_SECRET is not set, try to decode without verification (development only)
            # In production, you MUST set SUPABASE_JWT_SECRET
            print("WARNING: SUPABASE_JWT_SECRET not set. Decoding token without verification.")
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False, 
                    "verify_exp": False,
                    "verify_aud": False  # Skip audience verification
                }
            )
        else:
            # Decode and verify token with the JWT secret
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                options={
                    "verify_signature": True, 
                    "verify_exp": True,
                    "verify_aud": False  # Skip audience verification for now
                }
            )
        
        return payload
    
    except jwt.ExpiredSignatureError as e:
        print(f"Token expired: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except ValueError as e:
        print(f"Invalid header format: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


def extract_user_id(payload: dict) -> str:
    """Extract user ID from decoded JWT payload"""
    
    # Supabase JWT structure: payload["sub"] contains user ID
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )
    
    return user_id


def extract_user_email(payload: dict) -> str:
    """Extract email from decoded JWT payload"""
    
    email = payload.get("email")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in token"
        )
    
    return email
