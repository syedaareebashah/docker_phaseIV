# Todo Chatbot Helm Chart

This Helm chart deploys the complete Todo Chatbot application with frontend, backend, PostgreSQL, and Redis for local development.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Minikube (for local development)
- Docker (to build images)

## Local Setup Instructions

### 1. Build the Images

First, build the frontend and backend Docker images:

```bash
# Build the backend image
cd backend
docker build -t hackathon-backend:latest .
cd ..

# Build the frontend image
cd frontend
docker build -t hackathon-frontend:latest .
cd ..
```

### 2. Load Images into Minikube

```bash
# Make sure minikube is running
minikube start

# Load the images into minikube
minikube image load hackathon-backend:latest
minikube image load hackathon-frontend:latest
```

### 3. Install the Chart

```bash
# Navigate to the todo-chatbot directory
cd todo-chatbot

# Install the chart
helm install todo-chatbot-release . --namespace default --create-namespace
```

### 4. Access the Application

Once deployed, you can access the application in one of these ways:

#### Option 1: Using Port Forwarding
```bash
# Forward frontend port
kubectl port-forward svc/todo-chatbot-frontend 3000:3000

# Forward backend port
kubectl port-forward svc/todo-chatbot-backend 8000:8000
```

Then access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

#### Option 2: Using Ingress (Recommended)
Enable the ingress addon in minikube:
```bash
minikube addons enable ingress
```

Run minikube tunnel in a separate terminal:
```bash
minikube tunnel
```

Then access the application at: http://localhost

## Configuration

The following table lists the configurable parameters of the todo-chatbot chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Number of backend pods | `1` |
| `backend.image.repository` | Backend image repository | `"hackathon-backend"` |
| `backend.image.tag` | Backend image tag | `"latest"` |
| `backend.image.pullPolicy` | Backend image pull policy | `"Never"` |
| `backend.service.port` | Backend service port | `8000` |
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Number of frontend pods | `1` |
| `frontend.image.repository` | Frontend image repository | `"hackathon-frontend"` |
| `frontend.image.tag` | Frontend image tag | `"latest"` |
| `frontend.image.pullPolicy` | Frontend image pull policy | `"Never"` |
| `frontend.service.port` | Frontend service port | `3000` |
| `postgresql.enabled` | Enable PostgreSQL deployment | `true` |
| `postgresql.image.repository` | PostgreSQL image repository | `"postgres"` |
| `postgresql.image.tag` | PostgreSQL image tag | `"15-alpine"` |
| `postgresql.service.port` | PostgreSQL service port | `5432` |
| `redis.enabled` | Enable Redis deployment | `true` |
| `redis.image.repository` | Redis image repository | `"redis"` |
| `redis.image.tag` | Redis image tag | `"7-alpine"` |
| `redis.service.port` | Redis service port | `6379` |
| `ingress.enabled` | Enable ingress | `true` |

## Custom Values

To customize the deployment, create a custom `values.yaml` file and use it during installation:

```bash
helm install todo-chatbot-release . -f custom-values.yaml --namespace default --create-namespace
```

## Uninstalling the Chart

To uninstall/delete the `todo-chatbot-release` deployment:

```bash
helm delete todo-chatbot-release --namespace default
```

## Troubleshooting

### Common Issues

1. **Images not found**: Make sure you've built and loaded the images into minikube
2. **Services not accessible**: Check if the pods are running with `kubectl get pods`
3. **Database connection errors**: Verify that PostgreSQL is running and accessible

### Useful Commands

```bash
# Check pod status
kubectl get pods

# Check service status
kubectl get svc

# Check logs for backend
kubectl logs -l app=todo-chatbot-backend

# Check logs for frontend
kubectl logs -l app=todo-chatbot-frontend
```