
# Frontend Architecture (Next.js)

## Overview

The frontend is built with Next.js using the App Router, TypeScript, Tailwind CSS, and shadcn/ui for UI components. It follows a modular architecture with reusable dashboard widgets located in `frontend/src/components/dashboard/widgets/`. Data fetching is handled via SWR, and charts are rendered using Recharts. Framer Motion is used for animations.

## API Service Layer

**All frontend components call FastAPI directly via centralized API configuration** (no BFF middleware).

### API Configuration Pattern (Direct FastAPI calls)

**Implementation**: `lib/api.ts` provides centralized API endpoint configuration with:

- `FASTAPI_BASE_URL`: Base URL from environment variable (`NEXT_PUBLIC_API_URL`)
- `API_ENDPOINTS`: Object containing all endpoint URLs (static strings and factory functions for dynamic IDs)
- `fetcher`: Generic fetch wrapper for SWR that throws on non-OK responses

**Service Layer Pattern**: Domain-specific services (e.g., `clinicalDocumentService.ts`) import `API_ENDPOINTS` and wrap fetch calls with domain logic. Services handle error cases and return typed responses.

**Usage in Components**: React components use SWR with `API_ENDPOINTS` and `fetcher` for data fetching. No direct URL strings in components.

**Architecture Benefits**:

- Direct client-to-API pattern, proven in production environments
- No BFF layer = simpler architecture, fewer points of failure
- Centralized endpoint configuration prevents URL typos
- Environment-based URL switching (dev/staging/prod)

### Key Components

#### Dashboard Widgets - Patient Management

**Clean Architecture Pattern**: Separation of concerns with hooks (logic) + presentational components (UI) + orchestrator (container).

**Components**:

- **`usePatients` hook** (`hooks/usePatients.ts`): Business logic, SWR data fetching, CRUD operations, state management with DataStatus enum (IDLE/LOADING/SUCCESS/ERROR)
- **`PatientDialog`** (`dashboard/widgets/PatientDialog.tsx`): Form UI for add/edit patient, uses `useEffect` to populate form when patient prop changes
- **`PatientTable`** (`dashboard/widgets/PatientTable.tsx`): Table UI for displaying patients with loading skeletons
- **`PatientsSection`** (`dashboard/widgets/PatientsSection.tsx`): Orchestrator component that ties everything together

**State Management Pattern**:

Uses `DataStatus` enum (exported from `usePatients.ts`) instead of boolean flags for clear state tracking. Status values: IDLE (initial), LOADING (fetching), SUCCESS (data loaded), ERROR (fetch failed). Status derived from SWR state via `useMemo`.

**Design Decisions**:

- Enum over booleans: Eliminates ambiguous states (e.g., `isLoading && hasError`), makes status transitions explicit
- Form population: `useEffect` watches `patient` prop to populate edit form, avoiding manual prop-to-state sync issues
- SWR integration: Hook wraps SWR, exposes only relevant data/methods to UI components
- Error handling: Status enum drives UI states (error card, loading skeleton, success table)

#### PatientClinicalDocumentsPanel

Displays all documents for a patient with filtering by type.

**Implementation**:

- Fetches via `clinicalDocumentService.listClinicalDocuments(patientId)`
- API call: `GET /api/clinical-documents?patientId={id}`
- Uses SWR with `API_ENDPOINTS.documentsByPatient(patientId)` and `fetcher`
- Displays `typeLabel` for human-readable document types
- Click handlers to view/edit document details

#### InteractionDetailsModal - Audio Recording & Transcription

Shows details for a patient interaction with audio recording capability and linked documents.

**Clean Architecture Pattern**: Separation of business logic (hook) from UI (component).

**Components**:

- **`useInteractionAudio` hook** (`hooks/useInteractionAudio.ts`): Audio recording logic, upload/submission, polling for transcripts, state management with AudioState enum
- **`InteractionDetailsModal`** (`dashboard/InteractionDetailsModal.tsx`): UI component using hook methods, displays audio controls and transcript status

**AudioState Enum**: Tracks audio workflow state with 8 distinct states:

- `IDLE`: No audio activity
- `LOADED`: Audio loaded from backend (previously uploaded)
- `RECORDING`: Currently recording audio
- `RECORDED`: Recording stopped, ready to submit
- `SUBMITTING`: Uploading audio to backend
- `SUBMITTED`: Upload successful, brief confirmation
- `POLLING`: Waiting for AI transcription to complete
- `ERROR`: Recording or submission failed

**Audio Workflow**:

1. **Record**: User clicks microphone button → `startRecording()` → Browser MediaRecorder API captures audio → State = RECORDING
2. **Stop**: User clicks stop → `stopRecording()` → Audio blob created and stored locally → State = RECORDED
3. **Submit**: User clicks "Submit Audio" → `submitAudio()` → POST to `/api/interactions/{id}/audio` → State = SUBMITTING
4. **Poll**: After upload success → State = POLLING → Hook polls GET `/api/interactions/{id}` every 2s (max 20s) checking for note changes
5. **Update**: When `note` field changes → `onTranscriptUpdate(note)` callback → Modal displays updated note with transcript → State = IDLE

**Implementation Details**:

- **MediaRecorder API**: Browser-native audio recording, outputs WebM format
- **Blob Storage**: Recorded audio stored as local blob URL until submission
- **FormData Upload**: Audio sent as multipart/form-data with file named "audio.webm"
- **Polling with AbortController**: Background polling cancelled when modal closes to prevent memory leaks
- **Load Existing Audio**: On modal open, checks if interaction has stored audio via `metadata.audio` field, loads and displays audio player
- **Cleanup Pattern**: Hook exposes `cleanup()` method to abort polling and reset state when modal closes

**API Calls**:

- `GET /api/interactions/{id}` - Fetch interaction details and note
- `POST /api/interactions/{id}/audio` - Upload audio file
- `GET /api/interactions/{id}/audio` - Retrieve stored audio blob
- `PATCH /api/interactions/{id}/note` - Manual note editing (separate from transcript)

**Design Decisions**:

- Enum over booleans: Eliminates ambiguous states (e.g., `isRecording && isSubmitting`), makes workflow explicit
- Polling vs WebSockets: Polling chosen for MVP simplicity, WebSocket upgrade path planned for production
- Callback pattern: `onTranscriptUpdate` allows parent component to handle transcript differently (append, replace, notify)
- Separate LOADED state: Differentiates between freshly uploaded audio (SUBMITTED) and previously stored audio (LOADED) for UI messaging

### Data Models

#### Patient

**Backend Model** (`backend/app/models/patient.py`):

- Required fields: `medicalRecordNumber`, `firstName`, `lastName`, `dateOfBirth`, `gender`, `contactInfo`
- Optional fields: `email`, `phone`, `address`, `emergencyContact`
- Response includes: `id`, `createdAt`, `updatedAt`

**Frontend Type** (`frontend/src/types/index.ts`):

- Matches backend model structure
- `dateOfBirth` is ISO string format
- `gender` values: Male/Female/Other
- `contactInfo` is primary contact (phone or email)

**Key Decision**: Added `medicalRecordNumber`, `gender`, `contactInfo` as required fields to match clinical workflows. Backend models updated to align with frontend expectations (previously had different field names).
