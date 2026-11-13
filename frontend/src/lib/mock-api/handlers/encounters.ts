import type { ChartReview, PatientEncounter } from "@/types";
import { VoiceNoteWorkflowStatus } from "@/types";

import { jsonResponse } from "../http";
import type { MockApiHandler } from "../types";

function makeEncounter(
    body: Record<string, unknown>,
    patientId: string,
    createdBy: string,
    now: string
): PatientEncounter {
    const id = `demo-encounter-${crypto.randomUUID()}`;
    return {
        createdAt: now,
        createdBy,
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

export const handleEncounters: MockApiHandler = ({
    path,
    method,
    body,
    url,
    state,
}) => {
    if (path === "/api/v1/encounters") {
        if (method === "POST") {
            const encounter = makeEncounter(
                body,
                state.patientId,
                state.demoUser.id,
                state.now
            );
            state.encounters.push(encounter);
            return jsonResponse(encounter, 201);
        }
        return jsonResponse(
            state.encounters.filter(
                (item) =>
                    !url.searchParams.has("patientId") ||
                    item.patientId === url.searchParams.get("patientId")
            )
        );
    }

    const encounterMatch = path.match(
        /^\/api\/v1\/encounters\/([^/]+)(?:\/([^/]+))?$/
    );
    if (!encounterMatch) return undefined;

    const [, id, subresource] = encounterMatch;
    const encounter = state.encounters.find((item) => item.id === id);
    if (!encounter) return jsonResponse({ detail: "Encounter not found" }, 404);
    if (!subresource) return jsonResponse(encounter);
    if (subresource === "note" || subresource === "summary") {
        if (method !== "GET") {
            if (subresource === "note")
                encounter.note = String(body.note ?? "");
            else encounter.summary = String(body.summary ?? "");
        }
        return jsonResponse(encounter);
    }
    if (subresource === "chart-review") {
        return jsonResponse(
            state.chartReviews.get(id) ??
                ({
                    id: `demo-review-${id}`,
                    encounterId: id,
                    status: "completed",
                    summary: "Sample chart review completed.",
                    missingInfo: [],
                    followUpQuestions: [],
                    sourceRefs: [],
                    reviewFlags: [],
                } satisfies ChartReview)
        );
    }
    if (subresource === "voice-note-status") {
        return jsonResponse({
            encounterId: id,
            status: VoiceNoteWorkflowStatus.COMPLETED,
            encounter,
        });
    }
    if (subresource === "audio") {
        return method === "GET"
            ? new Response(null, { status: 404 })
            : jsonResponse({ status: "accepted" }, 202);
    }

    return undefined;
};
