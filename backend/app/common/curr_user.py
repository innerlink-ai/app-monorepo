import secrets
from fastapi import APIRouter, Depends, HTTPException,Request, Depends,Response
import asyncio
from sqlalchemy.orm import Session
from data_models import Invite, User
from database import get_admin_db
from utils.security import hash_password
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Cookie
from jose import JWTError, jwt
from typing import Optional
from pydantic import BaseModel


SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(request: Request, db: Session = Depends(get_admin_db),) -> User:
    """Extracts user from JWT token stored in cookies."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Use asyncio.to_thread to make DB access non-blocking
        user = await asyncio.to_thread(
            lambda: db.query(User).filter(User.email == email).first()
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    


