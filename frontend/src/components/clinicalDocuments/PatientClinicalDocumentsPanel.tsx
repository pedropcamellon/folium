import { useEffect, useState } from "react";
import { listClinicalDocuments } from "@/services/clinicalDocumentService";
import { ClinicalDocument } from "@/types/clinicalDocument";

interface PatientClinicalDocumentsPanelProps {
    patientId: string;
}

export function PatientClinicalDocumentsPanel({ patientId }: PatientClinicalDocumentsPanelProps) {
    const [documents, setDocuments] = useState<ClinicalDocument[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setLoading(true);
        setError(null);
        listClinicalDocuments(patientId)
            .then(setDocuments)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, [patientId]);

    if (loading) return <div>Loading documents...</div>;
    if (error) return <div className="text-red-500">{error}</div>;
    if (!documents.length) return <div>No documents found.</div>;

    return (
        <ul className="divide-y divide-slate-200">
            {documents.map((doc) => (
                <li key={doc.id} className="py-2">
                    <span className="font-medium">{doc.title}</span>
                    <span className="ml-2 text-xs bg-slate-100 rounded px-2 py-0.5">{doc.typeLabel}</span>
                    <span className="ml-2 text-xs text-slate-500">{new Date(doc.createdAt).toLocaleDateString()}</span>
                    <div className="text-slate-600 text-sm mt-1">{doc.summary || "No summary."}</div>
                </li>
            ))}
        </ul>
    );
}
