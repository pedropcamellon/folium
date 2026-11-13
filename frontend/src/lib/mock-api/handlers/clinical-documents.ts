import type { ClinicalDocument } from "@/types/clinicalDocument";

import { jsonResponse } from "../http";
import type { MockApiHandler } from "../types";

export const handleClinicalDocuments: MockApiHandler = ({
    path,
    method,
    body,
    url,
    state,
}) => {
    if (path === "/api/v1/clinical-documents") {
        return jsonResponse(
            state.documents.filter(
                (item) =>
                    !url.searchParams.has("patientId") ||
                    item.patientId === url.searchParams.get("patientId")
            )
        );
    }

    if (path === "/api/v1/clinical-documents/upload" && method === "POST") {
        const document: ClinicalDocument = {
            id: `demo-document-${crypto.randomUUID()}`,
            patientId: String(body.patientId ?? state.patientId),
            category: "patient_submission",
            status: "final",
            title: "Sample document",
            createdAt: state.now,
            attachments: [],
        };
        state.documents.push(document);
        return jsonResponse(document, 201);
    }

    const documentMatch = path.match(
        /^\/api\/v1\/clinical-documents\/([^/]+)(?:\/attachments\/([^/]+)\/download)?$/
    );
    if (!documentMatch) return undefined;

    const [, id, attachmentId] = documentMatch;
    if (attachmentId) {
        return new Response("Synthetic demo attachment.", {
            headers: { "Content-Type": "text/plain" },
        });
    }
    const document = state.documents.find((item) => item.id === id);
    if (method === "DELETE") return jsonResponse(null, 204);
    return document
        ? jsonResponse(document)
        : jsonResponse({ detail: "Document not found" }, 404);
};
