import type { SummarizationResponse } from "@/types";

import { jsonResponse } from "../http";
import type { MockApiHandler } from "../types";

export const handleSummarization: MockApiHandler = ({ path, method }) => {
    if (path === "/api/v1/summarization/health") {
        return jsonResponse({
            status: "ok",
            service_url: "mock",
            message: "Mock summarization is ready.",
        });
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

    return undefined;
};
