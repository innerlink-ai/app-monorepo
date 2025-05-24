# Innerlink Application Monorepo

This monorepo contains all the code for the Innerlink application, a secure enterprise AI platform. It is structured to manage different components of the application, including the frontend, backend, database, and embedding worker services, facilitating a cohesive development and deployment process.

## Project Structure

The monorepo is organized into the following main directories, each playing a distinct role in the application:

*   `frontend/`: This directory contains the complete user interface (UI) code. It is built using **Vue.js**, a progressive JavaScript framework. The frontend is responsible for rendering the application in the user's web browser, managing user interactions, and communicating with the backend via API calls to fetch and display data, as well as to trigger backend operations.

*   `backend/`: Houses the server-side logic, API endpoints, and core application functionality. Developed using **Python** with the **FastAPI** framework, the backend manages business logic, processes data, interacts with the PostgreSQL database, handles user authentication and authorization, and serves data to the frontend. It also likely interfaces with the AI model inference services (e.g., TGI - Text Generation Inference).

*   `database/`: This directory includes all resources related to data persistence. It contains schema definitions for the **PostgreSQL** database, migration scripts (if used) to manage database schema changes over time, and potentially Docker configurations specifically for setting up and running the database service. The database stores critical information such as user accounts, chat histories, uploaded documents, metadata, and application state.

*   `embedding-worker/`: This crucial component contains a dedicated service for handling computationally intensive tasks related to generating vector embeddings. For an AI platform like Innerlink, this worker would process documents uploaded by users to convert them into embeddings for Retrieval Augmented Generation (RAG) and generate embeddings for user queries to enable semantic search capabilities. This separation ensures that these intensive tasks do not block the main backend API.

*   `docker-compose.yaml`: This file defines and configures the multi-container Docker application for local development and testing. It orchestrates the startup and networking of all the services (frontend, backend, database, embedding worker, and any other dependencies like Redis cache), ensuring a consistent and easily reproducible development environment. It specifies container images, ports, volumes, and environment variables.


---

Local Development: 
```
#First start docker locally
#Start DB and Redis Cache (Terminal 1):
docker-compose up  --build postgres

#Start Frontend (Terminal 1):
cd app-monorepo/frontend
npm run dev

#Start Backend (Terminal 2):
cd app-monorepo/backend/app
source activate backend
source set_local.sh #should be same as vars set in docker-compose.yml
bash scripts/start-script.sh localhost 5432


#access at  http://localhost:5173/
```






Current tech stack:
- Python, FastAPI for backend services, api, 
- TGI for backend
- PostGres for database
- Vue for frontend
- docker-compose to test services/containers locally
- terraform to deploy to cloud provider
- k3s to run full stack of services in the cloud.  
- helm to deploy full stack to the cloud. 





To delete databases and running services:
docker-compose down --volumes --remove-orphans
docker volume rm -f postgres_data








#### Build images and push to GHCR
```
docker login ghcr.io -u mattgorb -p password
docker login ghcr.io -u mattgorb -p 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


export PROJECT_NAME=innerlink
docker build --no-cache  --platform linux/amd64 -t ghcr.io/innerlink-ai/${PROJECT_NAME}-frontend:latest ./app-monorepo/frontend
docker push ghcr.io/innerlink-ai/${PROJECT_NAME}-frontend:latest

export PROJECT_NAME=innerlink
cd app-monorepo/backend
docker build --no-cache --platform linux/amd64 -t ghcr.io/innerlink-ai/${PROJECT_NAME}-backend:latest -f Dockerfile.gpu .
docker push ghcr.io/innerlink-ai/${PROJECT_NAME}-backend:latest


#cd app/embedding-worker
#docker build --no-cache --platform linux/amd64 -t ghcr.io/mattgorb/${PROJECT_NAME}-embedding-worker:latest -f Dockerfile.embedding_worker .
#docker push ghcr.io/mattgorb/${PROJECT_NAME}-embedding-worker:latest


```

#Remove images, containers, and volumes
```
docker container stop $(docker container ls -aq)
docker container rm $(docker container ls -aq)
docker image rm -f $(docker image ls -aq)
docker volume rm $(docker volume ls -q)
docker system prune -a --volumes
docker system prune -a --volumes -f
```




aws ssm start-session --target i-09848ee4ef03942c3
bash upload-via-ssm.sh innerlink/innerlink-chart  i-0a3c89c1090aad70e




!!!!!!!ADD THIS TO AMI. 
# Create directory for certificates
mkdir -p /Users/matthewgorbett/postgres-certs
# Generate private key
openssl genrsa -out /Users/matthewgorbett/postgres-certs/server.key 2048
# Make key file only readable by owner
chmod 600 /Users/matthewgorbett/postgres-certs/server.key
# Generate self-signed certificate
openssl req -new -x509 -days 365 -key /Users/matthewgorbett/postgres-certs/server.key -out /Users/matthewgorbett/postgres-certs/server.crt -subj "/CN=postgres"


#### On instance: 
export KUBECONFIG=$HOME/.kube/config
kubectl get nodes
