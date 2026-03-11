import { useCallback, useRef, useState } from "react";

import { API_ENDPOINTS } from "@/lib/api";

export enum AudioState {
    IDLE = "idle",
    LOADED = "loaded", // Audio loaded from backend
    RECORDING = "recording",
    RECORDED = "recorded",
    SUBMITTING = "submitting",
    SUBMITTED = "submitted",
    ERROR = "error",
}

export function useInteractionAudio(interactionId: string) {
    const [audioState, setAudioState] = useState<AudioState>(AudioState.IDLE);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [recordingError, setRecordingError] = useState<string | null>(null);
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
        null
    );

    const audioChunks = useRef<Blob[]>([]);

    const startRecording = async () => {
        setRecordingError(null);
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });
            const recorder = new window.MediaRecorder(stream);
            audioChunks.current = [];

            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunks.current.push(e.data);
                }
            };

            recorder.onstop = () => {
                const audioBlob = new Blob(audioChunks.current, {
                    type: "audio/webm",
                });
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
            audioBlob = await fetch(audioUrl).then((r) => r.blob());
        } catch {
            setSubmitError("Failed to load audio blob");
            setAudioState(AudioState.ERROR);
            return;
        }

        setAudioState(AudioState.SUBMITTING);

        try {
            const formData = new FormData();
            formData.append("audio", audioBlob, "audio.webm");

            const res = await fetch(
                `${API_ENDPOINTS.interaction(interactionId)}/audio`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!res.ok) {
                let errorMsg = "Failed to submit audio";
                try {
                    const err = await res.json();
                    errorMsg = err?.error || errorMsg;
                } catch {}
                throw new Error(errorMsg);
            }

            setAudioState(AudioState.SUBMITTED);
            // Parent component will handle polling for transcription
        } catch (e: any) {
            setSubmitError(e?.message || "Submission failed");
            setAudioState(AudioState.ERROR);
        }
    };

    const cleanup = () => {
        setAudioState(AudioState.IDLE);
        setAudioUrl(null);
    };

    const loadExistingAudio = useCallback(async () => {
        try {
            const res = await fetch(API_ENDPOINTS.interaction(interactionId));
            if (res.ok) {
                const data = await res.json();
                if (data.metadata?.audio) {
                    const audioRes = await fetch(
                        `${API_ENDPOINTS.interaction(interactionId)}/audio`
                    );
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
    }, [interactionId]);

    return {
        audioState,
        audioUrl,
        recordingError,
        submitError,
        startRecording,
        stopRecording,
        submitAudio,
        cleanup,
        loadExistingAudio,
    };
}
