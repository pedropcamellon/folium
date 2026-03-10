"use client";

import { useState } from "react";

import { Document, Page, pdfjs } from "react-pdf";

// Types
import { DocumentViewerProps } from "./types";

// Configure PDF.js worker (client-side only)
if (typeof window !== "undefined") {
    pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;
}

interface PDFViewerProps extends DocumentViewerProps {
    onPageChange?: (pageNumber: number, totalPages: number) => void;
}

export function PDFViewer({
    document,
    scale,
    onLoadSuccess,
    onLoadError,
    onPageChange,
}: PDFViewerProps) {
    const [numPages, setNumPages] = useState<number>(0);
    const [pageNumber, setPageNumber] = useState(1);
    const [loading, setLoading] = useState(true);

    const handleDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
        setNumPages(numPages);
        setLoading(false);
        onLoadSuccess?.();
        onPageChange?.(pageNumber, numPages);
    };

    const handleDocumentLoadError = (error: Error) => {
        setLoading(false);
        onLoadError?.(error);
    };

    return (
        <div className="flex flex-col items-center gap-4">
            {loading && <p className="text-muted-foreground">Loading PDF...</p>}

            <Document
                file={document.fileUrl}
                onLoadSuccess={handleDocumentLoadSuccess}
                onLoadError={handleDocumentLoadError}
                loading=""
            >
                <Page
                    pageNumber={pageNumber}
                    scale={scale}
                    renderTextLayer={false}
                    renderAnnotationLayer={false}
                />
            </Document>

            {!loading && numPages > 0 && (
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => {
                            const newPage = Math.max(1, pageNumber - 1);
                            setPageNumber(newPage);
                            onPageChange?.(newPage, numPages);
                        }}
                        disabled={pageNumber <= 1}
                        className="px-3 py-1 text-sm border rounded disabled:opacity-50"
                    >
                        Previous
                    </button>
                    <span className="text-sm">
                        Page {pageNumber} of {numPages}
                    </span>
                    <button
                        onClick={() => {
                            const newPage = Math.min(numPages, pageNumber + 1);
                            setPageNumber(newPage);
                            onPageChange?.(newPage, numPages);
                        }}
                        disabled={pageNumber >= numPages}
                        className="px-3 py-1 text-sm border rounded disabled:opacity-50"
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
}

export const PDFViewerMetadata = {
    supportsZoom: true,
    supportsPagination: true,
    requiresDownload: false,
};
