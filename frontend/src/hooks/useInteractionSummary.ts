import { useCallback, useState } from "react";

import {
    formatSoapSummary,
    generateSummary,
} from "@/services/summarizationService";

import { StructuredSummary } from "@/types";

export enum SummaryState {
    IDLE = "idle",
    GENERATING = "generating",
    SUCCESS = "success",
    ERROR = "error",
}

interface UseInteractionSummaryResult {
    summary: string;
    summaryState: SummaryState;
    summaryError: string | null;
    generateSummaryFromTranscript: (
        transcript: string,
        interactionType?: string
    ) => Promise<void>;
    setSummary: (summary: string) => void;
    clearError: () => void;
}

export function useInteractionSummary(
    onSummaryGenerated?: (
        summary: string,
        structuredData: StructuredSummary
    ) => void
): UseInteractionSummaryResult {
    const [summary, setSummary] = useState<string>("");
    const [summaryState, setSummaryState] = useState<SummaryState>(
        SummaryState.IDLE
    );
    const [summaryError, setSummaryError] = useState<string | null>(null);

    const generateSummaryFromTranscript = useCallback(
        async (transcript: string, interactionType?: string) => {
            if (!transcript || transcript.trim().length === 0) {
                setSummaryState(SummaryState.ERROR);
                setSummaryError(
                    "No transcript available. Please add a note or record audio first."
                );
                return;
            }

            setSummaryState(SummaryState.GENERATING);
            setSummaryError(null);

            try {
                const response = await generateSummary({
                    transcript,
                    format: "soap",
                    interaction_type: interactionType,
                });

                const formattedSummary = formatSoapSummary(
                    response.structured_data
                );
                setSummary(formattedSummary);
                setSummaryState(SummaryState.SUCCESS);

                // Notify parent component of successful generation
                onSummaryGenerated?.(
                    formattedSummary,
                    response.structured_data
                );
            } catch (e: any) {
                setSummaryState(SummaryState.ERROR);
                setSummaryError(e?.message || "Failed to generate summary");
            }
        },
        [onSummaryGenerated]
    );

    const clearError = useCallback(() => {
        setSummaryError(null);
        if (summaryState === SummaryState.ERROR) {
            setSummaryState(SummaryState.IDLE);
        }
    }, [summaryState]);

    return {
        summary,
        summaryState,
        summaryError,
        generateSummaryFromTranscript,
        setSummary,
        clearError,
    };
}
