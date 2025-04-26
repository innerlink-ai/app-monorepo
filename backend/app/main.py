import sys
#p#rint("--- sys.path ---", sys.path) 
#sys.exit()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import chat, history, health, auth, admin, chat_history, projects
#, embeddings
from database import get_chat_db, get_admin_db
from db.init_admin import init_admin  # Import the initialization function
import asyncio
from contextlib import asynccontextmanager
import os
from sqlalchemy import text
from logger import get_logger

# Get logger for main module
logger = get_logger("main")

def init_collections_db():
    """Initialize the collections database with required tables and columns"""
    try:
        # Read and execute the init.sql script
        init_sql_path = os.path.join(os.path.dirname(__file__), 'db', 'ddl', 'init.sql')
        with open(init_sql_path, 'r') as f:
            init_sql = f.read()
        
        # Execute the SQL script
        with collections_engine.connect() as conn:
            conn.execute(text(init_sql))
            conn.commit()
            logger.info("Successfully initialized collections database")
    except Exception as e:
        logger.error(f"Error initializing collections database: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application initialization")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, get_admin_db)  # Initialize admin_db
    loop.run_in_executor(None, get_chat_db)   # Initialize chat_db
   
   
    #loop.run_in_executor(None, init_admin)  # Initialize admin user
    #loop.run_in_executor(None, get_collections_db)  # Initialize collections_db
    #loop.run_in_executor(None, init_collections_db)  # Initialize collections database
    logger.info("Application initialization completed")

    yield  # Execution continues after startup
    logger.info("Shutting down application")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan, root_path="/api")

# Define allowed origins for CORS
origins = [
    "http://localhost:5173",  # Vue frontend dev server
    "http://127.0.0.1:5173", # Also include loopback IP
    "http://innerlink.internal",  # Your custom internal domain without port
    "https://innerlink.internal",  # HTTPS version if needed
    # Add your production frontend URL here when deploying
    # e.g., "https://your-deployed-app.com"
]

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Use the specific list of origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Register API routers
app.include_router(auth.router, prefix="", tags=["Auth"])
app.include_router(chat.router, prefix="", tags=["Chat"])
app.include_router(history.router, prefix="", tags=["History"])
app.include_router(health.router, prefix="", tags=["Health"])
app.include_router(admin.router, prefix="", tags=["Admin"])
app.include_router(chat_history.router, prefix="", tags=["chat_history"])
app.include_router(projects.router, prefix="", tags=["Projects"])
#app.include_router(collections.router,prefix="", tags=["collections"])
#app.include_router(embeddings.router, prefix="", tags=["embeddings"])

if __name__ == "__main__":
    uvicorn.run(
        app,  # Runs the FastAPI app
        host="0.0.0.0",
        port=8000,
        workers=1,
        loop="uvloop" ,
        proxy_headers=False 
    )