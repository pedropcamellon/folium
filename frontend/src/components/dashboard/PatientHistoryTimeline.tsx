"use client";

import { useCallback, useEffect, useState } from "react";

import { API_ENDPOINTS } from "@/lib/api";
import { useTranscription } from "@/hooks/useTranscription";

import { InteractionType, PatientInteraction } from "@/types";

import PatientInteractionDetailsModal from "./InteractionDetailsModal";

interface PatientHistoryTimelineProps {
    interactions: PatientInteraction[];
}

const typeColors: Record<InteractionType, string> = {
    Appointment: "#2563eb",
    Vaccination: "#22c55e",
    Medication: "#f59e42",
    LabWork: "#a21caf",
    Procedure: "#ef4444",
    VoiceNote: "#14b8a6",
    Imaging: "#6366f1",
    Surgery: "#eab308",
    Consultation: "#0ea5e9",
    Emergency: "#dc2626",
    Discharge: "#6d28d9",
    Admission: "#f472b6",
};

export default function PatientHistoryTimeline({
    interactions,
}: PatientHistoryTimelineProps) {
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [selectedInteraction, setSelectedInteraction] =
        useState<PatientInteraction | null>(null);
    
    const { transcriptionState, startPolling } = useTranscription();

    // Fetch interaction when selected
    useEffect(() => {
        if (!selectedId) {
            setSelectedInteraction(null);
            return;
        }

        const fetchInteraction = async () => {
            try {
                const res = await fetch(API_ENDPOINTS.interaction(selectedId));
                if (res.ok) {
                    const data = await res.json();
                    setSelectedInteraction(data);
                }
            } catch (e) {
                console.error("Failed to fetch interaction:", e);
            }
        };

        fetchInteraction();
    }, [selectedId]);

    // Memoize callback to prevent recreating on every render
    const handleAudioSubmitted = useCallback(() => {
        if (selectedId) {
            startPolling(selectedId, (updatedInteraction) => {
                setSelectedInteraction(updatedInteraction);
            });
        }
    }, [selectedId, startPolling]);

    if (!Array.isArray(interactions) || interactions.length === 0) {
        return <div className="text-slate-400">No history found.</div>;
    }

    // Sort newest to oldest
    const sorted = [...interactions].sort(
        (a, b) =>
            new Date(b.interactionDate).getTime() -
            new Date(a.interactionDate).getTime()
    );

    return (
        <div className="relative pl-8">
            {/* Vertical line */}
            <div
                className="absolute left-3 top-0 bottom-0 w-0.5 bg-slate-200"
                style={{ zIndex: 0 }}
            />
            <div className="flex flex-col gap-8">
                {sorted.map((item, idx) => (
                    <div
                        key={item.id}
                        className="relative flex items-start gap-4 cursor-pointer group"
                        onClick={() => setSelectedId(item.id)}
                    >
                        {/* Dot */}
                        <div
                            className="absolute left-0 top-2 w-4 flex flex-col items-center"
                            style={{ zIndex: 1 }}
                        >
                            <div
                                className="w-4 h-4 rounded-full border-4 group-hover:scale-110 transition-transform"
                                style={{
                                    borderColor: typeColors[item.type],
                                    background: "#fff",
                                }}
                            />
                            {/* Only draw line below if not last */}
                            {idx !== sorted.length - 1 && (
                                <div className="w-0.5 flex-1 bg-slate-200 mt-0.5" />
                            )}
                        </div>
                        <div className="ml-8">
                            <div className="font-semibold text-base">
                                {item.title}{" "}
                                <span className="text-xs font-normal text-slate-400">
                                    ({item.type})
                                </span>
                            </div>
                            <div className="text-xs text-slate-500 mb-1">
                                {new Date(
                                    item.interactionDate
                                ).toLocaleString()}{" "}
                                &middot; {item.providerName}
                            </div>
                            <div className="text-sm text-slate-700">
                                {item.description}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
            {selectedId && selectedInteraction && (
                <PatientInteractionDetailsModal
                    interaction={selectedInteraction}
                    open={!!selectedId}
                    onClose={() => setSelectedId(null)}
                    onAudioSubmitted={handleAudioSubmitted}
                    transcriptionState={transcriptionState}
                />
            )}
        </div>
    );
}
