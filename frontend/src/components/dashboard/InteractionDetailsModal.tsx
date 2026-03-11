import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";

import { TranscriptionState } from "@/hooks/useTranscription";

import { PatientInteraction } from "@/types";

import { NotesSection } from "./NotesSection";
import { SummarySection } from "./SummarySection";

interface PatientInteractionDetailsModalProps {
    interaction: PatientInteraction;
    open: boolean;
    onClose: () => void;
    onAudioSubmitted: () => void;
    transcriptionState: TranscriptionState;
}

export default function PatientInteractionDetailsModal({
    interaction,
    open,
    onClose,
    onAudioSubmitted,
    transcriptionState,
}: PatientInteractionDetailsModalProps) {
    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="w-full max-w-md sm:max-w-lg md:max-w-xl max-h-[85vh] flex flex-col">
                <DialogHeader>
                    <DialogTitle>Interaction Details</DialogTitle>
                </DialogHeader>

                <div className="flex flex-col gap-4 overflow-y-auto">
                    <SummarySection
                        interaction={interaction}
                        note={interaction.note || ""}
                        onInteractionUpdate={() => {}}
                    />
                    <NotesSection
                        interaction={interaction}
                        onInteractionUpdate={() => {}}
                        onAudioSubmitted={onAudioSubmitted}
                        transcriptionState={transcriptionState}
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
