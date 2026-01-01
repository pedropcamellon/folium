
# SouthDrift: AI-Powered Clinical Documentation Platform

## Problem

Healthcare providers spend significant time on manual documentation—voice notes, visit summaries, lab result comments—that slows clinical workflow and wastes valuable practitioner time.

## Solution

SouthDrift is a SaaS platform that digitizes, analyzes, and automates clinical documentation through modular AI services:

- **Voice Note Processing:** Upload and process voice notes from physicians or medical assistants about patient visits, histories, or labs.
- **Automated Transcription & Summarization:** Calls are automatically transcribed and summarized using cloud AI models (e.g., AWS Lambda → Bedrock).
- **AI Clinical Insights:** Modules like lung nodule detection run asynchronously on patient imaging data, with results delivered to clinician dashboards.
- **Modular & Multi-Cloud:** Services run where they are most effective (e.g., AWS for transcription, Azure for imaging AI), integrated on a unified platform.
- **Secure & Compliant:** Role-based access, encrypted storage, and cloud logging support HIPAA readiness.

## Benefits

- Speeds documentation, allowing clinicians to focus more on patient care.
- Enhances diagnostic accuracy with AI-driven imaging insights.
- Centralizes data workflows in an easy-to-use web portal.
- Allows healthcare providers to scale without hiring additional admin staff.
- Enables incremental, modular adoption and scaling of AI features.

## 🏗️ Architecture

- **Frontend**: Next.js 15 with TypeScript → Vercel
- **Backend**: FastAPI (Python) → Azure Container Apps
- **AI Services**:
  - AWS Lambda + Bedrock for voice transcription
  - Azure Functions + Custom Vision for imaging analysis
- **Infrastructure**: Terraform
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- pnpm (frontend package manager)
- Docker (optional, for containerized development)
- Azure subscription (for deployment)
- Vercel account (for frontend deployment)

### Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/south-drift.git
   cd south-drift
   ```

2. **Install dependencies**

   ```bash
   # Frontend
   cd frontend
   pnpm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Setup environment variables**

   ```bash
   # Frontend
   cp frontend/.env.example frontend/.env.local
   
   # Backend
   cp backend/.env.example backend/.env
   ```

4. **Start development servers**

   ```bash
   # Backend (FastAPI)
   cd backend
   uvicorn main:app --reload --port 8000
   
   # Frontend (Next.js)
   cd frontend
   pnpm dev
   ```

   This will start:
   - **Backend**: <http://localhost:8000> (API docs at `/docs`)
   - **Frontend**: <http://localhost:3000>

### Using Docker

```bash
# Start the entire stack
docker-compose up -d

# Stop the stack
docker-compose down
```

## 🎯 Features

### Backend (FastAPI)

- ✅ RESTful API with automatic OpenAPI docs
- ✅ Async Python for high performance
- ✅ Patient management and clinical records
- ✅ Interaction tracking (visits, calls, appointments)
- ✅ Clinical document management (notes, labs, imaging, uploads)
- ✅ AI service orchestration
- ✅ CORS configuration for frontend
- ✅ Docker containerization

### Frontend (Next.js 15)

- ✅ Modern React with TypeScript
- ✅ Tailwind CSS + shadcn/ui components
- ✅ Patient dashboard with timeline
- ✅ Clinical document viewer
- ✅ Voice note upload and processing
- ✅ Responsive design
- ✅ BFF API routes for data aggregation

### AI Services

- ✅ Voice transcription via AWS Lambda + Bedrock
- ✅ Medical imaging analysis via Azure Functions
- ✅ Asynchronous processing with status tracking
- ✅ Multi-cloud orchestration

### Docker

```bash
docker-compose up -d       # Start all services
docker-compose down        # Stop all services
docker-compose logs -f     # View logs
```

## Deployment

### Azure Setup

1. **Run setup script**

   ```powershell
   .\scripts\setup-azure.ps1 -SubscriptionId "your-subscription-id"
   ```

2. **Configure GitHub Secrets**
   - `AZURE_CREDENTIALS` - Service Principal JSON
   - `AZURE_SUBSCRIPTION_ID`
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

3. **Deploy**

   ```bash
   git push origin main  # Triggers GitHub Actions
   ```

### Monitoring

- **Backend**: Application Insights in Azure portal
- **Frontend**: Vercel Analytics dashboard
- **Health Check**: `https://your-backend-url/health`

## Documentation

- [SPEC.md](./SPEC.md) - Technical specifications and implementation details
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed deployment guide
- Backend API Docs: `http://localhost:8000/docs` (when running locally)

## 🔒 Security

- Environment variables for all secrets
- CORS properly configured
- Role-based access control (RBAC)
- HIPAA-ready architecture
- Encrypted data at rest and in transit

# SouthDrift Technical Specification

## Architecture Overview

SouthDrift uses a modern, cloud-native architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js + React)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │   Patient    │  │  Dashboard   │  │  Clinical Docs UI    │  │
│  │   Timeline   │  │  Widgets     │  │  & Voice Upload      │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
│         │                  │                     │               │
│         │                  │                     │               │
│         └──────────────────┴─────────────────────┘               │
│                            │                                     │
│                   Direct HTTP Calls                              │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │   FastAPI Backend  │
                   │   (Python 3.11+)   │
                   │   - CRUD APIs      │
                   │   - Business Logic │
                   │   - AI Orchestration│
                   └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
      ┌───────▼──────┐ ┌──────▼──────┐ ┌────▼──────┐
      │ AWS Lambda    │ │   Azure      │ │  Database │
      │ + Bedrock     │ │  Functions   │ │  (Future) │
      │ (Audio AI)    │ │ (Imaging AI) │ │           │
      └───────────────┘ └──────────────┘ └───────────┘
```

### CI/CD Pipeline (GitHub Actions)

**Backend Workflow**:

1. Lint Python code (black, flake8)
2. Run tests (pytest)
3. Build Docker image
4. Push to Azure Container Registry
5. Deploy to Azure Container Apps

**Frontend Workflow**:

1. Lint TypeScript (ESLint)
2. Type check
3. Build Next.js
4. Deploy to Vercel

### Monitoring & Observability

**Application Insights**:

- Request/response logging
- Dependency tracking (external AI services)
- Custom events for AI processing
- Performance metrics

**Health Checks**:

- `GET /health` - Backend health status

**Alerts**:

- High error rate (> 5%)
- Slow response times (> 2s)
- AI service failures
- Blob storage unavailability

## Performance Optimization

### Backend (FastAPI)

- Async Python for concurrent request handling
- Connection pooling for database
- Caching for frequently accessed data
- Background tasks for AI processing

### Frontend (Next.js)

- Server-side rendering for initial load
- Client-side data fetching with SWR
- Image optimization (Next.js Image)
- Code splitting and lazy loading

### AI Services

- Batch processing for multiple requests
- Rate limiting to avoid quota exhaustion
- Retry logic with exponential backoff
- Status polling for long-running tasks

## 📝 License

MIT License - See [LICENSE](./LICENSE) for details
