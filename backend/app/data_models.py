from sqlalchemy import Column, Integer, String, Text, func, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import AdminBase, ChatBase
import uuid



class User(AdminBase):
    __tablename__ = "users"
    __table_args__ = {"schema": "admin"}  # ✅ Store users in `admin` schema

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=True)  # Made optional
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)  # ✅ Admin or Standard User (True/False)
    created_at = Column(DateTime, default=func.now())




class Invite(AdminBase):
    __tablename__ = "invites"
    __table_args__ = {"schema": "admin"}


    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    access_role = Column(String, )

# Model for Password Reset Tokens
class PasswordResetToken(AdminBase):
    __tablename__ = 'password_reset_tokens'
    __table_args__ = {"schema": "admin"}  # Ensure this is also in the admin schema

    id = Column(Integer, primary_key=True)
    # Correctly reference the user ID in the admin schema
    user_id = Column(Integer, ForeignKey('admin.users.id'), nullable=False) 
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Relationship needs to know how to find the User model
    user = relationship("User", primaryjoin="PasswordResetToken.user_id == User.id")