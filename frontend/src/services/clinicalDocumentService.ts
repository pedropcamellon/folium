import { ClinicalDocument, ClinicalNoteDocument } from "@/types/clinicalDocument";
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