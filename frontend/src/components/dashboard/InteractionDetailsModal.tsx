import { useState, useRef, useEffect } from "react";
import { FaMicrophone, FaPause } from "react-icons/fa";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

import { API_ENDPOINTS } from "@/lib/api";
import { useInteractionAudio, AudioState } from "@/hooks/useInteractionAudio";
import { useInteractionSummary, SummaryState } from "@/hooks/useInteractionSummary";

// Types
import { PatientInteraction } from "@/types";

// State enums
enum NoteEditState {
    VIEWING = 'viewing',
    EDITING = 'editing',
    SAVING = 'saving',
}

// Props
interface PatientInteractionDetailsModalProps {
    interactionId: string;
    open: boolean;
    onClose: () => void;
}

export default function PatientInteractionDetailsModal({ interactionId, open, onClose }: PatientInteractionDetailsModalProps) {
    // -------------------- State and refs --------------------
    // Data state
    const [currentInteraction, setCurrentInteraction] = useState<PatientInteraction | null>(null);

    // Summary hook
    const {
        summary,
        summaryState,
        summaryError,
        generateSummaryFromTranscript,
        setSummary,
    } = useInteractionSummary((formattedSummary, structuredData) => {
        // Update interaction with structured summary on success
        if (currentInteraction) {
            setCurrentInteraction({
                ...currentInteraction,
                summary: formattedSummary,
                structuredSummary: structuredData,
                chiefComplaint: structuredData.chief_complaint,
                clinicalAssessment: structuredData.assessment,
                treatmentPlan: structuredData.plan,
            });
        }
    });

    // UI state
    const [note, setNote] = useState("");
    const [noteEditState, setNoteEditState] = useState<NoteEditState>(NoteEditState.VIEWING);
    const [editedNote, setEditedNote] = useState("");
    const [lastSavedNote, setLastSavedNote] = useState("");
    const [saveNoteError, setSaveNoteError] = useState<string | null>(null);
    const noteInputRef = useRef<HTMLTextAreaElement>(null);

    // Audio hook
    const {
        audioState,
        audioUrl,
        recordingError,
        submitError,
        startRecording,
        stopRecording,
        submitAudio,
        cleanup: cleanupAudio,
        loadExistingAudio
    } = useInteractionAudio(interactionId, (transcriptNote) => {
        setNote(transcriptNote);
        setLastSavedNote(transcriptNote);
        if (currentInteraction) {
            setCurrentInteraction({ ...currentInteraction, note: transcriptNote });
        }
    });

    // -------------------- Data fetching and sync --------------------
    // Fetch interaction details when modal opens or id changes
    useEffect(() => {
        if (open && interactionId) {
            fetch(API_ENDPOINTS.interaction(interactionId))
                .then(async (res) => {
                    if (!res.ok) throw new Error('Failed to fetch interaction');
                    const data = await res.json();
                    setCurrentInteraction(data);
                    setNote(data.note || "");
                    setLastSavedNote(data.note || "");

                    // Load existing audio if available
                    loadExistingAudio();
                })
                .catch(() => {
                    setCurrentInteraction(null);
                    setNote("");
                    setLastSavedNote("");
                });
        } else {
            setCurrentInteraction(null);
            setNote("");
            setLastSavedNote("");
            cleanupAudio();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [open, interactionId]);

    // Use summary field from currentInteraction
    useEffect(() => {
        if (currentInteraction) {
            setSummary(currentInteraction.summary || "");
        }
    }, [currentInteraction, setSummary]);

    // When entering edit mode, set editedNote and focus
    useEffect(() => {
        if (noteEditState === NoteEditState.EDITING) {
            setEditedNote(note);
            setTimeout(() => noteInputRef.current?.focus(), 0);
        }
    }, [noteEditState, note]);

    // -------------------- Handlers --------------------
    // Generate clinical summary
    const handleGenerateSummary = () => {
        generateSummaryFromTranscript(note, currentInteraction?.type);
    };

    // Discard note edits
    const handleDiscardNote = () => {
        setEditedNote(lastSavedNote);
        setNoteEditState(NoteEditState.VIEWING);
    };

    // Save note
    const handleSaveNote = async () => {
        setNoteEditState(NoteEditState.SAVING);
        setSaveNoteError(null);
        try {
            const res = await fetch(API_ENDPOINTS.interactionNote(currentInteraction?.id || ""), {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ note: editedNote }),
            });
            if (!res.ok) throw new Error('Failed to save note');
            setNote(editedNote);
            setLastSavedNote(editedNote);
            setNoteEditState(NoteEditState.VIEWING);
        } catch (e) {
            setSaveNoteError("Failed to save note");
            setNoteEditState(NoteEditState.EDITING);
        }
    };

    // -------------------- UI --------------------
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
                    {/* Summary */}
                    <div>
                        <div className="flex items-center justify-between mb-1">
                            <div className="font-semibold">Clinical Summary</div>
                            <Button
                                size="sm"
                                variant="outline"
                                onClick={handleGenerateSummary}
                                disabled={summaryState === SummaryState.GENERATING || !note}
                            >
                                {summaryState === SummaryState.GENERATING ? "Generating..." : "Generate Summary"}
                            </Button>
                        </div>
                        {summaryError && (
                            <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 flex items-center gap-2">
                                <span>Failed to generate summary</span>
                            </div>
                        )}
                        <div className="whitespace-pre-wrap text-sm border p-3 rounded bg-slate-50">
                            {summary || "No summary available. Generate one from your notes."}
                        </div>
                    </div>

                    {/* Notes */}
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="font-semibold">Notes</div>
                            {audioState !== AudioState.RECORDING ? (
                                <Button size="icon" variant="outline" onClick={startRecording} aria-label="Record">
                                    <FaMicrophone />
                                </Button>
                            ) : (
                                <Button size="icon" variant="destructive" onClick={stopRecording} aria-label="Stop Recording">
                                    <FaPause className="animate-pulse" />
                                </Button>
                            )}
                            <span className="text-xs text-slate-500">
                                {audioState === AudioState.RECORDING ? "Recording..." :
                                    audioState === AudioState.POLLING ? "Processing transcript..." :
                                        "Voice Recording"}
                            </span>
                            {audioUrl && (
                                <audio controls src={audioUrl} className="ml-2 h-10" />
                            )}
                        </div>
                        {audioState === AudioState.RECORDED && (
                            <div className="flex items-center gap-2 mb-3">
                                <span className="text-xs text-slate-600">Looks good?</span>
                                <Button size="sm" variant="default" onClick={submitAudio}>
                                    Submit Audio
                                </Button>
                            </div>
                        )}
                        {audioState === AudioState.SUBMITTING && (
                            <div className="flex items-center gap-2 mb-3">
                                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                                </svg>
                                <span className="text-xs text-slate-600">Uploading...</span>
                            </div>
                        )}
                        {audioState === AudioState.SUBMITTED && (
                            <div className="text-xs text-green-600 mb-3">Audio submitted successfully!</div>
                        )}
                        {audioState === AudioState.ERROR && submitError && (
                            <div className="text-xs text-red-500 mb-3">{submitError}</div>
                        )}
                        {recordingError && <div className="text-xs text-red-500 mb-1">{recordingError}</div>}

                        {noteEditState === NoteEditState.VIEWING ? (
                            <>
                                <div className="whitespace-pre-wrap text-sm mb-2 border p-2 rounded">
                                    {note || "No notes yet."}
                                </div>
                                <Button size="sm" variant="outline" onClick={() => setNoteEditState(NoteEditState.EDITING)}>
                                    Edit Note
                                </Button>
                            </>
                        ) : (
                            <>
                                <textarea
                                    ref={noteInputRef}
                                    value={editedNote}
                                    onChange={(e) => setEditedNote(e.target.value)}
                                    className="w-full border p-2 rounded text-sm mb-2 min-h-[100px]"
                                    placeholder="Type your notes here..."
                                />
                                <div className="flex items-center gap-2">
                                    <Button size="sm" onClick={handleSaveNote} disabled={noteEditState === NoteEditState.SAVING}>
                                        {noteEditState === NoteEditState.SAVING ? "Saving..." : "Save"}
                                    </Button>
                                    <Button size="sm" variant="ghost" onClick={handleDiscardNote}>
                                        Cancel
                                    </Button>
                                </div>
                                {saveNoteError && <div className="text-xs text-red-500 mt-1">{saveNoteError}</div>}
                            </>
                        )}
                    </div>
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
