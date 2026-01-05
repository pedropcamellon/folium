import { ClinicalDocument, ClinicalNoteDocument, ClinicalDocumentType } from "@/types/clinicalDocument";
import { API_ENDPOINTS } from "@/lib/api";

export async function listClinicalDocuments(patientId: string, types?: string[]): Promise<ClinicalDocument[]> {
    const url = API_ENDPOINTS.documentsByPatient(patientId, types);
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch documents");
    return res.json();
}

export async function getClinicalDocument(id: string): Promise<ClinicalDocument> {
    const res = await fetch(API_ENDPOINTS.document(id));
    if (!res.ok) throw new Error("Failed to fetch document");
    return res.json();
}

export async function updateClinicalNote(id: string, doc: Partial<ClinicalNoteDocument>): Promise<ClinicalNoteDocument> {
    const res = await fetch(API_ENDPOINTS.document(id), {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(doc),
    });
    if (!res.ok) throw new Error("Failed to update document");
    return res.json();
}

export async function deleteClinicalDocument(id: string): Promise<void> {
    const res = await fetch(API_ENDPOINTS.document(id), { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete document");
}

export async function createClinicalNote(
    patientId: string, 
    doc: Omit<ClinicalNoteDocument, "id" | "createdAt" | "updatedAt" | "createdBy" | "updatedBy" | "typeLabel">
): Promise<ClinicalNoteDocument> {
    const res = await fetch(API_ENDPOINTS.documents, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...doc, patientId }),
    });
    if (!res.ok) throw new Error("Failed to create document");
    return res.json();
}

export interface UploadDocumentParams {
    file: File;
    patientId: string;
    type: ClinicalDocumentType;
    title: string;
    summary?: string;
    interactionId?: string;
    onProgress?: (progress: number) => void;
}

export async function uploadDocument(params: UploadDocumentParams): Promise<ClinicalDocument> {
    const { file, patientId, type, title, summary, interactionId, onProgress } = params;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('patientId', patientId);
    formData.append('type', type);
    formData.append('title', title);
    if (summary) formData.append('summary', summary);
    if (interactionId) formData.append('interactionId', interactionId);

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // Track upload progress
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable && onProgress) {
                const progress = Math.round((e.loaded / e.total) * 100);
                onProgress(progress);
            }
        };

        // Handle successful response
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response);
                } catch (error) {
                    reject(new Error('Failed to parse response'));
                }
            } else {
                reject(new Error(`Upload failed with status ${xhr.status}`));
            }
        };

        // Handle errors
        xhr.onerror = () => reject(new Error('Network error during upload'));
        xhr.onabort = () => reject(new Error('Upload aborted'));

        // Send request
        xhr.open('POST', API_ENDPOINTS.documentUpload);
        xhr.send(formData);
    });
}