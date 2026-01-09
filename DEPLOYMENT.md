# TrueTone - DEPLOYMENT


## Project Overview


**TrueTone** is a real-time emotion recognition application that uses machine learning to classify text sentiment into 6 emotion categories: anger, fear, joy, love, sadness, and surprise. The application consists of a React frontend and a FastAPI backend powered by a DistilRoBERTa model trained on the dair-ai/emotion dataset.


**GitHub Repository:** [https://github.com/darrengunawan15/TrueTone](https://github.com/darrengunawan15/TrueTone)

---


## Prerequisites


### For Local Development


- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **Docker Desktop** (for containerized local testing)
- **Git** installed and configured
- ~2GB RAM minimum for model inference


### For Azure Cloud Deployment


- **Azure Account** with active subscription
- **Azure CLI** installed: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- **Docker Desktop** installed
- **kubectl** (Kubernetes command-line tool): `az aks install-cli`
- **PowerShell 5.1+** (for running deployment scripts)


---


## Local Development Setup


### 1. Clone the Repository


```bash
git clone https://github.com/darrengunawan15/truetone.git
cd truetone
```


### 2. Backend Setup (Python)


```bash
# Create a virtual environment
python -m venv venv


# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```


**Dependencies Overview:**
- **FastAPI 0.109.0**: Web framework for building the REST API
- **Uvicorn 0.27.0**: ASGI server for running FastAPI
- **PyTorch 2.1.2**: Deep learning framework for model inference
- **Transformers 4.36.2**: Hugging Face library for loading pre-trained models
- **Accelerate**: Distributed model inference support
- **NumPy**: Numerical computing library


### 3. Frontend Setup (Node.js)


```bash
# Navigate to frontend directory
cd frontend


# Install Node dependencies
npm install


# Return to project root
cd ..
```


### 4. Run Backend Locally


```bash
# Make sure virtual environment is activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


Backend will be available at: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`


### 5. Run Frontend Locally


```bash
cd frontend
npm run dev
```


Frontend will be available at: `http://localhost:5173` (or the port shown in console)


### 6. Using Docker Compose (Alternative)


For a complete local environment with both services:


```bash
# Build and start all services
docker-compose up --build


# Frontend: http://localhost
# Backend: http://localhost:8000
```


Services will automatically connect. The frontend is configured to communicate with the backend on the same network.


---


## Cloud Deployment (Azure)


### Overview


TrueTone is deployed on **Microsoft Azure** using:
- **Azure Container Registry (ACR)**: Stores Docker images
- **Azure Kubernetes Service (AKS)**: Orchestrates containerized deployment
- **Azure Resource Group**: Manages all resources


**Cost Estimate (Student Plan):** ~$45-60/month (covered by $100 Azure student credit)


### Step 1: Set Up Azure Resources


```powershell
# Login to Azure
az login


# Create resource group
az group create --name truetone-rg --location eastus


# Create Azure Container Registry (Basic tier for cost efficiency)
az acr create `
  --resource-group truetone-rg `
  --name truetoneregistry `
  --sku Basic


# Retrieve ACR login server URL
$ACR_URL = az acr show --resource-group truetone-rg --name truetoneregistry --query loginServer -o tsv
Write-Host "ACR URL: $ACR_URL"
```


### Step 2: Build and Push Docker Images


```powershell
# Login to Azure Container Registry
az acr login --name truetoneregistry


# Set variables
$ACR_URL = "truetoneregistry.azurecr.io"
$REGISTRY = "truetoneregistry"


# Build and push backend image
az acr build `
  --registry $REGISTRY `
  --image truetone-backend:latest `
  .


# Build and push frontend image
az acr build `
  --registry $REGISTRY `
  --image truetone-frontend:latest `
  ./frontend
```


### Step 3: Create AKS Cluster


```powershell
# Create AKS cluster (may take 5-10 minutes)
# B1s VM SKU for cost optimization on student plan
az aks create `
  --resource-group truetone-rg `
  --name truetone-cluster `
  --node-count 1 `
  --vm-set-type VirtualMachineScaleSets `
  --load-balancer-sku standard `
  --enable-managed-identity `
  --network-plugin azure `
  --network-policy azure `
  --docker-bridge-address 172.17.0.1/16 `
  --service-cidr 10.0.0.0/16 `
  --dns-service-ip 10.0.0.10


# Get cluster credentials
az aks get-credentials `
  --resource-group truetone-rg `
  --name truetone-cluster


# Verify connection
kubectl cluster-info
```


### Step 4: Attach ACR to AKS


```powershell
# Enable AKS to pull images from ACR
az aks update `
  --name truetone-cluster `
  --resource-group truetone-rg `
  --attach-acr truetoneregistry
```


### Step 5: Configure Kubernetes Manifests


Update the ACR URL in Kubernetes deployment files:


```powershell
$ACR_URL = "truetoneregistry.azurecr.io"


# Update backend deployment
(Get-Content kubernetes/backend-deployment.yml) -replace 'YOUR_REGISTRY', $ACR_URL | Set-Content kubernetes/backend-deployment.yml


# Update frontend deployment
(Get-Content kubernetes/frontend-deployment.yml) -replace 'YOUR_REGISTRY', $ACR_URL | Set-Content kubernetes/frontend-deployment.yml
```


### Step 6: Deploy to AKS


```powershell
# Create namespace
kubectl apply -f kubernetes/namespace.yml


# Deploy backend and frontend
kubectl apply -f kubernetes/backend-deployment.yml
kubectl apply -f kubernetes/frontend-deployment.yml


# Check deployment status
kubectl get pods -n truetone
kubectl get svc -n truetone


# Wait for LoadBalancer external IP (this may take a few minutes)
kubectl get svc truetone-frontend -n truetone -w


# Once the external IP is assigned, access the app at:
# http://<EXTERNAL_IP>
```


### Step 7: Monitor Deployments

```powershell
# View pod logs
kubectl logs -n truetone -l app=truetone-backend --tail=100


# View all resources
kubectl get all -n truetone


# Describe a deployment for debugging
kubectl describe deployment truetone-backend -n truetone


# Scale replicas (for load balancing)
kubectl scale deployment truetone-backend -n truetone --replicas=3
```
