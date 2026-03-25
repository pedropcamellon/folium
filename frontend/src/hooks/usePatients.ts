import { useMemo, useState } from "react";

import useSWR from "swr";

import { API_ENDPOINTS, apiJson, apiRequest } from "@/lib/api";

import type { Patient } from "@/types";

export enum DataStatus {
    IDLE = "idle",
    LOADING = "loading",
    SUCCESS = "success",
    ERROR = "error",
}

interface PatientFormData {
    medicalRecordNumber: string;
    firstName: string;
    lastName: string;
    dateOfBirth: string;
    gender: string;
    contactInfo: string;
}

export function usePatients() {
    const { data, error, isLoading, mutate } = useSWR<Patient[]>(
        API_ENDPOINTS.patients,
        (url: string) => apiJson<Patient[]>(url),
        { refreshInterval: 10000 }
    );

    console.log("usePatients:", {
        endpoint: API_ENDPOINTS.patients,
        data,
        error,
        isLoading,
    });

    const [submitting, setSubmitting] = useState(false);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    // Derive status from SWR state
    const status: DataStatus = useMemo(() => {
        if (error) return DataStatus.ERROR;
        if (isLoading) return DataStatus.LOADING;
        if (data) return DataStatus.SUCCESS;
        return DataStatus.IDLE;
    }, [data, error, isLoading]);

    const createPatient = async (
        formData: PatientFormData
    ): Promise<boolean> => {
        setSubmitting(true);
        setErrorMsg(null);
        try {
            const res = await apiRequest(API_ENDPOINTS.patients, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });
            if (!res.ok) {
                const err = await res.json();
                setErrorMsg(err.error || "Failed to add patient");
                return false;
            }
            await mutate();
            return true;
        } catch (err) {
            setErrorMsg("Network error");
            return false;
        } finally {
            setSubmitting(false);
        }
    };

    const updatePatient = async (
        patientId: string,
        formData: PatientFormData
    ): Promise<boolean> => {
        setSubmitting(true);
        setErrorMsg(null);
        try {
            const res = await apiRequest(API_ENDPOINTS.patient(patientId), {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });
            if (!res.ok) {
                const err = await res.json();
                setErrorMsg(err.error || "Failed to update patient");
                return false;
            }
            await mutate();
            return true;
        } catch (err) {
            setErrorMsg("Network error");
            return false;
        } finally {
            setSubmitting(false);
        }
    };

    const deletePatient = async (patientId: string): Promise<boolean> => {
        setErrorMsg(null);
        try {
            const res = await apiRequest(API_ENDPOINTS.patient(patientId), {
                method: "DELETE",
            });
            if (!res.ok) {
                setErrorMsg("Failed to delete patient");
                return false;
            }
            await mutate();
            return true;
        } catch (err) {
            setErrorMsg("Network error");
            return false;
        }
    };

    return {
        patients: data,
        status,
        submitting,
        errorMsg,
        createPatient,
        updatePatient,
        deletePatient,
    };
}
