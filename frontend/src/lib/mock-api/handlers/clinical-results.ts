import { jsonResponse } from "../http";
import type { MockApiHandler } from "../types";

export const handleClinicalResults: MockApiHandler = ({ path, state }) => {
    if (path === "/api/v1/diagnostic-reports") {
        return jsonResponse(state.reports);
    }
    const reportMatch = path.match(/^\/api\/v1\/diagnostic-reports\/([^/]+)$/);
    if (reportMatch) {
        const report = state.reports.find((item) => item.id === reportMatch[1]);
        return report
            ? jsonResponse(report)
            : jsonResponse({ detail: "Report not found" }, 404);
    }

    if (path === "/api/v1/imaging-studies") {
        return jsonResponse(state.imagingStudies);
    }

    return undefined;
};
