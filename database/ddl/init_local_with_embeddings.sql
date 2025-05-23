-- ✅ Connect to the default `postgres` database
\c postgres


-- ✅ Create two separate databases
CREATE DATABASE admin_db OWNER admin;
CREATE DATABASE chat_db OWNER admin;

-- ✅ Switch to `admin_db` and create tables
\c admin_db

-- Enable cryptographic functions for password hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ✅ Create a dedicated schema for admin users
CREATE SCHEMA IF NOT EXISTS admin AUTHORIZATION admin;

-- ✅ Set the default schema for new connections (optional)
ALTER ROLE admin SET search_path TO admin;

-- ✅ Secure the schema (prevent public access)
REVOKE ALL ON SCHEMA admin FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA admin TO admin;

-- ✅ Create Users table inside the admin schema
CREATE TABLE IF NOT EXISTS admin.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

-- ✅ Create Invites table inside the admin schema
CREATE TABLE IF NOT EXISTS admin.invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP NOT NULL,
    access_role TEXT 
);

-- ✅ Optimize storage for large text fields
ALTER TABLE admin.users ALTER COLUMN email SET STORAGE EXTERNAL;
ALTER TABLE admin.users ALTER COLUMN password_hash SET STORAGE EXTERNAL;
ALTER TABLE admin.invites ALTER COLUMN token SET STORAGE EXTERNAL;

-- ✅ Ensure only the admin role can access these tables
REVOKE ALL ON admin.users FROM PUBLIC;
REVOKE ALL ON admin.invites FROM PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON admin.users TO admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON admin.invites TO admin;

-- ✅ Insert an admin user (hashed password with Blowfish)
--INSERT INTO admin.users (email, password_hash, is_admin)
--VALUES ('matthewgorbett@gmail.com', crypt('SuperSecurePassword', gen_salt('bf')), TRUE)
--ON CONFLICT (email) DO NOTHING;

-- ✅ Switch to `chat_db` (no tables for now)
\c chat_db

-- ✅ Create a dedicated schema for future chat-related data
CREATE SCHEMA IF NOT EXISTS chat AUTHORIZATION admin;

-- ✅ Secure the schema (prevent public access)
REVOKE ALL ON SCHEMA chat FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA chat TO admin;


-- Chat table
    --user_id VARCHAR REFERENCES users(id),
CREATE TABLE chat.chats (
    chat_id VARCHAR PRIMARY KEY,

    user_id VARCHAR ,
    name VARCHAR NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE chat.messages (
    message_id VARCHAR PRIMARY KEY,
    chat_id VARCHAR REFERENCES chat.chats(chat_id),
    content TEXT NOT NULL,
    is_user BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);






















-- Create collections database
CREATE DATABASE collections_db OWNER admin;

\c collections_db

-- Create collections schema
CREATE SCHEMA IF NOT EXISTS collections AUTHORIZATION admin;
REVOKE ALL ON SCHEMA collections FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA collections TO admin;

-- First, set the search path to include public
SET search_path TO public, collections;

-- Then create the extension in the public schema
CREATE EXTENSION IF NOT EXISTS vector SCHEMA public;
CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA public;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA public;

-- Collections tables
CREATE TABLE collections.collections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collections.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    collection_id UUID NOT NULL REFERENCES collections.collections(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    size BIGINT NOT NULL,
    file_path TEXT NOT NULL,
    content_type TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    status TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks with vector embeddings
CREATE TABLE collections.document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES collections.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_documents_collection_id ON collections.documents(collection_id);
CREATE INDEX idx_document_chunks_document_id ON collections.document_chunks(document_id);
CREATE INDEX idx_collections_user_id ON collections.collections(user_id);

-- Create vector index for similarity searches
CREATE INDEX embedding_idx ON collections.document_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);