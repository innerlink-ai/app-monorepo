# Innerlink Application Monorepo

This monorepo contains all the code for the Innerlink AI application, a secure enterprise AI platform. It is structured to manage different components of the application, including the frontend, backend, database, and embedding worker services, facilitating a cohesive development and deployment process.

Current tech stack:
- Python, FastAPI for app-monorepo/backend
- PostGres for app-monorepo/database
- Vue for app-monorepo/frontend
- TGI for model inference
- docker-compose to test services/containers locally
- terraform to deploy to cloud provider 
- k3s to run full stack of services in the cloud.  
- helm to deploy full stack to the cloud. 


## Project Structure
The monorepo is organized into the following main directories.  Each bullet has its own container which runs in a k3s application (see helm-charts repository):

*   `frontend/`: Built with **Vue.js**. Contains all the UI code that runs in the browser, handles user interactions, and communicates with the backend API.

*   `backend/`: Built with **Python** and **FastAPI**. Handles all server-side logic including API endpoints, business logic, database operations, and user authentication.

*   `database/`: Contains everything related to our **PostgreSQL** database - schema definitions, migration scripts, and database setup configs. Stores user data, chat history, documents, and application state.

*   `embedding-worker/`: A separate service that handles resource-intensive document processing tasks. This keeps the main API responsive by offloading heavy computational work.

*   `docker-compose.yaml`: Sets up our local development environment. Configures and connects all services (frontend, backend, database, workers) using Docker containers. Includes all the necessary ports, volumes, and environment variables.


---

Local Development and Debugging: 
```
# S1. tart docker locally
# 2. Start postgres:
docker-compose up  --build postgres

#Start Frontend (Terminal 1):
cd app-monorepo/frontend
npm run dev

#Start Backend (Terminal 2):
cd app-monorepo/backend/app
source activate backend
source set_local.sh #should be same as vars set in docker-compose.yml
bash scripts/start-script.sh localhost 5432


 Access frontend at  http://localhost:5173/

```






#Remove images, containers, and volumes
```
To delete databases and running services locally:
docker-compose down --volumes --remove-orphans
docker volume rm -f postgres_data
docker container stop $(docker container ls -aq)
docker container rm $(docker container ls -aq)
docker image rm -f $(docker image ls -aq)
docker volume rm $(docker volume ls -q)
docker system prune -a --volumes
docker system prune -a --volumes -f
```



