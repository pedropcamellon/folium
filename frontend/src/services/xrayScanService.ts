import { XrayScan } from "@/types/xrayScan";

import { API_ENDPOINTS, apiJson } from "@/lib/api";

export async function createXrayScan(params: {
    patientId: string;
    clinicalDocumentId: string;
}): Promise<XrayScan> {
    return apiJson<XrayScan>(API_ENDPOINTS.xrayScans, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
    });
}

export async function getXrayScan(
    id: string,
    patientId: string
): Promise<XrayScan> {
    return apiJson<XrayScan>(API_ENDPOINTS.xrayScan(id, patientId));
}

export async function listXrayScans(patientId: string): Promise<XrayScan[]> {
    return apiJson<XrayScan[]>(
        `${API_ENDPOINTS.xrayScans}?patientId=${patientId}`
    );
}
