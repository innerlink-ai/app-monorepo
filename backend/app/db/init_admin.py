from sqlalchemy.orm import Session
from database import get_admin_db
from data_models import Invite, User
import uuid
from datetime import datetime, timedelta
from utils.email import send_invite_email
import os

def init_admin():
    db = next(get_admin_db())
    env_email=os.getenv('INITIAL_USER_EMAIL')
    # Check if an admin invite already exists
    existing_invite = db.query(Invite).filter_by(email=env_email).first()
    existing_user = db.query(User).filter_by(email=env_email).first()
    if not existing_user and not existing_invite:
        invite_token = str(uuid.uuid4())
        new_invite = Invite(
            email=env_email,
            token=invite_token,
            expires_at=datetime.utcnow() + timedelta(hours=48), 
            access_role='admin'
        )
        db.add(new_invite)
        db.commit()
        send_invite_email(email=env_email, token=invite_token,is_admin=True )