import {
    ClinicalDocument,
    ClinicalDocumentCategory,
} from "@/types/clinicalDocument";

import { API_ENDPOINTS, apiJson, apiRequest, apiUpload } from "@/lib/api";

export async function listClinicalDocuments(
    patientId: string
): Promise<ClinicalDocument[]> {
    const url = API_ENDPOINTS.documentsByPatient(patientId);
    return apiJson<ClinicalDocument[]>(url);
}

export async function getClinicalDocument(
    id: string
): Promise<ClinicalDocument> {
    return apiJson<ClinicalDocument>(API_ENDPOINTS.document(id));
}

export async function deleteClinicalDocument(id: string): Promise<void> {
    const res = await apiRequest(API_ENDPOINTS.document(id), {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete document");
}

export interface UploadDocumentParams {
    file: File;
    patientId: string;
    category: ClinicalDocumentCategory;
    title: string;
    onProgress?: (progress: number) => void;
}

export async function uploadDocument(
    params: UploadDocumentParams
): Promise<ClinicalDocument> {
    const { file, patientId, category, title, onProgress } = params;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("patientId", patientId);
    formData.append("category", category);
    formData.append("title", title);

    return apiUpload<ClinicalDocument>(
        API_ENDPOINTS.documentUpload,
        formData,
        onProgress
    );
}
