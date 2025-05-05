import secrets
from fastapi import APIRouter, Depends, HTTPException,Request, Depends,Response

from sqlalchemy.orm import Session
from data_models import Invite, User, PasswordResetToken
from database import get_admin_db
from utils.security import hash_password
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from common.curr_user import get_current_user
from utils.email import send_invite_email, send_password_reset_email
import uuid
from sqlalchemy import text
# Add this to your auth routes file
from pydantic import BaseModel
from typing import Optional
import time
from fastapi import Depends, HTTPException, Request, status
from utils.security import hash_password, verify_password

# Rate limiting variables for enhanced security
PASSWORD_ATTEMPT_LIMIT = 5
PASSWORD_LOCKOUT_MINUTES = 15
password_attempts = {}  # user_id: {"count": 0, "lockout_until": timestamp}



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_ACCESS_TOKEN_EXPIRE_DAYS=1

SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key")
ALGORITHM = "HS256"


@router.get("/invite")
def get_invite_details(token: str, db: Session = Depends(get_admin_db)):
    #invite = db.query(Invite).filter(Invite.token == token).first()

    invite = db.execute(
        text("""
            SELECT admin.decrypt_data(encrypted_email, 'invites') AS email
            FROM admin.invites_encrypted
            WHERE admin.decrypt_data(encrypted_token, 'invites') = :token
        """),
        {"token": token}
    ).fetchone()
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid invite token")
    return {"email": invite.email}



# ✅ Pydantic model for user registration
class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    token: str



@router.post("/register")
def register_user(response: Response, request: RegisterUserRequest, db: Session = Depends(get_admin_db)):
    # ✅ Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    # ✅ Validate the invite token and get access_role
    invite = db.query(Invite).filter_by(email=request.email, token=request.token).first()
    if not invite:
        raise HTTPException(status_code=403, detail="Invalid invite")

    # ✅ Set the user's access role based on the invite
    access_role = invite.access_role  # ✅ Can be "admin" or "user"

    # ✅ Create and save the new user
    new_user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        is_admin=(access_role == "admin"),  # ✅ Convert role to boolean for admin access
    )
    db.add(new_user)
    
    # Delete all pending invites for this email
    db.query(Invite).filter(Invite.email == request.email).delete()
    
    db.commit()
    
    access_token = create_access_token(data={"sub": new_user.email, "role": "admin" if new_user.is_admin else "user"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(data={"sub": new_user.email}, expires_delta=timedelta(days=REFRESH_ACCESS_TOKEN_EXPIRE_DAYS))  

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  
        secure=True,   
        samesite="Strict"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict"
    )
    
    return {
        "message": "Registration successful",
    }


class LoginRequest(BaseModel):
    email: str
    password: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # ✅ Fix here
# ✅ Verify Password


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/login")
def login_user(response: Response, login_data: LoginRequest, db: Session = Depends(get_admin_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email, "role": "admin" if user.is_admin else "user"}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(days=REFRESH_ACCESS_TOKEN_EXPIRE_DAYS))  

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  
        secure=True,   
        samesite="Strict"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict"
    )
    return {"message": "Login successful"}



@router.post("/logout")
def logout(response: Response):
    """Clears the authentication cookie."""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logged out successfully"}





@router.get("/user-info")
def get_user_info(user: User = Depends(get_current_user)):
    """Fetch authenticated user info (email + role)."""
    return {
        "email": user.email,
        "name": user.full_name,
        "is_admin": user.is_admin
    }



@router.post("/refresh")
def refresh_token(request: Request, response: Response):
    """Refreshes the access token if the refresh token is valid."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Generate a new access token
        new_access_token = create_access_token(data={"sub": email})

        # Set new access token in the cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="Strict"
        )
        return {"message": "Token refreshed successfully"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@router.get("/check-first-user")
def check_first_user(db: Session = Depends(get_admin_db)):
    """Check if there are any users or invites in the database."""
    # Check for any users
    user_count = db.query(User).count()
    # Check for any invites
    invite_count = db.query(Invite).count()
    
    return {
        "has_users": user_count > 0,
        "has_invites": invite_count > 0,
        "is_first_user": user_count == 0 and invite_count == 0
    }

class InviteRequest(BaseModel):
    email: EmailStr

@router.post("/invite")
def create_invite(request: InviteRequest, db: Session = Depends(get_admin_db)):
    """Create an invite for the first user."""
    # Check if there are any users or invites
    user_count = db.query(User).count()
    invite_count = db.query(Invite).count()
    
    if user_count > 0 or invite_count > 0:
        raise HTTPException(
            status_code=403,
            detail="Cannot create invite: users or invites already exist"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Create a new invite
    invite_token = str(uuid.uuid4())
    invite = Invite(
        email=request.email,
        token=invite_token,
        expires_at=datetime.utcnow() + timedelta(hours=48),
        access_role="admin"  # First user is always an admin
    )

    db.add(invite)
    db.commit()
    
    return {
        "message": "Invite created successfully",
        "token": invite_token
    }




# Add this to your auth routes file



# Security model
class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    newPassword: Optional[str] = None
    currentPassword: Optional[str] = None

    
@router.put("/user")
def update_user_info(
    request: Request,
    update_request: UserUpdateRequest,
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_admin_db)
):
    """Update user information with security measures."""
    try:
        # Password change requested
        if update_request.newPassword:
            # Verify current password is provided
            if not update_request.currentPassword:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required to update password"
                )
            
            # Verify current password is correct
            if not verify_password(update_request.currentPassword, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )
            
            # Check password complexity
            if len(update_request.newPassword) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="New password must be at least 8 characters long"
                )
            
            # Update password
            user.password_hash = hash_password(update_request.newPassword)
        
        # Update name if provided
        if update_request.name is not None:
            user.full_name = update_request.name
        
        # Save changes - no explicit transaction needed
        db.commit()
        
        return {"message": "User information updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user information: {str(e)}"
        )

# --- Password Reset Functionality ---

class PasswordResetRequest(BaseModel):
    email: EmailStr

@router.post("/password-reset-request")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_admin_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    # Important: Do not reveal if the user exists for security reasons
    if user:
        # Generate token
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1) # Token valid for 1 hour
        
        # Delete any existing tokens for this user
        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
        
        # Store new token
        reset_token = PasswordResetToken(
            user_id=user.id, 
            token=token, 
            expires_at=expires
        )
        db.add(reset_token)
        db.commit()
        
        # Send email (implement send_password_reset_email in utils/email.py)
        try:
            send_password_reset_email(email=user.email, token=token)
        except Exception as e:
            # Log the error, but don't expose details to the client
            print(f"Error sending password reset email: {e}") # Replace with proper logging
            # Even if email fails, don't tell the user, might reveal email validity
            pass 
            
    # Always return a generic success message
    return {"message": "If an account with that email exists, a password reset link has been sent."}

class PasswordResetPayload(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password")
def reset_password(payload: PasswordResetPayload, db: Session = Depends(get_admin_db)):
    if not payload.token or not payload.new_password:
        raise HTTPException(status_code=400, detail="Token and new password are required")

    # Find the token
    reset_token_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == payload.token).first()
    
    if not reset_token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    # Check expiry
    if datetime.utcnow() > reset_token_record.expires_at:
        db.delete(reset_token_record) # Clean up expired token
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Find the user associated with the token
    user = db.query(User).filter(User.id == reset_token_record.user_id).first()
    if not user:
        # This case should ideally not happen if DB constraints are set
        db.delete(reset_token_record) 
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid token: User not found")

    # Optional: Add password strength check here if desired
    if len(payload.new_password) < 12: # Example basic check
         raise HTTPException(status_code=400, detail="Password does not meet complexity requirements.")
    
    # Update user's password
    user.password_hash = hash_password(payload.new_password)
    
    # Delete the used token
    db.delete(reset_token_record)
    
    db.commit()
    
    return {"message": "Password has been reset successfully."}


# --- End Password Reset ---

class GenerateRegistrationLinkRequest(BaseModel):
    email: EmailStr
    is_admin: bool
    base_url: str

@router.post("/admin/generate-registration-link")
def generate_registration_link(
    request: GenerateRegistrationLinkRequest,
    db: Session = Depends(get_admin_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a registration link for a new user."""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can generate registration links"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check if there's already a pending invite
    existing_invite = db.query(Invite).filter(Invite.email == request.email).first()
    if existing_invite:
        # Delete the existing invite
        db.delete(existing_invite)
        db.commit()
    
    # Generate a new invite token
    invite_token = str(uuid.uuid4())
    
    # Create new invite with the specified role
    invite = Invite(
        email=request.email,
        token=invite_token,
        expires_at=datetime.utcnow() + timedelta(hours=48),
        access_role="admin" if request.is_admin else "user"
    )
    
    db.add(invite)
    db.commit()
    
    # Generate the registration URL using the provided base_url
    registration_url = f"{request.base_url}/register?token={invite_token}"
    
    return {
        "token": invite_token,
        "registrationUrl": registration_url
    }

@router.get("/admin/invites")
def get_pending_invites(
    db: Session = Depends(get_admin_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending invites for unregistered emails."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view pending invites"
        )
    
    # Get all registered emails
    registered_emails = {user.email for user in db.query(User).all()}
    
    # Get all invites and filter out those for registered emails
    invites = db.query(Invite).all()
    pending_invites = [
        invite for invite in invites 
        if invite.email not in registered_emails and datetime.utcnow() < invite.expires_at
    ]

    
    return pending_invites