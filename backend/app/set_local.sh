
# Uncomment the following line if you want to restrict email domains
# export EMAIL_DOMAIN_RESTRICTION="gmail.com"
export DOMAIN="localhost:5173"
export LLM="gpt2"  # You can change this to another model, e.g., "microsoft/phi-1_5"
export ADMIN_DATABASE_URL="postgresql://admin:SuperSecurePassword@localhost:5432/admin_db"
export CHAT_DATABASE_URL="postgresql://admin:SuperSecurePassword@localhost:5432/admin_db"
export COLLECTIONS_DATABASE_URL="postgresql://admin:SuperSecurePassword@localhost:5432/collections_db"
export DATA_DIR="$HOME/data"
export EMBEDDING_DIMENSION='768'
export LOG_LEVEL='DEBUG'
export EMBEDDING_MODEL_NAME="intfloat/multilingual-e5-base"
export EMBEDDING_CACHE_SIZE="1"
export EMBEDDING_DIMENSION="768"
export VECTORDB_K="3"
export REDIS_URL="redis://localhost:6379/0"
export USE_CPU='true'