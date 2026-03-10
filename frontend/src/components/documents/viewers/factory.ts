import dynamic from "next/dynamic";

// Types
import { ClinicalDocument } from "@/types/clinicalDocument";

import { ImageViewer, ImageViewerMetadata } from "./ImageViewer";
import { TextViewer, TextViewerMetadata } from "./TextViewer";
import {
    UnsupportedViewer,
    UnsupportedViewerMetadata,
} from "./UnsupportedViewer";
import { DocumentViewerProps, ViewerMetadata } from "./types";

// Dynamic import for PDFViewer to avoid SSR issues
const PDFViewer = dynamic(
    () => import("./PDFViewer").then((mod) => mod.PDFViewer),
    {
        ssr: false,
    }
);

const PDFViewerMetadata = {
    supportsZoom: true,
    supportsPagination: true,
    requiresDownload: false,
};

interface ViewerConfig {
    component: React.ComponentType<DocumentViewerProps>;
    metadata: ViewerMetadata;
    canHandle: (mimeType: string) => boolean;
}

class DocumentViewerFactory {
    private viewers: ViewerConfig[] = [
        {
            component: PDFViewer,
            metadata: PDFViewerMetadata,
            canHandle: (mimeType: string) => mimeType === "application/pdf",
        },
        {
            component: ImageViewer,
            metadata: ImageViewerMetadata,
            canHandle: (mimeType: string) => {
                const imageTypes = [
                    "image/jpeg",
                    "image/jpg",
                    "image/png",
                    "image/gif",
                    "image/webp",
                    "image/svg+xml",
                ];
                return imageTypes.includes(mimeType);
            },
        },
        {
            component: TextViewer,
            metadata: TextViewerMetadata,
            canHandle: (mimeType: string) => mimeType === "text/plain",
        },
    ];

    private fallbackViewer: ViewerConfig = {
        component: UnsupportedViewer,
        metadata: UnsupportedViewerMetadata,
        canHandle: () => true,
    };

    /**
     * Get the appropriate viewer component based on document MIME type
     */
    getViewer(document: ClinicalDocument): ViewerConfig {
        const mimeType = this.detectMimeType(document);
        const viewer = this.viewers.find((v) => v.canHandle(mimeType));
        return viewer || this.fallbackViewer;
    }

    /**
     * Detect MIME type from document metadata or file extension
     */
    private detectMimeType(document: ClinicalDocument): string {
        // Priority 1: Use stored mimeType
        if (document.mimeType) {
            return document.mimeType;
        }

        // Priority 2: Detect from file extension
        if (document.fileName) {
            const extension = document.fileName.split(".").pop()?.toLowerCase();
            return this.extensionToMimeType(extension || "");
        }

        // Priority 3: Detect from fileUrl
        if (document.fileUrl) {
            const extension = document.fileUrl.split(".").pop()?.toLowerCase();
            return this.extensionToMimeType(extension || "");
        }

        return "application/octet-stream"; // Unknown type
    }

    /**
     * Map file extension to MIME type
     */
    private extensionToMimeType(extension: string): string {
        const mimeMap: Record<string, string> = {
            // Documents
            pdf: "application/pdf",
            doc: "application/msword",
            docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            txt: "text/plain",

            // Images
            jpg: "image/jpeg",
            jpeg: "image/jpeg",
            png: "image/png",
            gif: "image/gif",
            webp: "image/webp",
            svg: "image/svg+xml",

            // Archives
            zip: "application/zip",
            rar: "application/x-rar-compressed",
        };

        return mimeMap[extension] || "application/octet-stream";
    }

    /**
     * Register a custom viewer (for extensibility)
     */
    registerViewer(config: ViewerConfig): void {
        this.viewers.unshift(config); // Add to beginning for priority
    }

    /**
     * Get all supported MIME types
     */
    getSupportedMimeTypes(): string[] {
        return [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            "text/plain",
        ];
    }
}

// Export singleton instance
export const documentViewerFactory = new DocumentViewerFactory();

// Export factory class for testing/extension
export { DocumentViewerFactory };
