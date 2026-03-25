/**
 * Custom hook for interaction form logic
 * Handles form state, validation, submission, and error handling
 */
import { useState } from "react";

import { mutate } from "swr";

import { API_ENDPOINTS, apiRequest } from "@/lib/api";

export interface InteractionFormData {
    type: string;
    title: string;
    description: string;
    interactionDate: string;
    location: string;
    providerId: string;
    providerName: string;
}

interface UseInteractionFormProps {
    patientId: string;
    onSuccess?: () => void;
}

interface UseInteractionFormReturn {
    formData: InteractionFormData;
    loading: boolean;
    error: string | null;
    setFormData: React.Dispatch<React.SetStateAction<InteractionFormData>>;
    updateField: (field: keyof InteractionFormData, value: string) => void;
    handleSubmit: (e: React.FormEvent) => Promise<void>;
    resetForm: () => void;
}

const getInitialFormData = (): InteractionFormData => ({
    type: "",
    title: "",
    description: "",
    interactionDate: new Date().toISOString().slice(0, 16), // YYYY-MM-DDTHH:mm
    location: "",
    providerId: "",
    providerName: "",
});

export function useInteractionForm({
    patientId,
    onSuccess,
}: UseInteractionFormProps): UseInteractionFormReturn {
    const [formData, setFormData] =
        useState<InteractionFormData>(getInitialFormData());
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const updateField = (field: keyof InteractionFormData, value: string) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
    };

    const resetForm = () => {
        setFormData(getInitialFormData());
        setError(null);
    };

    const validate = (): boolean => {
        if (!formData.type || !formData.title || !formData.interactionDate) {
            setError("Please fill in all required fields (Type, Title, Date)");
            return false;
        }
        return true;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!validate()) {
            return;
        }

        setLoading(true);

        try {
            const payload = {
                patientId,
                type: formData.type,
                title: formData.title,
                description: formData.description || undefined,
                interactionDate: new Date(
                    formData.interactionDate
                ).toISOString(),
                location: formData.location || undefined,
                providerId: formData.providerId || undefined,
                providerName: formData.providerName || undefined,
                isCompliant: true,
            };

            const response = await apiRequest(API_ENDPOINTS.interactions, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.detail ||
                        `Failed to create interaction: ${response.statusText}`
                );
            }

            // Refresh interactions list for this patient
            await mutate(API_ENDPOINTS.interactionsByPatient(patientId));

            // Success callback
            if (onSuccess) {
                onSuccess();
            }

            resetForm();
        } catch (err) {
            console.error("Error creating interaction:", err);
            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to create interaction"
            );
        } finally {
            setLoading(false);
        }
    };

    return {
        formData,
        loading,
        error,
        setFormData,
        updateField,
        handleSubmit,
        resetForm,
    };
}
