Local Development: 
```
#First start docker locally
#Start DB and Redis Cache (Terminal 1):
docker-compose up  --build postgres
 pgadmin embedding-worker

#Start Frontend (Terminal 1):
cd app/frontend
npm run dev

#Start Backend (Terminal 2):
cd app/backend/app
source activate backend
source set_local.sh #should be same as vars set in docker-compose.yml
bash scripts/start-script.sh localhost 5432

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
docker build --no-cache  --platform linux/amd64 -t ghcr.io/mattgorb/${PROJECT_NAME}-frontend:latest ./app/frontend
docker push ghcr.io/mattgorb/${PROJECT_NAME}-frontend:latest


cd app/backend
docker build --no-cache --platform linux/amd64 -t ghcr.io/mattgorb/${PROJECT_NAME}-backend:latest -f Dockerfile.gpu .
docker push ghcr.io/mattgorb/${PROJECT_NAME}-backend:latest


cd app/embedding-worker
docker build --no-cache --platform linux/amd64 -t ghcr.io/mattgorb/${PROJECT_NAME}-embedding-worker:latest -f Dockerfile.embedding_worker .
docker push ghcr.io/mattgorb/${PROJECT_NAME}-embedding-worker:latest


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
