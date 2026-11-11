import type {
    Patient,
    PatientEncounter,
    SummarizationHealthResponse,
    SummarizationResponse,
    VoiceNoteWorkflowStatusResponse,
} from "@/types";
import type { ClinicalDocument } from "@/types/clinicalDocument";
import type { DiagnosticReport } from "@/types/diagnosticReport";
import type { ImagingStudy } from "@/types/imagingStudy";
import type { PatientTimelineResponse } from "@/types/patientTimeline";
import type { ChartReview } from "@/types";
import { VoiceNoteWorkflowStatus } from "@/types";
import { UserRole, type User } from "@/types/user";

const now = "2026-01-15T10:00:00.000Z";
const patientId = "demo-patient-001";
const encounterId = "demo-encounter-001";

const demoUser: User = {
    id: "demo-user-001",
    email: "demo.provider@example.invalid",
    role: UserRole.PROVIDER,
    is_active: true,
    is_superuser: false,
    is_verified: true,
    created_at: now,
    updated_at: now,
};

const patients: Patient[] = [
    {
        id: patientId,
        medicalRecordNumber: "DEMO-001",
        firstName: "Sample",
        lastName: "Patient",
        dateOfBirth: "1980-01-01",
        gender: "Other",
        contactInfo: "Synthetic demo record",
        medicalImages: [],
        clinicalSummaries: [],
    },
];

const encounters: PatientEncounter[] = [
    {
        id: encounterId,
        createdAt: now,
        createdBy: demoUser.id,
        startedAt: now,
        endedAt: now,
        isCompliant: true,
        note: "Sample note: patient reports feeling well and has no new concerns.",
        summary:
            "Routine follow-up. No new concerns reported. Continue current care plan.",
        structuredSummary: {
            chief_complaint: "Routine follow-up",
            subjective: "No new concerns reported.",
            objective: "Sample observations reviewed.",
            assessment: "Stable at this visit.",
            plan: "Continue the current care plan.",
            clinical_tags: ["follow-up"],
            icd_codes: [],
            action_items: ["Schedule the next routine follow-up."],
        },
        chiefComplaint: "Routine follow-up",
        clinicalAssessment: "Stable at this visit.",
        treatmentPlan: "Continue the current care plan.",
        patientId,
        clinicianId: demoUser.id,
        clinicianName: "Demo Provider",
        title: "Routine follow-up",
        encounterType: "outpatient",
        purpose: "follow_up",
        status: "completed",
        narratives: [],
        updatedAt: now,
        updatedBy: demoUser.id,
    },
];

const documents: ClinicalDocument[] = [
    {
        id: "demo-document-001",
        patientId,
        category: "visit_summary",
        status: "final",
        title: "Sample visit summary",
        authoredAt: now,
        createdAt: now,
        attachments: [],
    },
];
const reports: DiagnosticReport[] = [];
const imagingStudies: ImagingStudy[] = [];
const chartReviews = new Map<string, ChartReview>([
    [
        encounterId,
        {
            id: "demo-review-001",
            encounterId,
            status: "completed",
            summary: "Sample chart review completed.",
            reasoning: "Synthetic demo content only.",
            missingInfo: [],
            followUpQuestions: [],
            sourceRefs: [],
            confidence: "high",
            reviewFlags: [],
        },
    ],
]);

function jsonResponse(data: unknown, status = 200): Response {
    return new Response(status === 204 ? null : JSON.stringify(data), {
        status,
        headers: { "Content-Type": "application/json" },
    });
}

function readBody(init: RequestInit): Record<string, unknown> {
    if (typeof init.body !== "string") return {};
    try {
        return JSON.parse(init.body) as Record<string, unknown>;
    } catch {
        return {};
    }
}

function makeEncounter(body: Record<string, unknown>): PatientEncounter {
    const id = `demo-encounter-${crypto.randomUUID()}`;
    return {
        createdAt: now,
        createdBy: demoUser.id,
        startedAt: String(body.startedAt ?? now),
        isCompliant: true,
        patientId: String(body.patientId ?? patientId),
        title: String(body.title ?? "Sample encounter"),
        encounterType: "outpatient",
        purpose: "follow_up",
        status: "completed",
        narratives: [],
        ...body,
        id,
    } as PatientEncounter;
}

export async function mockApiRequest(
    input: string,
    init: RequestInit = {}
): Promise<Response> {
    const url = new URL(input, "http://localhost");
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const method = (init.method ?? "GET").toUpperCase();
    const body = readBody(init);

    if (path === "/health") {
        return jsonResponse({ status: "ok", message: "Mock API is ready." });
    }

    if (path === "/auth/register" && method === "POST") {
        return jsonResponse(demoUser, 201);
    }
    if (path === "/auth/jwt/login" && method === "POST") {
        return jsonResponse({
            access_token: "demo-token",
            token_type: "bearer",
        });
    }
    if (path === "/auth/jwt/logout" && method === "POST") {
        return jsonResponse(null, 204);
    }
    if (path === "/users/me" && method === "GET") {
        return jsonResponse(demoUser);
    }

    if (path.endsWith("/api/v1/patients")) {
        if (method === "GET") return jsonResponse(patients);
        if (method === "POST") {
            const patient: Patient = {
                id: `demo-patient-${crypto.randomUUID()}`,
                medicalRecordNumber: String(body.medicalRecordNumber ?? "DEMO-NEW"),
                firstName: String(body.firstName ?? "Sample"),
                lastName: String(body.lastName ?? "Patient"),
                dateOfBirth: String(body.dateOfBirth ?? "1980-01-01"),
                gender: String(body.gender ?? "Other"),
                contactInfo: String(body.contactInfo ?? "Synthetic demo record"),
                medicalImages: [],
                clinicalSummaries: [],
            };
            patients.push(patient);
            return jsonResponse(patient, 201);
        }
    }

    const patientMatch = path.match(/^\/api\/v1\/patients\/([^/]+)(?:\/(timeline))?$/);
    if (patientMatch) {
        const [, id, subresource] = patientMatch;
        const patient = patients.find((item) => item.id === id);
        if (subresource === "timeline") {
            const entries = encounters
                .filter((item) => item.patientId === id)
                .map((encounter) => ({
                    id: encounter.id,
                    patientId: id,
                    occurredAt: encounter.startedAt,
                    title: encounter.title,
                    status: encounter.status,
                    kind: "encounter" as const,
                    encounter,
                }));
            return jsonResponse({ entries, nextCursor: null } satisfies PatientTimelineResponse);
        }
        if (method === "GET") {
            return patient
                ? jsonResponse(patient)
                : jsonResponse({ detail: "Patient not found" }, 404);
        }
        if (method === "PUT" && patient) {
            Object.assign(patient, body);
            return jsonResponse(patient);
        }
        if (method === "DELETE") {
            const index = patients.findIndex((item) => item.id === id);
            if (index >= 0) patients.splice(index, 1);
            return jsonResponse(null, 204);
        }
    }

    if (path === "/api/v1/encounters") {
        if (method === "POST") {
            const encounter = makeEncounter(body);
            encounters.push(encounter);
            return jsonResponse(encounter, 201);
        }
        return jsonResponse(
            encounters.filter(
                (item) => !url.searchParams.has("patientId") ||
                    item.patientId === url.searchParams.get("patientId")
            )
        );
    }

    const encounterMatch = path.match(/^\/api\/v1\/encounters\/([^/]+)(?:\/([^/]+))?$/);
    if (encounterMatch) {
        const [, id, subresource] = encounterMatch;
        const encounter = encounters.find((item) => item.id === id);
        if (!encounter) return jsonResponse({ detail: "Encounter not found" }, 404);
        if (!subresource) return jsonResponse(encounter);
        if (subresource === "note" || subresource === "summary") {
            if (method !== "GET") {
                if (subresource === "note") encounter.note = String(body.note ?? "");
                else encounter.summary = String(body.summary ?? "");
            }
            return jsonResponse(encounter);
        }
        if (subresource === "chart-review") {
            return jsonResponse(
                chartReviews.get(id) ?? {
                    id: `demo-review-${id}`,
                    encounterId: id,
                    status: "completed",
                    summary: "Sample chart review completed.",
                    missingInfo: [],
                    followUpQuestions: [],
                    sourceRefs: [],
                    reviewFlags: [],
                } satisfies ChartReview
            );
        }
        if (subresource === "voice-note-status") {
            return jsonResponse({
                encounterId: id,
                status: VoiceNoteWorkflowStatus.COMPLETED,
                encounter,
            } satisfies VoiceNoteWorkflowStatusResponse);
        }
        if (subresource === "audio") {
            return method === "GET"
                ? new Response(null, { status: 404 })
                : jsonResponse({ status: "accepted" }, 202);
        }
    }

    if (path === "/api/v1/clinical-documents") {
        return jsonResponse(
            documents.filter(
                (item) => !url.searchParams.has("patientId") ||
                    item.patientId === url.searchParams.get("patientId")
            )
        );
    }
    if (path === "/api/v1/clinical-documents/upload" && method === "POST") {
        const document: ClinicalDocument = {
            id: `demo-document-${crypto.randomUUID()}`,
            patientId: String(body.patientId ?? patientId),
            category: "patient_submission",
            status: "final",
            title: "Sample document",
            createdAt: now,
            attachments: [],
        };
        documents.push(document);
        return jsonResponse(document, 201);
    }

    const documentMatch = path.match(/^\/api\/v1\/clinical-documents\/([^/]+)(?:\/attachments\/([^/]+)\/download)?$/);
    if (documentMatch) {
        const [, id, attachmentId] = documentMatch;
        if (attachmentId) {
            return new Response("Synthetic demo attachment.", {
                headers: { "Content-Type": "text/plain" },
            });
        }
        const document = documents.find((item) => item.id === id);
        if (method === "DELETE") return jsonResponse(null, 204);
        return document
            ? jsonResponse(document)
            : jsonResponse({ detail: "Document not found" }, 404);
    }

    if (path === "/api/v1/diagnostic-reports") return jsonResponse(reports);
    const reportMatch = path.match(/^\/api\/v1\/diagnostic-reports\/([^/]+)$/);
    if (reportMatch) {
        const report = reports.find((item) => item.id === reportMatch[1]);
        return report
            ? jsonResponse(report)
            : jsonResponse({ detail: "Report not found" }, 404);
    }

    if (path === "/api/v1/imaging-studies") return jsonResponse(imagingStudies);

    if (path === "/api/v1/summarization/health") {
        return jsonResponse({
            status: "ok",
            service_url: "mock",
            message: "Mock summarization is ready.",
        } satisfies SummarizationHealthResponse);
    }
    if (path === "/api/v1/summarization" && method === "POST") {
        const structured_data: SummarizationResponse["structured_data"] = {
            chief_complaint: "Routine follow-up",
            subjective: "Sample notes reviewed.",
            objective: "Sample observations reviewed.",
            assessment: "Stable at this visit.",
            plan: "Continue the current care plan.",
            clinical_tags: ["follow-up"],
            icd_codes: [],
            action_items: ["Schedule the next routine follow-up."],
        };
        return jsonResponse({
            summary: "Synthetic sample summary.",
            structured_data,
            processing_time: 0,
            model_used: "mock",
            provider: "mock",
            usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
        } satisfies SummarizationResponse);
    }

    return jsonResponse(
        { detail: `No mock API route for ${method} ${path}` },
        501
    );
}

export { demoUser };
