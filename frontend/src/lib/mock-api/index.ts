import { handleAuth } from "./handlers/auth";
import { handleClinicalDocuments } from "./handlers/clinical-documents";
import { handleClinicalResults } from "./handlers/clinical-results";
import { handleEncounters } from "./handlers/encounters";
import { handlePatients } from "./handlers/patients";
import { handleSummarization } from "./handlers/summarization";
import { handleXrayScans } from "./handlers/xray-scans";
import { jsonResponse, readJsonBody } from "./http";
import { mockApiState } from "./state";
import type { MockApiHandler } from "./types";

const handlers: MockApiHandler[] = [
    handleAuth,
    handlePatients,
    handleEncounters,
    handleClinicalDocuments,
    handleClinicalResults,
    handleXrayScans,
    handleSummarization,
];

export async function mockApiRequest(
    input: string,
    init: RequestInit = {}
): Promise<Response> {
    const url = new URL(input, "http://localhost");
    const path = url.pathname.replace(/\/+$/, "") || "/";
    const request = {
        url,
        path,
        method: (init.method ?? "GET").toUpperCase(),
        body:
            init.body instanceof FormData
                ? Object.fromEntries(
                      Array.from(init.body.entries()).filter(
                          ([, value]) => typeof value === "string"
                      )
                  )
                : readJsonBody(init),
        state: mockApiState,
    };

    for (const handler of handlers) {
        const response = handler(request);
        if (response) return response;
    }

    return jsonResponse(
        { detail: `No mock API route for ${request.method} ${path}` },
        501
    );
}

export { demoUser } from "./state";
