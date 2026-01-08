# TrueTone Deployment Guide

## Prerequisites
- Azure account with student credits
- Azure CLI installed: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- Docker Desktop installed
- kubectl installed: `az aks install-cli`

---

## Step 1: Test Locally with Docker Compose

```powershell
cd c:\Users\viona\OneDrive\Desktop\Uni\TrueTone

# Build and run locally
docker-compose up --build

# Test the app
# Frontend: http://localhost
# Backend: http://localhost:8000
```

---

## Step 2: Set Up Azure Resources

```powershell
# Login to Azure
az login

# Create resource group
az group create --name truetone-rg --location eastus

# Create Azure Container Registry (ACR)
az acr create `
  --resource-group truetone-rg `
  --name truetoneregistry `
  --sku Basic

# Get ACR login server
$ACR_URL = az acr show --resource-group truetone-rg --name truetoneregistry --query loginServer -o tsv
Write-Host "ACR URL: $ACR_URL"
```

---

## Step 3: Build and Push Docker Images

```powershell
# Login to ACR
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

---

## Step 4: Create AKS Cluster

```powershell
# Create AKS cluster (may take 5-10 minutes)
# Using B1s VM for cost efficiency on student plan
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

---

## Step 5: Attach ACR to AKS

```powershell
# Attach ACR to AKS
az aks update `
  --name truetone-cluster `
  --resource-group truetone-rg `
  --attach-acr truetoneregistry
```

---

## Step 6: Update Kubernetes Manifests

Edit the following files and replace `YOUR_REGISTRY` with your ACR login server:

- [kubernetes/backend-deployment.yml](kubernetes/backend-deployment.yml#L14)
- [kubernetes/frontend-deployment.yml](kubernetes/frontend-deployment.yml#L14)

Example:
```powershell
# Replace YOUR_REGISTRY with your ACR URL
$ACR_URL = "truetoneregistry.azurecr.io"

# Update manifests
(Get-Content kubernetes/backend-deployment.yml) -replace 'YOUR_REGISTRY', $ACR_URL | Set-Content kubernetes/backend-deployment.yml
(Get-Content kubernetes/frontend-deployment.yml) -replace 'YOUR_REGISTRY', $ACR_URL | Set-Content kubernetes/frontend-deployment.yml
```

---

## Step 7: Deploy to AKS

```powershell
# Create namespace and deploy
kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/backend-deployment.yml
kubectl apply -f kubernetes/frontend-deployment.yml

# Check deployment status
kubectl get pods -n truetone
kubectl get svc -n truetone

# Wait for LoadBalancer external IP
kubectl get svc truetone-frontend -n truetone -w

# Once external IP appears, access your app at: http://<EXTERNAL_IP>
```

---

## Step 8: Monitoring & Logs

```powershell
# View pod logs
kubectl logs -n truetone -l app=truetone-backend --tail=100

# View all resources in namespace
kubectl get all -n truetone

# Describe a deployment
kubectl describe deployment truetone-backend -n truetone

# Scale replicas
kubectl scale deployment truetone-backend -n truetone --replicas=3
```

---

## Cost Estimation (Student Plan)

| Resource | Monthly Cost (Est.) |
|----------|-------------------|
| AKS Cluster (1 node, B1s) | ~$30-40 |
| ACR (Basic) | ~$5 |
| Public IP | ~$3 |
| Data Transfer | ~$5-10 |
| **Total** | **~$45-60** |

✅ **Covered by $100 Azure student credit!**

---

## Troubleshooting

**Pod stuck in Pending:**
```powershell
kubectl describe pod <pod-name> -n truetone
```

**Image pull errors:**
```powershell
# Check ACR credentials
kubectl get secrets -n truetone
az aks update -n truetone-cluster -g truetone-rg --attach-acr truetoneregistry
```

**Check cluster status:**
```powershell
az aks show --resource-group truetone-rg --name truetone-cluster --query "agentPoolProfiles[0].provisioningState"
```

---

## Cleanup (Delete Resources)

```powershell
# Delete resource group (removes everything)
az group delete --name truetone-rg --yes --no-wait
```

---

## Next Steps

- Set up CI/CD with GitHub Actions
- Add HTTPS with cert-manager
- Enable auto-scaling with Horizontal Pod Autoscaler
- Add persistent storage for model files
