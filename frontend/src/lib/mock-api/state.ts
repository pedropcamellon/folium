import type { ClinicalDocument } from "@/types/clinicalDocument";
import type { DiagnosticReport } from "@/types/diagnosticReport";
import type { ImagingStudy } from "@/types/imagingStudy";
import { type User, UserRole } from "@/types/user";
import type { XrayScan } from "@/types/xrayScan";

import type { ChartReview, Patient, PatientEncounter } from "@/types";

export interface MockApiState {
    now: string;
    patientId: string;
    encounterId: string;
    demoUser: User;
    patients: Patient[];
    encounters: PatientEncounter[];
    documents: ClinicalDocument[];
    reports: DiagnosticReport[];
    imagingStudies: ImagingStudy[];
    xrayScans: Map<string, XrayScan>;
    chartReviews: Map<string, ChartReview>;
}

export const now = "2026-01-15T10:00:00.000Z";
export const patientId = "demo-patient-001";
export const encounterId = "demo-encounter-001";

export const demoUser: User = {
    id: "demo-user-001",
    email: "demo.provider@example.invalid",
    role: UserRole.PROVIDER,
    is_active: true,
    is_superuser: false,
    is_verified: true,
    created_at: now,
    updated_at: now,
};

export function createMockApiState(): MockApiState {
    return {
        now,
        patientId,
        encounterId,
        demoUser,
        patients: [
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
        ],
        encounters: [
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
        ],
        documents: [
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
        ],
        reports: [],
        imagingStudies: [],
        xrayScans: new Map(),
        chartReviews: new Map([
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
        ]),
    };
}

export const mockApiState = createMockApiState();
