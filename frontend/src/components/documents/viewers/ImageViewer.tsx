"use client";

import { DocumentViewerProps } from "./types";

export function ImageViewer({ document, scale, onLoadSuccess, onLoadError }: DocumentViewerProps) {
    return (
        <div className="flex justify-center items-center w-full h-full">
            <img
                src={document.fileUrl}
                alt={document.title}
                style={{
                    transform: `scale(${scale})`,
                    maxWidth: "100%",
                    maxHeight: "80vh",
                    width: "auto",
                    height: "auto",
                    transformOrigin: "center",
                }}
                className="object-contain transition-transform duration-200"
                onLoad={() => onLoadSuccess?.()}
                onError={(e) => onLoadError?.(new Error("Failed to load image"))}
            />
        </div>
    );
}

export const ImageViewerMetadata = {
  supportsZoom: true,
  supportsPagination: false,
  requiresDownload: false,
};
