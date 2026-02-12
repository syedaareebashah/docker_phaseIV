#!/bin/bash

# Script to deploy the Todo AI Chatbot System to Minikube

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting deployment of Todo AI Chatbot System to Minikube..."

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Starting minikube..."
    minikube start
else
    echo "✅ Minikube is already running"
fi

# Enable ingress addon
echo "🔧 Enabling ingress addon..."
minikube addons enable ingress

# Set Docker environment to use Minikube's Docker daemon
echo "🐳 Setting Docker environment to Minikube..."
eval $(minikube docker-env)

# Build backend Docker image
echo "🏗️ Building backend Docker image..."
docker build -t hackathon-backend:latest . -f Dockerfile

# Build frontend Docker image
echo "🏗️ Building frontend Docker image..."
cd frontend
docker build -t hackathon-frontend:latest . -f Dockerfile
cd ..

echo "✅ Docker images built successfully!"

# Update the frontend service URL in values.yaml to point to the backend service in the cluster
echo "📝 Updating values.yaml to use correct backend service URL..."
sed -i.bak 's|NEXT_PUBLIC_API_URL: "http://localhost:8000"|NEXT_PUBLIC_API_URL: "http://todo-chatbot-backend:8000"|' todo-chatbot/values.yaml
rm todo-chatbot/values.yaml.bak

# Deploy using Helm
echo "🚢 Deploying application using Helm..."
helm upgrade --install todo-chatbot ./todo-chatbot --namespace todo-app --create-namespace

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-backend --timeout=300s -n todo-app
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-frontend --timeout=300s -n todo-app
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-postgres --timeout=300s -n todo-app
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-redis --timeout=300s -n todo-app

# Get the Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "🌐 Application will be accessible at: http://$MINIKUBE_IP"

# Display deployment status
echo ""
echo "📋 Deployment Status:"
kubectl get pods,svc,ingress -n todo-app

echo ""
echo "🎉 Deployment completed successfully!"
echo "💡 Access your Todo AI Chatbot System at: http://$MINIKUBE_IP"
echo ""
echo "🔧 To access the application logs:"
echo "   kubectl logs -f -l app=todo-chatbot-backend -n todo-app"
echo "   kubectl logs -f -l app=todo-chatbot-frontend -n todo-app"
echo ""
echo "🧹 To cleanup later:"
echo "   helm uninstall todo-chatbot -n todo-app"
echo "   minikube delete"