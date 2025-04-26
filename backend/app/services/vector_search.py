'''
import os
import asyncio
import numpy as np
import torch
from sqlalchemy import text
from sqlalchemy.orm import Session
from functools import lru_cache
import traceback
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer, AutoModel

# Change to absolute imports
from database import get_collections_db
from logger import get_logger

logger = get_logger("vector_search")

# =============== Environment Variables ===============
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-base")
EMBEDDING_CACHE_SIZE = int(os.getenv("EMBEDDING_CACHE_SIZE", "1"))
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
VECTORDB_K = int(os.getenv("VECTORDB_K", "2"))

# =============== Initialization Functions ===============
async def initialize_vector_search():
    """Initialize necessary components for vector search"""
    logger.info("Initializing vector search service components...")
    try:
        # Get database connection
        db_generator = get_collections_db()
        db = next(db_generator)
        try:
            # Ensure pgvector extension is available
            success = await ensure_pgvector_extension(db)
            if success:
                logger.info("Successfully initialized pgvector extension")
            else:
                logger.error("Failed to initialize pgvector extension")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during vector search initialization: {e}")
        logger.error(traceback.format_exc())
        # Don't raise the exception - let the application start anyway
        # but log the error for investigation

# =============== Embedding Functions ===============
@lru_cache(maxsize=EMBEDDING_CACHE_SIZE)
def get_embedding_model():
    """Load and cache the embedding model"""
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)
    model = AutoModel.from_pretrained(EMBEDDING_MODEL_NAME)
    if torch.cuda.is_available():
        model = model.to("cuda")
        logger.info("Using GPU for embeddings")
    else:
        logger.info("Using CPU for embeddings")
    return tokenizer, model

async def generate_embedding(text):
    """Generate embedding for text using the loaded model"""
    logger.debug(f"Generating embedding for text of length: {len(text)}")

    if not text or not text.strip():
        logger.warning("Empty text provided for embedding generation")
        return []

    # If CUDA is not available, return random embedding for testing
    if not torch.cuda.is_available():
        logger.debug("GPU not available, generating random embedding for simulation")
        # Generate random embedding with the same dimension as the model
        random_embedding = np.random.normal(0, 0.1, EMBEDDING_DIMENSION).astype(np.float32)
        # Simulate processing time
        await asyncio.sleep(0.5)
        return random_embedding.tolist()

    # If CUDA is available, use the actual model
    tokenizer, model = get_embedding_model()

    # Tokenize and prepare for model
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)

    # Move to GPU
    inputs = {k: v.to("cuda") for k, v in inputs.items()}

    # Generate embeddings
    with torch.no_grad():
        outputs = model(**inputs)
        # Use mean pooling to get a single vector
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

        # Handle case where outputs is single dimension
        if len(embeddings.shape) == 1:
            return embeddings.tolist()
        else:
            return embeddings[0].tolist()

async def ensure_pgvector_extension(db: Session):
    """Ensure pgvector extension is created and available"""
    try:
        # Set search path to include both schemas
        db.execute(text("SET search_path TO public, collections"))
        db.commit()

        # First check if extension exists
        result = db.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'")).fetchone()
        if not result:
            logger.info("Creating pgvector extension...")
            db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            db.commit()
            logger.info("pgvector extension created successfully")
        else:
            logger.info("pgvector extension already exists")

        # Now ensure the vector type is available in the collections schema
        db.execute(text("SET search_path TO collections,public"))
        db.commit()
        logger.info("Set search path to collections schema")

        return True
    except Exception as e:
        logger.error(f"Error setting up pgvector extension: {e}")
        logger.error(traceback.format_exc())
        return False

async def retrieve_collection_context(collection_id: str, query_text: str, limit: int = VECTORDB_K):
    """
    Retrieve relevant chunks from a collection based on similarity to the query
    """
    try:
        # Generate embedding for the query text
        logger.debug(f"Generating embedding for query: {query_text[:100]}...")
        query_embedding = await generate_embedding(query_text)

        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return ""

        # Log embedding dimension for debugging
        embedding_dimension = len(query_embedding)
        logger.debug(f"Generated embedding with dimension: {embedding_dimension}")

        # Get database connection - Consuming the generator properly
        db_generator = get_collections_db()
        db = next(db_generator)

        try:
            # Convert embedding to text for SQL
            embedding_str = str(query_embedding)
            # Query for similar chunks
            logger.debug(f"Querying for chunks in collection {collection_id} similar to prompt")

            # Check if embeddings exist for this collection
            check_sql = text("""
                SELECT COUNT(*)
                FROM collections.document_chunks dc
                JOIN collections.documents d ON dc.document_id = d.id
                WHERE d.collection_id = :collection_id
                AND dc.embedding IS NOT NULL
            """)

            embedding_count = db.execute(check_sql, {"collection_id": str(collection_id)}).scalar()
            logger.debug(f"Found {embedding_count} document chunks with embeddings in collection {collection_id}")

            if embedding_count == 0:
                logger.warning(f"No document chunks with embeddings found in collection {collection_id}")
                return f"Note: Collection {collection_id} has no embedded document chunks yet."

            # SQL for vector similarity search
            search_sql = text("""
                SET search_path TO collections, public;

                SELECT
                    dc.chunk_text,
                    dc.chunk_index,
                    d.name as document_name,
                    d.id as document_id,
                    c.name as collection_name,
                    c.id as collection_id,
                    1 - (dc.embedding <=> (:embedding)::vector) as similarity
                FROM
                    collections.document_chunks dc
                JOIN
                    collections.documents d ON dc.document_id = d.id
                JOIN
                    collections.collections c ON d.collection_id = c.id
                WHERE
                    c.id = :collection_id
                    AND dc.embedding IS NOT NULL
                ORDER BY
                    dc.embedding <=> (:embedding)::vector
                LIMIT :limit
            """)

            # Execute similarity search query
            result = db.execute(
                search_sql,
                {
                    "embedding": embedding_str,
                    "collection_id": str(collection_id),
                    "limit": limit
                }
            ).fetchall()

            # If no results, return empty string
            if not result:
                logger.warning(f"No similar chunks found for collection {collection_id}")
                return ""

            # Format results
            logger.debug(f"Found {len(result)} similar chunks in collection {collection_id}")

            chunks_text = []
            for row in result:
                chunk_text = row.chunk_text
                doc_name = row.document_name
                similarity = row.similarity

                # Add formatted chunk with document name and similarity score
                logger.debug(f"Chunk from '{doc_name}' with similarity score: {similarity:.4f}")
                chunks_text.append(f"Document: {doc_name}\nSimilarity: {similarity:.4f}\nText: {chunk_text}\n")

            # Combine all chunks
            context = "Context:\n" + "\n".join(chunks_text)

            return context

        except Exception as e:
            if "different column dimensions" in str(e).lower():
                logger.error(f"Vector dimension mismatch. Query vector dimension: {len(query_embedding)}")
                return "Error: Vector dimension mismatch between query and stored embeddings."
            logger.error(f"Error during vector similarity search: {str(e)}")
            return "Error: Unable to perform similarity search."

        finally:
            # Properly close the database connection
            db.close()

    except Exception as e:
        logger.error(f"Error retrieving collection context: {str(e)}")
        return "Error: Unable to retrieve context from collection." 
'''