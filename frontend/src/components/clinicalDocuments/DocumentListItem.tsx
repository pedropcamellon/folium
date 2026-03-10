import { ClinicalDocument } from "@/types/clinicalDocument";
import { Download, Eye, Paperclip, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";

interface DocumentListItemProps {
    document: ClinicalDocument;
    onView: (doc: ClinicalDocument) => void;
    onDownload: (doc: ClinicalDocument) => void;
    onDelete: (doc: ClinicalDocument) => void;
}

export function DocumentListItem({
    document,
    onView,
    onDownload,
    onDelete,
}: DocumentListItemProps) {
    return (
        <li className="py-2 flex justify-between items-start">
            <div className="flex-1">
                <span className="font-medium">{document.title}</span>
                <span className="ml-2 text-xs bg-slate-100 rounded px-2 py-0.5">
                    {document.type}
                </span>
                <span className="ml-2 text-xs text-slate-500">
                    {new Date(document.createdAt).toLocaleDateString()}
                </span>
                {document.fileName && (
                    <span className="ml-2 text-xs text-blue-600 inline-flex items-center gap-1">
                        <Paperclip className="w-3 h-3" />
                        {document.fileName}
                    </span>
                )}
                <div className="text-slate-600 text-sm mt-1">
                    {document.summary || "No summary."}
                </div>
            </div>

            <div className="flex gap-1 ml-2">
                {document.fileUrl && (
                    <>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onView(document)}
                            title="View document"
                        >
                            <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onDownload(document)}
                            title="Download document"
                        >
                            <Download className="w-4 h-4" />
                        </Button>
                    </>
                )}
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(document)}
                    title="Delete document"
                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                >
                    <Trash2 className="w-4 h-4" />
                </Button>
            </div>
        </li>
    );
}
