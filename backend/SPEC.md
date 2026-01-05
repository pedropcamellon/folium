# Backend Architecture (FastAPI)

> **Documentation Rule**: SPEC files contain high-level architecture descriptions and design decisions only. Code snippets should be minimal (5-10 lines max) to illustrate patterns. Full implementations belong in source files, not documentation.

## Overview

The backend is built with FastAPI using Python 3.11+. It follows a 3-layer architecture pattern (API routes, service layer, repository layer) with clear separation of concerns. Currently, it uses in-memory repositories for data storage to facilitate rapid development and prototyping. The architecture is designed to be easily migrated to a persistent database (PostgreSQL or Cosmos DB) in the future.

## Documentation Structure

This document provides a high-level overview of the backend architecture. For detailed implementation specifications of individual modules, refer to:

- **Storage Module**: [`app/services/storage/SPEC.md`](app/services/storage/SPEC.md) - Multi-cloud storage architecture (AWS S3, Azure Blob, MinIO) using Abstract Factory pattern with native SDKs

For user-facing feature documentation (workflows, use cases, business requirements), refer to:

- **Document Upload Feature**: [`/docs/features/document-upload.md`](../docs/features/document-upload.md) - Clinical document upload/viewing workflows and user requirements

Additional module-specific SPEC files will be added as the system evolves (e.g., authentication, caching, messaging queues).

## Application Architecture

**Entry Point (main.py)**:

- FastAPI app initialization with OpenAPI documentation at `/docs` and `/redoc`
- CORS middleware configured to allow Next.js frontend (localhost:3000 and production domains)
- API router registration under `/api` prefix
- Root-level health check endpoint at `/health` returning status and version
- Startup event for initializing connections and loading seed data
- Shutdown event for graceful cleanup of resources

**Configuration Management (config.py)**:8

- Uses `pydantic-settings` for type-safe environment variable loading
- Loads from `.env` file with sensible defaults
- Key settings: app name, debug mode, CORS origins, database URL, Azure/AWS credentials
- `extra = "ignore"` configuration to coexist with .NET Core environment variables during migration
- All secrets should be stored in Azure Key Vault for production

### 3-Layer Architecture Pattern

**Layer 1: API Routes (api/v1/endpoints/)**

- Thin controllers that handle HTTP-specific logic (request/response, status codes)
- Use FastAPI dependency injection with `Depends()` to inject services
- Define Pydantic models for request validation and response serialization
- Example: `@router.get("/", response_model=List[PatientResponse])`
- Each endpoint delegates business logic to service layer

**Layer 2: Service Layer (services/)**

- Contains all business logic and orchestration
- Validates business rules before calling repositories
- Transforms repository data to Pydantic response models using `model_validate()`
- Example: Patient service validates duplicates, checks constraints before creation
- Raises custom exceptions (e.g., `PatientNotFoundError`) for error handling

**Layer 3: Repository Layer (repositories/)**

- Pure data access with no business logic
- Currently uses in-memory dictionaries for MVP (easy to migrate to SQLAlchemy later)
- Inherits from `BaseRepository` abstract class for consistent interface
- Provides CRUD operations: `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`
- Seed data in `_seed_data()` method for development/demo purposes

### Dependency Injection Pattern

**Design Decision**: Use FastAPI's built-in DI system instead of external frameworks

- Repository instances created as module-level singletons (for in-memory storage)
- Dependency functions (e.g., `get_patient_service()`) use `Depends()` to chain dependencies
- Service functions receive repository via `Depends(get_patient_repository)`
- Benefits: Testable (easy to mock), explicit dependencies, automatic injection by FastAPI

**Migration Path**: When moving to database, replace singleton pattern with connection pooling using `async_session_maker()` to yield database sessions.

### Data Modeling Strategy

**Pydantic Models** (models/):

- Three model types per entity: `Base`, `Create`, `Update`, `Response`
- `Base`: Shared fields (used by Create and Response)
- `Create`: Required fields for new records (no ID, timestamps)
- `Update`: All fields optional (use `exclude_unset=True` when saving)
- `Response`: Includes ID, timestamps, and uses `from_attributes=True` for ORM compatibility

**Field Validation**:

- Use `Field()` for constraints: `min_length`, `max_length`, regex patterns
- Mark optional fields with `Optional[T]` and default `None`
- DateTime fields stored as ISO strings in repository, converted by Pydantic automatically

### Core Modules

#### 1. Patient Management

- **Models**: `Patient`, `PatientProfile`
- **Endpoints**:
  - `GET /api/patients` - List all patients
  - `GET /api/patients/{id}` - Get patient details
  - `POST /api/patients` - Create new patient
  - `PUT /api/patients/{id}` - Update patient
  - `DELETE /api/patients/{id}` - Delete patient

#### 2. Patient Interactions

Tracks all touchpoints with patients (visits, calls, appointments).

- **Models**: `PatientInteraction`, `InteractionType` (enum)
- **Endpoints**:
  - `GET /api/patient-interactions?patientId={id}` - List patient interactions (timeline)
  - `GET /api/patient-interactions/{id}` - Get interaction details
  - `POST /api/patient-interactions` - Create interaction
  - `PUT /api/patient-interactions/{id}` - Update interaction
  - `DELETE /api/patient-interactions/{id}` - Delete interaction
  - `PATCH /api/interactions/{id}/note` - Update interaction note
  - `POST /api/interactions/{id}/audio` - Upload audio file for interaction
  - `GET /api/interactions/{id}/audio` - Retrieve stored audio blob
  - `GET /api/interactions/{id}/documents` - Get documents linked to interaction

**Interaction Types**:

- `Visit` - In-person appointment
- `PhoneCall` - Phone consultation
- `VideoCall` - Telehealth session
- `LabVisit` - Lab work
- `ImagingStudy` - Imaging appointment
- `FollowUp` - Follow-up appointment

#### 3. Clinical Documents

Unified document management for all patient-related documents.

- **Base Model**: `ClinicalDocumentBase`
  - Common fields: `id`, `patientId`, `type`, `typeLabel`, `title`, `summary`, `createdAt`, `interactionId`
- **Document Types**:
  - `ClinicalNote` - Provider notes (SOAP, free text, structured)
  - `LabResult` - Lab test results with status
  - `ImagingReport` - Imaging study reports
  - `PatientUpload` - Patient-uploaded forms/documents
  - `AdministrativeForm` - HIPAA, consent, financial forms
  - `Prescription` - Medication prescriptions
  - `VisitSummary` - Post-visit summaries

- **Endpoints**:
  - `GET /api/clinical-documents?patientId={id}&types={types}` - List patient documents (with optional type filtering)
  - `GET /api/clinical-documents/{id}` - Get document details
  - `POST /api/clinical-documents?patientId={id}` - Create document
  - `PATCH /api/clinical-documents/{id}` - Update document
  - `DELETE /api/clinical-documents/{id}` - Delete document

**Document Type Labels** (human-readable):

- `ClinicalNote` → "Note"
- `LabResult` → "Labs"
- `ImagingReport` → "Imaging"
- `PatientUpload` → "Upload"
- `AdministrativeForm` → "Form"

#### 4. AI Service Orchestration

**Voice Processing Pipeline**:

1. User uploads audio file via `PATCH /api/patient-interactions/{id}/audio`
2. Backend uploads to Azure Blob Storage
3. Triggers AWS Lambda for transcription (Bedrock)
4. Lambda returns transcription + summary
5. Backend links result to interaction via `audioDocumentId`

**Imaging Analysis Pipeline**:

1. Medical images uploaded via dedicated endpoint
2. Stored in blob storage
3. Azure Function processes image (Custom Vision)
4. Results stored as `ImagingReport` document
5. Dashboard displays alerts for critical findings

### Domain Model Design Decisions

**ClinicalDocumentBase** - Abstract base model for all clinical documents:

- **Design Choice**: Use discriminated union pattern with `type` field (enum) for polymorphism
- **typeLabel**: Human-readable label auto-generated from enum type (e.g., `ClinicalNote` → "Note")
- **interactionId**: Optional link to PatientInteraction (visit/call during which document was created)
- **metadata**: JSON field for extensibility without schema changes
- **Audit fields**: `createdBy`, `updatedBy`, `createdAt`, `updatedAt` for compliance tracking

**ClinicalNoteDocument** - Extends base model for provider notes:

- **format**: Enum supporting SOAP (Subjective/Objective/Assessment/Plan), free text, or structured templates
- **Provider context**: Captures who wrote the note (ID, name, role) for audit trail
- **Clinical context**: Arrays for diagnoses, procedures, medications mentioned in note
- **Design rationale**: Keep structured data separate from free-text content for search/analytics

**PatientInteraction** - Represents any patient touchpoint:

- **Type-based workflow**: Enum determines required fields and subsequent actions
- **audioDocumentId**: Links to transcription/summary document created by AI processing
- **Status lifecycle**: `Scheduled` → `Completed` (or `Cancelled`) affects billing, follow-ups
- **Extensibility**: Can link multiple documents via `interactionId` foreign key pattern

## AI Services Integration

### Modular AI Microservices Architecture

**Design Philosophy**: AI services are deployed as containerized FastAPI microservices (not serverless functions) for portability, consistency, and avoiding vendor lock-in.

**Deployment Strategy**:

- Docker containers running on Kubernetes (EKS/AKS) or container platforms (ECS/Azure Container Apps)
- Horizontal pod autoscaling based on queue depth and CPU metrics
- GPU node pools for imaging workloads (NVIDIA CUDA support)
- Service mesh for internal communication (Istio/Linkerd optional)

### Voice Processing Microservice

**Container**: `southdrift-voice-processing` (FastAPI)

**Endpoints**:

- `POST /transcribe` - Accept audio file, return transcript + summary
- `GET /health` - Health check for load balancer
- `GET /metrics` - Prometheus metrics for monitoring

**Current Implementation (MVP)**:

Main backend handles audio inline:

1. Accept multipart/form-data audio file upload via `POST /api/interactions/{id}/audio`
2. Store audio as base64 string in `interaction.metadata.audio` field
3. Launch background task with `asyncio.create_task(mock_transcription())`
4. Background task sleeps 3 seconds, appends mock transcript to interaction note
5. Frontend polls GET `/api/interactions/{id}` to detect note change

**Future Production Implementation** (Microservice):

1. Main backend uploads audio to Azure Blob Storage
2. Main backend sends message to Azure Service Bus queue:

   ```json
   {
     "interactionId": "interaction-123",
     "audioUrl": "https://storage.blob.core.windows.net/audio/abc.webm",
     "callbackUrl": "https://api.southdrift.com/api/interactions/interaction-123/note"
   }
   ```

3. Voice processing microservice polls queue, downloads audio
4. Microservice calls AWS Bedrock/Azure Speech API for transcription
5. Microservice POSTs result to callback URL: `PATCH /api/interactions/{id}/note`
6. Main backend updates note, frontend polls for changes (or use WebSocket)

**Tech Stack**:

- FastAPI container with Celery for background processing
- AWS Bedrock API or Azure Cognitive Services Speech API
- Redis for caching and rate limiting
- Prometheus metrics exported for monitoring

**Deployment**:

- EKS/ECS with Docker containers
- Horizontal pod autoscaling (HPA) based on queue depth
- Spot instances for cost optimization
- 2-5 minute cold start acceptable (async processing)

### Medical Imaging Microservice

**Container**: `southdrift-imaging-analysis` (FastAPI + CUDA)

**Endpoints**:

- `POST /analyze` - Accept medical image, return findings + confidence scores
- `GET /health` - Health check for load balancer
- `GET /metrics` - Prometheus metrics for monitoring

**Current Implementation (MVP)**:

Not yet implemented (Phase 3).

**Future Production Implementation** (Microservice):

1. Main backend uploads image to Azure Blob Storage
2. Main backend sends message to Azure Service Bus queue:

   ```json
   {
     "patientId": "patient-123",
     "imageUrl": "https://storage.blob.core.windows.net/images/xray-456.dcm",
     "imageType": "ChestXRay",
     "callbackUrl": "https://api.southdrift.com/api/clinical-documents"
   }
   ```

3. Imaging microservice polls queue, downloads image (DICOM format)
4. Microservice runs inference using Azure Custom Vision or custom PyTorch model
5. Microservice POSTs result to callback: `POST /api/clinical-documents` (creates ImagingReport)
6. Dashboard displays alerts if critical findings detected

**Tech Stack**:

- FastAPI container with NVIDIA CUDA drivers
- PyTorch/TensorFlow for custom models or Azure Custom Vision SDK
- DICOM processing libraries (pydicom)
- Redis for caching inference results

**Deployment**:

- EKS/AKS with GPU-enabled node pools (NVIDIA T4/A10 instances)
- Horizontal pod autoscaling based on queue depth
- GPU sharing for cost optimization (multiple containers per GPU)
- 5-10 minute processing time acceptable (async)

**Error Handling** (Both Microservices):

- HTTP 503 if blob storage unavailable
- HTTP 502 if AI API (Bedrock/Custom Vision) fails
- Retry logic with exponential backoff (3 retries, max 5 minutes)
- Dead letter queue for failed messages
- Alerting via Prometheus/Grafana

**Migration Path from MVP**:

1. Extract audio processing code from main backend to new FastAPI service
2. Containerize with Dockerfile (multi-stage build)
3. Add Azure Service Bus consumer for queue-based processing
4. Deploy to ECS/EKS with minimal infrastructure (1-2 containers)
5. Update main backend to enqueue messages instead of inline processing
6. Add observability (logs, metrics, traces via OpenTelemetry)

**Benefits of Container-First Approach**:

- **Portability**: Run same containers in dev (Docker Compose), staging (ECS), prod (EKS)
- **No vendor lock-in**: Avoid Lambda/Azure Functions proprietary APIs
- **Consistent environment**: Same Python/dependencies across all environments
- **Local development**: Full microservice architecture runs on developer laptop
- **Cost predictable**: No per-invocation billing, reserved instances for baseline
- **Observability**: Standard container metrics (Prometheus) vs. serverless limitations

## Database Strategy

**Current**: In-memory repositories for MVP

- `InMemoryPatientRepository`
- `InMemoryPatientInteractionRepository`
- `InMemoryClinicalDocumentRepository`

**Future**: PostgreSQL or Cosmos DB

- Patient records
- Clinical documents (with blob storage for files)
- Interaction history
- AI processing results

## Security Implementation

### Authentication & Authorization

- **Current**: API key-based for external services
- **Planned**: Azure AD B2C for user authentication
- **RBAC**: Provider, Admin, Patient roles

### Data Protection

- **At Rest**: Encrypted blob storage (Azure)
- **In Transit**: HTTPS/TLS 1.3
- **Secrets**: Azure Key Vault
- **Compliance**: HIPAA-ready architecture

### CORS Configuration

**Implementation**: FastAPI CORS middleware configured in `main.py`

- **Allowed origins**: Dynamic list loaded from `settings.ALLOWED_ORIGINS`
- **Development**: `http://localhost:3000` (Next.js dev server)
- **Production**: Vercel deployment URL (configured via environment variable)
- **Credentials**: Enabled for cookie-based auth (future)
- **Methods/Headers**: Wildcard (`*`) for simplicity during development, should be restricted in production

**Security Considerations**:

- Never use `origins=["*"]` with `allow_credentials=True` (security risk)
- For production, maintain explicit allowlist of frontend domains
- Consider rate limiting middleware for public endpoints
