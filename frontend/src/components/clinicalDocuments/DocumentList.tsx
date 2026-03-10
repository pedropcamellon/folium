import { ClinicalDocument } from "@/types/clinicalDocument";

import { DocumentListItem } from "./DocumentListItem";

interface DocumentListProps {
    documents: ClinicalDocument[];
    onView: (doc: ClinicalDocument) => void;
    onDownload: (doc: ClinicalDocument) => void;
    onDelete: (doc: ClinicalDocument) => void;
}

export function DocumentList({
    documents,
    onView,
    onDownload,
    onDelete,
}: DocumentListProps) {
    if (documents.length === 0) {
        return (
            <div className="text-slate-500 text-sm py-4">
                No documents found.
            </div>
        );
    }

    return (
        <ul className="divide-y divide-slate-200">
            {documents.map((doc) => (
                <DocumentListItem
                    key={doc.id}
                    document={doc}
                    onView={onView}
                    onDownload={onDownload}
                    onDelete={onDelete}
                />
            ))}
        </ul>
    );
}
