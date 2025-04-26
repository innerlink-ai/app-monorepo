from sqlalchemy import create_engine, Column, Integer, String, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URLs
ADMIN_DATABASE_URL = os.getenv('ADMIN_DATABASE_URL')
CHAT_DATABASE_URL = os.getenv('CHAT_DATABASE_URL')
COLLECTIONS_DATABASE_URL = os.getenv('COLLECTIONS_DATABASE_URL')



# Create engines
admin_engine = create_engine(ADMIN_DATABASE_URL, connect_args={})
SessionLocalAdmin = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

chat_engine = create_engine(CHAT_DATABASE_URL, connect_args={})
SessionLocalChat = sessionmaker(autocommit=False, autoflush=False, bind=chat_engine)

#collections_engine = create_engine(COLLECTIONS_DATABASE_URL, connect_args={})
#SessionLocalCollections = sessionmaker(autocommit=False, autoflush=False, bind=collections_engine)

# Create bases
AdminBase = declarative_base()
ChatBase = declarative_base()
CollectionsBase = declarative_base()

# Database session dependencies
def get_admin_db():
    db = SessionLocalAdmin()
    try:
        yield db
    finally:
        db.close()

def get_chat_db():
    db = SessionLocalChat()
    try:
        yield db
    finally:
        db.close()

