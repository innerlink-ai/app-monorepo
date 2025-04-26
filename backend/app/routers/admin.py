from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from database import get_admin_db
from data_models import Invite, User
from utils.email import send_invite_email  # ✅ Refactored for both user & admin invites
from uuid import UUID
from common.curr_user import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text # Import text
from logger import get_logger


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from database import get_admin_db
from data_models import Invite, User
from utils.email import send_invite_email
from common.curr_user import get_current_user 
from pydantic import BaseModel, EmailStr



logger = get_logger("admin")

#EMAIL_DOMAIN_RESTRICTION='gmail.com'
EMAIL_DOMAIN_RESTRICTION=None

router = APIRouter()

# ✅ Define Pydantic schema for validation
class InviteRequest(BaseModel):
    email: EmailStr  # ✅ Ensures a valid email format
    is_admin: bool

@router.post("/admin/invite")
def invite_user(
    request: InviteRequest,  # ✅ Accepts JSON body as a validated Pydantic model
    db: Session = Depends(get_admin_db), 
    current_user: User = Depends(get_current_user)  # ✅ Validate JWT Token
):
    """Creates an invite token and sends an email invite for admin or user access."""

    # ✅ Only admins can invite users
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")


    # ✅ Validate email domain restriction
    if EMAIL_DOMAIN_RESTRICTION:
        email_domain = request.email.split("@")[-1]
        if email_domain != EMAIL_DOMAIN_RESTRICTION:
            raise HTTPException(
                status_code=400,
                detail=f"Only emails with the domain '{EMAIL_DOMAIN_RESTRICTION}' are allowed."
            )
    
    # ✅ Check if an invite already exists
    existing_invite = db.query(Invite).filter_by(email=request.email).first()
    if existing_invite:
        raise HTTPException(status_code=400, detail="Invite already sent")

    # ✅ Generate unique token & expiration
    invite_token = str(uuid.uuid4())
    new_invite = Invite(
        email=request.email,
        token=invite_token,
        expires_at=datetime.utcnow() + timedelta(hours=48),  # ✅ Invite valid for 2 days
        access_role="admin" if request.is_admin else "user"
    )

    # ✅ Store invite in database
    db.add(new_invite)
    db.commit()
    # ✅ Send invite email
    send_invite_email(request.email, invite_token, request.is_admin)

    return {"message": "Invitation sent successfully"}


@router.get("/admin/users")
def list_users(
    db: Session = Depends(get_admin_db), 
    current_user: User = Depends(get_current_user) 
):
    """Returns a list of all users (only for authenticated users)."""

    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
        }
        for user in users
    ]





class InviteResponse(BaseModel):
    id: UUID
    email: str
    token: str
    created_at: datetime
    expires_at: datetime
    access_role: str  # "user" or "admin"

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy models


# Cleanup expired invites before returning results
def cleanup_expired_invites(db: Session):
    current_time = datetime.utcnow()
    db.query(Invite).filter(Invite.expires_at < current_time).delete(synchronize_session=False)
    db.commit()

@router.get("/admin/invites", response_model=list[InviteResponse])
def get_pending_invites(db: Session = Depends(get_admin_db)):
    """
    Fetch all pending invites where the expiration date is still valid.
    Also deletes any expired invites before returning results.
    """
    cleanup_expired_invites(db)  # Remove expired invites

    invites = db.query(Invite).filter(Invite.expires_at > datetime.utcnow()).all()
    return invites


@router.delete("/admin/invites/{invite_id}")
def delete_invite(invite_id: str, db: Session = Depends(get_admin_db)):
    """
    Manually delete an invite by ID.
    """
    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    db.delete(invite)
    db.commit()
    return {"message": "Invite deleted successfully"}


@router.post("/admin/reset-system", status_code=status.HTTP_200_OK)
async def reset_entire_system(
    db: Session = Depends(get_admin_db),
    current_user: User = Depends(get_current_user)
):
    """
    WARNING: Truncates all user, invite, key, audit, chat, and message data.
    Re-initializes encryption keys. Only callable by admins.
    """
    logger.warning(f"User {current_user.email} (ID: {current_user.id}) is attempting system reset.")

    if not current_user.is_admin:
        logger.error(f"Non-admin user {current_user.email} attempted system reset.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")

    try:
        logger.warning("Proceeding with system reset...")
        # Truncate all relevant tables in both schemas using the admin_db connection
        # Ensure the 'admin' role has TRUNCATE privileges on these tables/schemas
        truncate_sql = text("""
            TRUNCATE
                admin.users_encrypted,
                admin.invites_encrypted,
                admin.encryption_keys,
                admin.audit_log,
                chat.chats_encrypted,
                chat.messages_encrypted
            RESTART IDENTITY CASCADE;
        """)
        db.execute(truncate_sql)

        # Re-initialize encryption keys
        init_keys_sql = text("SELECT admin.initialize_encryption();")
        db.execute(init_keys_sql)

        db.commit()
        logger.info("System reset successful. All data truncated and encryption keys re-initialized.")
        return {"message": "System reset successfully. All data has been wiped."}

    except Exception as e:
        db.rollback()
        logger.exception(f"System reset failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"System reset failed: {e}")
