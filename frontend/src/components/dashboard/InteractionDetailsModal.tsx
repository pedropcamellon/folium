import { useEffect, useState } from "react";

import { SAMPLE_CLINICAL_TRANSCRIPT } from "@/data/sampleTranscripts";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";

import { API_ENDPOINTS } from "@/lib/api";

import { PatientInteraction } from "@/types";

import { NotesSection } from "./NotesSection";
import { SummarySection } from "./SummarySection";

interface PatientInteractionDetailsModalProps {
    interactionId: string;
    open: boolean;
    onClose: () => void;
}

export default function PatientInteractionDetailsModal({
    interactionId,
    open,
    onClose,
}: PatientInteractionDetailsModalProps) {
    const [currentInteraction, setCurrentInteraction] =
        useState<PatientInteraction | null>(null);

    useEffect(() => {
        if (open && interactionId) {
            fetch(API_ENDPOINTS.interaction(interactionId))
                .then(async (res) => {
                    if (!res.ok) throw new Error("Failed to fetch interaction");
                    const data = await res.json();
                    setCurrentInteraction(data);
                })
                .catch(() => {
                    setCurrentInteraction(null);
                });
        } else {
            setCurrentInteraction(null);
        }
    }, [open, interactionId]);

    const handleLoadSample = () => {
        if (currentInteraction) {
            setCurrentInteraction({
                ...currentInteraction,
                note: SAMPLE_CLINICAL_TRANSCRIPT,
            });
        }
    };

    if (!currentInteraction) {
        return null;
    }

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="w-full max-w-md sm:max-w-lg md:max-w-xl max-h-[85vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle>Interaction Details</DialogTitle>
                </DialogHeader>

                <div className="flex flex-col gap-4 overflow-y-auto">
                    <SummarySection
                        interaction={currentInteraction}
                        note={currentInteraction.note || ""}
                        onInteractionUpdate={setCurrentInteraction}
                        onLoadSample={handleLoadSample}
                    />
                    <NotesSection
                        interaction={currentInteraction}
                        onInteractionUpdate={setCurrentInteraction}
                        onLoadSample={handleLoadSample}
                    />
                </div>

                <div className="pt-4 border-t flex justify-end">
                    <Button variant="secondary" onClick={onClose}>
                        Close
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}
