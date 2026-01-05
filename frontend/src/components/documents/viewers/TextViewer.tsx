"use client";

import { DocumentViewerProps } from "./types";

export function TextViewer({ document, onLoadSuccess, onLoadError }: DocumentViewerProps) {
  return (
    <div className="w-full">
      <iframe
        src={document.fileUrl}
        className="w-full h-[70vh] border-0"
        title={document.title}
        onLoad={() => onLoadSuccess?.()}
        onError={(e) => onLoadError?.(new Error("Failed to load text file"))}
      />
    </div>
  );
}

export const TextViewerMetadata = {
  supportsZoom: false,
  supportsPagination: false,
  requiresDownload: false,
};
