import { useState, useRef } from 'react';
import { API_ENDPOINTS } from '@/lib/api';

export enum AudioState {
    IDLE = 'idle',
    LOADED = 'loaded',          // Audio loaded from backend
    RECORDING = 'recording',
    RECORDED = 'recorded',
    SUBMITTING = 'submitting',
    SUBMITTED = 'submitted',
    POLLING = 'polling',
    ERROR = 'error'
}

export function useInteractionAudio(interactionId: string, onTranscriptUpdate?: (note: string) => void) {
    const [audioState, setAudioState] = useState<AudioState>(AudioState.IDLE);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [recordingError, setRecordingError] = useState<string | null>(null);
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

    const audioChunks = useRef<Blob[]>([]);
    const pollingAbortRef = useRef<AbortController | null>(null);

    const startRecording = async () => {
        setRecordingError(null);
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new window.MediaRecorder(stream);
            audioChunks.current = [];

            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunks.current.push(e.data);
                }
            };

            recorder.onstop = () => {
                const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
                setAudioUrl(URL.createObjectURL(audioBlob));
                setAudioState(AudioState.RECORDED);
            };

            recorder.start();
            setMediaRecorder(recorder);
            setAudioState(AudioState.RECORDING);
        } catch (err) {
            setRecordingError("Microphone access denied or unavailable.");
            setAudioState(AudioState.ERROR);
        }
    };

    const stopRecording = () => {
        if (mediaRecorder && audioState === AudioState.RECORDING) {
            mediaRecorder.stop();
        }
    };

    const submitAudio = async () => {
        setSubmitError(null);

        if (!audioUrl) {
            setSubmitError("No audio to submit");
            return;
        }

        let audioBlob: Blob;
        try {
            audioBlob = await fetch(audioUrl).then(r => r.blob());
        } catch {
            setSubmitError("Failed to load audio blob");
            setAudioState(AudioState.ERROR);
            return;
        }

        setAudioState(AudioState.SUBMITTING);

        try {
            const formData = new FormData();
            formData.append("audio", audioBlob, "audio.webm");

            const res = await fetch(`${API_ENDPOINTS.interaction(interactionId)}/audio`, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) {
                let errorMsg = "Failed to submit audio";
                try {
                    const err = await res.json();
                    errorMsg = err?.error || errorMsg;
                } catch { }
                throw new Error(errorMsg);
            }

            setAudioState(AudioState.SUBMITTED);

            // Brief success message, then start polling
            setTimeout(() => {
                setAudioState(AudioState.POLLING);
                startPolling();
            }, 2000);

        } catch (e: any) {
            setSubmitError(e?.message || "Submission failed");
            setAudioState(AudioState.ERROR);
        }
    };

    const startPolling = async () => {
        const abortController = new AbortController();
        pollingAbortRef.current = abortController;

        const maxAttempts = 5;
        const interval = 2000;

        // Get initial note state and metadata
        let initialNote = '';
        let initialUpdatedAt = '';
        try {
            const initialRes = await fetch(API_ENDPOINTS.interaction(interactionId));
            if (initialRes.ok) {
                const initialData = await initialRes.json();
                initialNote = initialData.note || '';
                initialUpdatedAt = initialData.updatedAt || '';
            }
        } catch (e) {
            console.error('Failed to get initial interaction state:', e);
        }

        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            if (abortController.signal.aborted) break;

            await new Promise(res => setTimeout(res, interval));

            if (abortController.signal.aborted) break;

            try {
                const noteRes = await fetch(API_ENDPOINTS.interaction(interactionId));

                if (!noteRes.ok) {
                    console.error(`Polling attempt ${attempt + 1} failed: ${noteRes.status} ${noteRes.statusText}`);
                    continue;
                }

                const data = await noteRes.json();

                // Check if transcription failed
                const transcriptionError = data.metadata?.audio?.transcriptionError;
                if (transcriptionError) {
                    console.error('Transcription failed:', transcriptionError);
                    setAudioState(AudioState.ERROR);
                    setSubmitError(`Transcription failed: ${transcriptionError}`);
                    pollingAbortRef.current = null;
                    return;
                }

                // Check if interaction was updated (transcription completed)
                const wasUpdated = data.updatedAt !== initialUpdatedAt;
                const noteChanged = data.note && data.note !== initialNote;
                const hasTranscript = data.note && data.note.includes('[Audio Transcript');

                // Stop polling if: updated, note changed, or transcript already present
                if (wasUpdated || noteChanged || hasTranscript) {
                    console.log(`Transcript updated after ${attempt + 1} poll(s)`);
                    onTranscriptUpdate?.(data.note || '');
                    setAudioState(AudioState.IDLE);
                    pollingAbortRef.current = null;
                    return;
                }

                console.log(`Polling attempt ${attempt + 1}/${maxAttempts} - no update yet`);

            } catch (e) {
                console.error(`Polling attempt ${attempt + 1} error:`, e);
                // Continue polling on network errors
            }
        }

        // Polling timeout - transcription may still be processing
        console.warn('Polling timeout - transcription may still be in progress');
        setAudioState(AudioState.IDLE);
        pollingAbortRef.current = null;
    };

    const cleanup = () => {
        setAudioState(AudioState.IDLE);
        setAudioUrl(null);
        if (pollingAbortRef.current) {
            pollingAbortRef.current.abort();
            pollingAbortRef.current = null;
        }
    };

    const loadExistingAudio = async () => {
        try {
            const res = await fetch(API_ENDPOINTS.interaction(interactionId));
            if (res.ok) {
                const data = await res.json();
                if (data.metadata?.audio) {
                    const audioRes = await fetch(`${API_ENDPOINTS.interaction(interactionId)}/audio`);
                    if (audioRes.ok) {
                        const audioBlob = await audioRes.blob();
                        setAudioUrl(URL.createObjectURL(audioBlob));
                        setAudioState(AudioState.LOADED);
                    }
                }
            }
        } catch {
            // Ignore errors loading existing audio
        }
    };

    return {
        audioState,
        audioUrl,
        recordingError,
        submitError,
        startRecording,
        stopRecording,
        submitAudio,
        cleanup,
        loadExistingAudio
    };
}
