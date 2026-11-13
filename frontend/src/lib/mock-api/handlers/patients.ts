import type { PatientTimelineResponse } from "@/types/patientTimeline";

import { jsonResponse } from "../http";
import type { MockApiHandler } from "../types";

export const handlePatients: MockApiHandler = ({
    path,
    method,
    body,
    url,
    state,
}) => {
    if (path.endsWith("/api/v1/patients")) {
        if (method === "GET") return jsonResponse(state.patients);
        if (method === "POST") {
            const patient = {
                id: `demo-patient-${crypto.randomUUID()}`,
                medicalRecordNumber: String(
                    body.medicalRecordNumber ?? "DEMO-NEW"
                ),
                firstName: String(body.firstName ?? "Sample"),
                lastName: String(body.lastName ?? "Patient"),
                dateOfBirth: String(body.dateOfBirth ?? "1980-01-01"),
                gender: String(body.gender ?? "Other"),
                contactInfo: String(
                    body.contactInfo ?? "Synthetic demo record"
                ),
                medicalImages: [],
                clinicalSummaries: [],
            };
            state.patients.push(patient);
            return jsonResponse(patient, 201);
        }
    }

    const patientMatch = path.match(
        /^\/api\/v1\/patients\/([^/]+)(?:\/(timeline))?$/
    );
    if (!patientMatch) return undefined;

    const [, id, subresource] = patientMatch;
    const patient = state.patients.find((item) => item.id === id);
    if (subresource === "timeline") {
        const entries = state.encounters
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
        return jsonResponse({
            entries,
            nextCursor: null,
        } satisfies PatientTimelineResponse);
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
        const index = state.patients.findIndex((item) => item.id === id);
        if (index >= 0) state.patients.splice(index, 1);
        return jsonResponse(null, 204);
    }

    return undefined;
};
