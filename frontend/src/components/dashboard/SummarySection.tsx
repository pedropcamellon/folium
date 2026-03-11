import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";

import { API_ENDPOINTS } from "@/lib/api";

import {
    SummaryState,
    useInteractionSummary,
} from "@/hooks/useInteractionSummary";

import { PatientInteraction } from "@/types";

enum SummaryEditState {
    VIEWING = "viewing",
    EDITING = "editing",
    SAVING = "saving",
}

interface SummarySectionProps {
    interaction: PatientInteraction;
    note: string;
    onInteractionUpdate: (interaction: PatientInteraction) => void;
}

export function SummarySection({
    interaction,
    note,
    onInteractionUpdate,
}: SummarySectionProps) {
    const [editState, setEditState] = useState<SummaryEditState>(
        SummaryEditState.VIEWING
    );
    const [editedSummary, setEditedSummary] = useState("");
    const [saveError, setSaveError] = useState<string | null>(null);
    const summaryInputRef = useRef<HTMLTextAreaElement>(null);

    const {
        summary,
        summaryState,
        summaryError,
        generateSummaryFromTranscript,
        setSummary,
    } = useInteractionSummary((formattedSummary, structuredData) => {
        onInteractionUpdate({
            ...interaction,
            summary: formattedSummary,
            structuredSummary: structuredData,
            chiefComplaint: structuredData.chief_complaint,
            clinicalAssessment: structuredData.assessment,
            treatmentPlan: structuredData.plan,
        });
    });

    useEffect(() => {
        setSummary(interaction.summary || "");
    }, [interaction.summary, setSummary]);

    useEffect(() => {
        if (editState === SummaryEditState.EDITING) {
            setEditedSummary(summary);
            setTimeout(() => summaryInputRef.current?.focus(), 0);
        }
    }, [editState, summary]);

    const handleGenerate = () => {
        generateSummaryFromTranscript(note, interaction.type);
    };

    const handleSave = async () => {
        setEditState(SummaryEditState.SAVING);
        setSaveError(null);
        try {
            const res = await fetch(
                API_ENDPOINTS.interactionSummary(interaction.id),
                {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ summary: editedSummary }),
                }
            );
            if (!res.ok) throw new Error("Failed to save summary");
            setSummary(editedSummary);
            onInteractionUpdate({ ...interaction, summary: editedSummary });
            setEditState(SummaryEditState.VIEWING);
        } catch (e) {
            setSaveError("Failed to save summary");
            setEditState(SummaryEditState.EDITING);
        }
    };

    const handleCancel = () => {
        setEditedSummary(summary);
        setEditState(SummaryEditState.VIEWING);
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-1">
                <div className="font-semibold">Clinical Summary</div>
                <div className="flex gap-2">
                    <Button
                        size="sm"
                        variant="outline"
                        onClick={handleGenerate}
                        disabled={
                            summaryState === SummaryState.GENERATING || !note
                        }
                    >
                        {summaryState === SummaryState.GENERATING
                            ? "Generating..."
                            : "Generate Summary"}
                    </Button>
                </div>
            </div>
            {summaryError && (
                <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                    Failed to generate summary
                </div>
            )}
            {editState === SummaryEditState.VIEWING ? (
                <>
                    <div className="whitespace-pre-wrap text-sm mb-2 border p-3 rounded bg-slate-50">
                        {summary ||
                            "No summary available. Generate one from your notes."}
                    </div>
                    {summary && (
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                                setEditState(SummaryEditState.EDITING)
                            }
                        >
                            Edit Summary
                        </Button>
                    )}
                </>
            ) : (
                <>
                    <textarea
                        ref={summaryInputRef}
                        value={editedSummary}
                        onChange={(e) => setEditedSummary(e.target.value)}
                        className="w-full border p-2 rounded text-sm mb-2 min-h-[120px]"
                        placeholder="Edit summary..."
                    />
                    <div className="flex items-center gap-2">
                        <Button
                            size="sm"
                            onClick={handleSave}
                            disabled={editState === SummaryEditState.SAVING}
                        >
                            {editState === SummaryEditState.SAVING
                                ? "Saving..."
                                : "Save"}
                        </Button>
                        <Button
                            size="sm"
                            variant="ghost"
                            onClick={handleCancel}
                        >
                            Cancel
                        </Button>
                    </div>
                    {saveError && (
                        <div className="text-xs text-red-500 mt-1">
                            {saveError}
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
