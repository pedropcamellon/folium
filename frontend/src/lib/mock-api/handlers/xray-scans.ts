import type { XrayScan } from "@/types/xrayScan";

import { jsonResponse } from "../http";
import type { MockApiHandler } from "../types";

function completeSyntheticScan(scan: XrayScan): XrayScan {
    return {
        ...scan,
        status: "COMPLETE",
        result: {
            findings: [
                { label: "Lung Lesion", score: 0.74 },
                { label: "No Finding", score: 0.18 },
            ],
            modelRepository: "synthetic-mock",
            modelRevision: "mock",
            reviewRequired: true,
            disclaimer:
                "Synthetic mock result only. Not a model output or diagnosis.",
        },
    };
}

export const handleXrayScans: MockApiHandler = ({
    path,
    method,
    body,
    url,
    state,
}) => {
    if (path === "/api/v1/xray-scans" && method === "POST") {
        const id = `demo-xray-scan-${crypto.randomUUID()}`;
        const scan: XrayScan = {
            id,
            patientId: String(body.patientId ?? state.patientId),
            clinicalDocumentId: String(body.clinicalDocumentId ?? ""),
            status: "PENDING",
            result: null,
            failureMessage: null,
        };
        state.xrayScans.set(id, scan);
        globalThis.setTimeout(() => {
            const current = state.xrayScans.get(id);
            if (current) {
                state.xrayScans.set(id, { ...current, status: "PROCESSING" });
            }
        }, 1200);
        globalThis.setTimeout(() => {
            const current = state.xrayScans.get(id);
            if (current) {
                state.xrayScans.set(id, completeSyntheticScan(current));
            }
        }, 3600);
        return jsonResponse(scan, 202);
    }

    if (path === "/api/v1/xray-scans" && method === "GET") {
        const requestedPatientId = url.searchParams.get("patientId");
        return jsonResponse(
            [...state.xrayScans.values()].filter(
                (scan) =>
                    !requestedPatientId || scan.patientId === requestedPatientId
            )
        );
    }

    const scanMatch = path.match(/^\/api\/v1\/xray-scans\/([^/]+)$/);
    if (!scanMatch) return undefined;
    const scan = state.xrayScans.get(scanMatch[1]);
    return scan
        ? jsonResponse(scan)
        : jsonResponse({ detail: "X-ray review not found" }, 404);
};
