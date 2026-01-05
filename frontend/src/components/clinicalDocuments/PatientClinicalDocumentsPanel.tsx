"use client";

import { useEffect, useState } from "react";
import { Upload, Eye, Download, Trash2 } from "lucide-react";

import { listClinicalDocuments, deleteClinicalDocument } from "@/services/clinicalDocumentService";
import { Button } from "@/components/ui/button";
import { DocumentUploadModal } from "@/components/documents/DocumentUploadModal";
import { DocumentViewerModal } from "@/components/documents/DocumentViewerModal";
import { DeleteDocumentDialog } from "@/components/documents/DeleteDocumentDialog";
import { API_ENDPOINTS } from "@/lib/api";

// Types
import { ClinicalDocument } from "@/types/clinicalDocument";

interface PatientClinicalDocumentsPanelProps {
    patientId: string;
}

export function PatientClinicalDocumentsPanel({ patientId }: PatientClinicalDocumentsPanelProps) {
    const [documents, setDocuments] = useState<ClinicalDocument[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [uploadModalOpen, setUploadModalOpen] = useState(false);
    const [viewerModalOpen, setViewerModalOpen] = useState(false);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [selectedDocument, setSelectedDocument] = useState<ClinicalDocument | null>(null);
    const [documentToDelete, setDocumentToDelete] = useState<ClinicalDocument | null>(null);

    const fetchDocuments = () => {
        setLoading(true);
        setError(null);
        listClinicalDocuments(patientId)
            .then(setDocuments)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        fetchDocuments();
    }, [patientId]);

    const handleUploadSuccess = () => {
        fetchDocuments(); // Refresh document list after successful upload
    };

    const handleViewDocument = async (doc: ClinicalDocument) => {
        // Fetch presigned URL from backend
        try {
            const viewUrl = API_ENDPOINTS.documentView(doc.id);
            const response = await fetch(viewUrl);

            if (!response.ok) {
                throw new Error("Failed to get document view URL");
            }

            // Backend redirects to presigned URL, get the final URL
            const presignedUrl = response.url;

            // Create a modified document with the presigned URL
            const docWithPresignedUrl = { ...doc, fileUrl: presignedUrl };
            setSelectedDocument(docWithPresignedUrl);
            setViewerModalOpen(true);
        } catch (err) {
            console.error("Error loading document:", err);
            alert("Failed to load document for viewing");
        }
    };

    const handleDownloadDocument = async (doc: ClinicalDocument) => {
        // Use backend download endpoint which returns presigned URL
        const downloadUrl = API_ENDPOINTS.documentDownload(doc.id);
        window.open(downloadUrl, "_blank");
    };

    const handleDeleteClick = (doc: ClinicalDocument) => {
        setDocumentToDelete(doc);
        setDeleteModalOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!documentToDelete) return;

        try {
            await deleteClinicalDocument(documentToDelete.id);
            fetchDocuments(); // Refresh list
        } catch (err) {
            console.error("Failed to delete document:", err);
            alert("Failed to delete document. Please try again.");
        }
    };

    if (loading) return <div>Loading documents...</div>;
    if (error) return <div className="text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold">Clinical Documents</h3>
                <Button onClick={() => setUploadModalOpen(true)} size="sm">
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Document
                </Button>
            </div>

            {!documents.length ? (
                <div className="text-slate-500 text-sm py-4">No documents found.</div>
            ) : (
                <ul className="divide-y divide-slate-200">
                    {documents.map((doc) => (
                        <li key={doc.id} className="py-2 flex justify-between items-start">
                            <div className="flex-1">
                                <span className="font-medium">{doc.title}</span>
                                <span className="ml-2 text-xs bg-slate-100 rounded px-2 py-0.5">{doc.type}</span>
                                <span className="ml-2 text-xs text-slate-500">
                                    {new Date(doc.createdAt).toLocaleDateString()}
                                </span>
                                {doc.fileName && (
                                    <span className="ml-2 text-xs text-blue-600">📎 {doc.fileName}</span>
                                )}
                                <div className="text-slate-600 text-sm mt-1">{doc.summary || "No summary."}</div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-1 ml-2">
                                {doc.fileUrl && (
                                    <>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleViewDocument(doc)}
                                            title="View document"
                                        >
                                            <Eye className="w-4 h-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDownloadDocument(doc)}
                                            title="Download document"
                                        >
                                            <Download className="w-4 h-4" />
                                        </Button>
                                    </>
                                )}
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleDeleteClick(doc)}
                                    title="Delete document"
                                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </Button>
                            </div>
                        </li>
                    ))}
                </ul>
            )}

            <DocumentUploadModal
                open={uploadModalOpen}
                onClose={() => setUploadModalOpen(false)}
                patientId={patientId}
                onUploadSuccess={handleUploadSuccess}
            />

            {selectedDocument && (
                <DocumentViewerModal
                    document={selectedDocument}
                    open={viewerModalOpen}
                    onClose={() => {
                        setViewerModalOpen(false);
                        setSelectedDocument(null);
                    }}
                />
            )}

            <DeleteDocumentDialog
                document={documentToDelete}
                open={deleteModalOpen}
                onClose={() => {
                    setDeleteModalOpen(false);
                    setDocumentToDelete(null);
                }}
                onConfirm={handleDeleteConfirm}
            />
        </div>
    );
}
