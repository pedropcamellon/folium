# Azure Infrastructure Specification

## Overview

Azure hosts the main SouthDrift application backend using App Service, Blob Storage, and Application Insights.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Resource Group                          │
│              rg-south-drift-{environment}                  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         App Service Plan (Linux F1)                  │ │
│  │           asp-south-drift-{env}                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         App Service (Linux)                          │ │
│  │      app-south-drift-backend-{env}                   │ │
│  │                                                      │ │
│  │  Runtime: .NET 6.0 / .NET 8.0                       │ │
│  │  Container: ASP.NET Core backend                    │ │
│  │  CORS: Frontend URLs configured                     │ │
│  │  HTTPS: Enforced                                    │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          │ Telemetry                       │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │      Application Insights                            │ │
│  │    appi-south-drift-{env}                            │ │
│  │                                                      │ │
│  │  - Request tracking                                  │ │
│  │  - Exception logging                                 │ │
│  │  - Performance metrics                               │ │
│  │  - Custom events                                     │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘

External Access:
┌──────────────┐                                              
│   Frontend   │                                              
│  (Next.js)   │──────HTTP/HTTPS──────▶ App Service          
└──────────────┘                         (Backend API)        
```

## Resources

### Resource Group

- **Name**: `rg-south-drift-{environment}`
- **Location**: East US (default)
- **Purpose**: Container for all Azure resources
- **Tags**: environment, project, managed-by

### App Service Plan

- **Name**: `asp-south-drift-{environment}`
- **SKU**: F1 (Free tier)
  - 1 GB RAM
  - 60 CPU minutes/day
  - 1 GB storage
  - No auto-scaling
- **OS**: Linux
- **Purpose**: Hosting backend API

### App Service (Backend API)

- **Name**: `app-south-drift-backend-{environment}`
- **Runtime**: .NET 6.0 or .NET 8.0
- **Deployment**: Docker container (recommended) or zip deploy
- **Endpoints**:
  - `/api/v1/patients` - Patient management
  - `/api/v1/interactions` - Clinical interactions
  - `/api/v1/documents` - Document management
  - `/api/v1/dashboard` - Dashboard metrics
  - `/swagger` - API documentation (dev only)

**Environment Variables**:

```bash
ASPNETCORE_ENVIRONMENT=Production
APPLICATIONINSIGHTS_CONNECTION_STRING=<from_terraform_output>
SUMMARIZATION_SERVICE_URL=http://summarize:8002
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Application Insights

- **Name**: `appi-south-drift-{environment}`
- **Type**: Workspace-based
- **Retention**: 90 days (default)
- **Purpose**: Monitoring, logging, telemetry

**Key Metrics**:

- Request rate and response times
- Failed request percentage
- Server response time (avg, p95, p99)
- Exception count
- Custom events (patient interactions, summarizations)

## Monitoring

### Application Insights Queries

**Request Performance**:

```kql
requests
| where timestamp > ago(1h)
| summarize 
    count=count(),
    avg_duration=avg(duration),
    p95_duration=percentile(duration, 95)
  by name
| order by count desc
```

**Failed Requests**:

```kql
requests
| where timestamp > ago(1h) and success == false
| project timestamp, name, resultCode, duration
| order by timestamp desc
```

## Cost Management

### Tiers

- **F1 (Free)**: $0/month - Development only
- **B1 (Basic)**: ~$13/month - Staging, low-traffic
- **S1 (Standard)**: ~$70/month - Production, auto-scaling

### Tips

- Use F1 for development
- Monitor Application Insights usage (1 GB/month free)
- Set budget alerts at 80% and 100%

## Troubleshooting

### App Service Not Starting

```powershell
az webapp log tail `
  --name app-south-drift-backend-dev `
  --resource-group rg-south-drift-dev
```

Common issues: Missing environment variables, port binding, CPU quota exceeded

### State File Issues

```powershell
terraform force-unlock <lock-id>
terraform refresh
```
