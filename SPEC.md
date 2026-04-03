
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
