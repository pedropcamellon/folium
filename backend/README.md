# SouthDrift: AI-Powered Clinical Documentation Platform Backend

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

## 📊 Core API Endpoints

### Patients

- `GET /api/patients` - List all patients
- `GET /api/patients/{id}` - Get patient details
- `GET /api/patients/{id}/interactions` - Get patient interactions

### Interactions

- `GET /api/patient-interactions?patientId={id}` - List patient interactions
- `GET /api/patient-interactions/{id}` - Get interaction details
- `GET /api/patient-interactions/{id}/documents` - Get documents for interaction
- `PATCH /api/patient-interactions/{id}/audio` - Upload audio for interaction

### Clinical Documents

- `GET /api/clinical-documents?patientId={id}` - List patient documents
- `GET /api/clinical-documents/{id}` - Get document details
- `POST /api/clinical-documents?patientId={id}` - Create document

For complete API documentation, see [SPEC.md](./SPEC.md)

### Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload      # Start dev server
pytest                          # Run tests
black .                         # Format code
```
