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
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Alembic migrations for schema management
- ✅ Auto-seeding with test data on startup

## 🗄️ Database Setup

### Connection

PostgreSQL runs in Docker Compose. Connection configured via environment variables:

```
DATABASE_URL=postgresql+asyncpg://southdrift:southdrift@postgres:5432/southdrift_db
```

### Migrations

Alembic manages database schema changes:

```bash
# Create a new migration after model changes
docker compose exec backend alembic revision --autogenerate -m "Description"

# Apply pending migrations
docker compose exec backend alembic upgrade head

# Rollback last migration
docker compose exec backend alembic downgrade -1

# View migration history
docker compose exec backend alembic history
```

### Seed Data

Test data automatically seeds on startup via `app/main.py`:

- **Users**: 4 test users (admin, provider, staff, patient)
- **Patients**: 4 sample patients (María García, James Thompson, Luis Fernández, jon d)
- **Interactions**: 10 diverse encounters (appointments, voice notes, lab work, vaccinations)
- **Documents**: 3 clinical documents (imaging reports, forms, lab results)

To manually reseed:

```bash
docker compose exec backend python -m app.seed_db
```

To clear interactions and documents:

```bash
docker compose exec backend sh -c "cd /app && python -m app.clear_data"
docker compose restart backend  # Triggers auto-reseed
```

### Database Console

Access PostgreSQL directly:

```bash
docker compose exec postgres psql -U southdrift -d southdrift_db

# Useful queries
\dt                           # List tables
SELECT * FROM patient;        # View patients
SELECT * FROM interaction;    # View interactions
SELECT * FROM document;       # View documents
```

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

## 🛠️ Development

### Local Development (Docker)

```bash
# Start all services
docker compose up

# View logs
docker compose logs backend -f

# Restart backend after code changes
docker compose restart backend

# Access backend shell
docker compose exec backend sh
```

### Database Management

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "Add field"

# Reseed database
docker compose restart backend  # Auto-seeds on startup
```

### API Testing

Interactive API docs available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

```bash
# Health check
curl http://localhost:8000/health

# List patients
curl http://localhost:8000/api/v1/patients

# Get patient interactions
curl "http://localhost:8000/api/v1/interactions?patientId={id}"
```
