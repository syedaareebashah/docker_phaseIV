# PowerShell script to deploy the Todo AI Chatbot System to Minikube

Write-Host "🚀 Starting deployment of Todo AI Chatbot System to Minikube..." -ForegroundColor Green

# Check if minikube is running
try {
    $minikubeStatus = minikube status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Minikube is already running" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Minikube is not running. Starting minikube..." -ForegroundColor Red
    minikube start
}

# Enable ingress addon
Write-Host "🔧 Enabling ingress addon..." -ForegroundColor Yellow
minikube addons enable ingress

# Set Docker environment to use Minikube's Docker daemon
Write-Host "🐳 Setting Docker environment to Minikube..." -ForegroundColor Yellow
minikube docker-env | Invoke-Expression

# Build backend Docker image
Write-Host "🏗️ Building backend Docker image..." -ForegroundColor Yellow
docker build -t hackathon-backend:latest . -f Dockerfile

# Build frontend Docker image
Write-Host "🏗️ Building frontend Docker image..." -ForegroundColor Yellow
Set-Location frontend
docker build -t hackathon-frontend:latest . -f Dockerfile
Set-Location ..

Write-Host "✅ Docker images built successfully!" -ForegroundColor Green

# Update the frontend service URL in values.yaml to point to the backend service in the cluster
Write-Host "📝 Updating values.yaml to use correct backend service URL..." -ForegroundColor Yellow
(Get-Content todo-chatbot/values.yaml) -replace 'NEXT_PUBLIC_API_URL: "http://localhost:8000"', 'NEXT_PUBLIC_API_URL: "http://todo-chatbot-backend:8000"' | Set-Content todo-chatbot/values.yaml

# Deploy using Helm
Write-Host "🚢 Deploying application using Helm..." -ForegroundColor Yellow
helm upgrade --install todo-chatbot ./todo-chatbot --namespace todo-app --create-namespace

# Wait for deployments to be ready
Write-Host "⏳ Waiting for deployments to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-backend --timeout=300s -n todo-app
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-frontend --timeout=300s -n todo-app
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-postgres --timeout=300s -n todo-app
kubectl wait --for=condition=Ready pods -l app=todo-chatbot-redis --timeout=300s -n todo-app

# Get the Minikube IP
$minikubeIP = minikube ip
Write-Host "🌐 Application will be accessible at: http://$minikubeIP" -ForegroundColor Cyan

# Display deployment status
Write-Host "" -ForegroundColor White
Write-Host "📋 Deployment Status:" -ForegroundColor White
kubectl get pods,svc,ingress -n todo-app

Write-Host "" -ForegroundColor White
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "💡 Access your Todo AI Chatbot System at: http://$minikubeIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 To access the application logs:" -ForegroundColor Yellow
Write-Host "   kubectl logs -f -l app=todo-chatbot-backend -n todo-app" 
Write-Host "   kubectl logs -f -l app=todo-chatbot-frontend -n todo-app" 
Write-Host ""
Write-Host "🧹 To cleanup later:" -ForegroundColor Yellow
Write-Host "   helm uninstall todo-chatbot -n todo-app" 
Write-Host "   minikube delete" 