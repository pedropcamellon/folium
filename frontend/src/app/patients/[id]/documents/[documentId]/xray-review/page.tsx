"use client";

import { useEffect, useState } from "react";

import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, ZoomIn, ZoomOut } from "lucide-react";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { XrayReviewInsights } from "@/components/documents/XrayReviewInsights";
import { XrayReviewImage } from "@/components/documents/XrayReviewImage";
import { Button } from "@/components/ui/button";

import { API_ENDPOINTS, apiRequest } from "@/lib/api";
import { permissions } from "@/lib/permissions";
import { getClinicalDocument } from "@/services/clinicalDocumentService";
import type {
    Attachment,
    ClinicalDocumentAttachmentView,
} from "@/types/clinicalDocument";

export default function XrayReviewPage() {
    const params = useParams<{ id: string; documentId: string }>();

    return (
        <DashboardLayout requiredPermissions={[permissions.documentsRead]}>
            <XrayReviewPageContent
                patientId={params.id}
                documentId={params.documentId}
            />
        </DashboardLayout>
    );
}

function XrayReviewPageContent({
    patientId,
    documentId,
}: {
    patientId: string;
    documentId: string;
}) {
    const router = useRouter();
    const [document, setDocument] =
        useState<ClinicalDocumentAttachmentView | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [scale, setScale] = useState(1);

    useEffect(() => {
        let active = true;
        let fileUrl: string | null = null;
        setLoading(true);
        setError(null);
        setDocument(null);

        const loadDocument = async () => {
            try {
                const clinicalDocument =
                    await getClinicalDocument(documentId);
                if (clinicalDocument.patientId !== patientId) {
                    throw new Error("Document not found for this patient");
                }
                if (clinicalDocument.category !== "xray") {
                    throw new Error("This document is not marked as an X-ray");
                }

                const attachment: Attachment | undefined =
                    clinicalDocument.attachments.find((item) =>
                        ["image/jpeg", "image/jpg", "image/png"].includes(
                            item.mimeType.trim().toLowerCase()
                        )
                    );
                if (!attachment) {
                    throw new Error(
                        "X-ray review requires a JPEG or PNG image"
                    );
                }

                const response = await apiRequest(
                    API_ENDPOINTS.documentAttachmentDownload(
                        clinicalDocument.id,
                        attachment.id
                    )
                );
                if (!response.ok) {
                    throw new Error(
                        `Failed to load image (HTTP ${response.status})`
                    );
                }

                fileUrl = URL.createObjectURL(await response.blob());
                if (!active) {
                    URL.revokeObjectURL(fileUrl);
                    return;
                }
                setDocument({
                    ...clinicalDocument,
                    attachment,
                    fileUrl,
                });
            } catch (loadError) {
                if (active) {
                    setError(
                        loadError instanceof Error
                            ? loadError.message
                            : "Could not load the X-ray image"
                    );
                }
            } finally {
                if (active) setLoading(false);
            }
        };

        void loadDocument();

        return () => {
            active = false;
            if (fileUrl) URL.revokeObjectURL(fileUrl);
        };
    }, [documentId, patientId]);

    return (
        <div className="-m-8 flex min-h-[calc(100vh-4rem)] flex-col">
            <header className="flex flex-wrap items-center gap-4 border-b bg-background px-6 py-3">
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => router.push(`/patients/${patientId}`)}
                >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back to patient
                </Button>
                <div className="min-w-0 flex-1">
                    <h1 className="truncate text-lg font-semibold">
                        X-ray review
                    </h1>
                    {document && (
                        <p className="truncate text-sm text-muted-foreground">
                            {document.title}
                        </p>
                    )}
                </div>
            </header>

            {error && (
                <p role="alert" className="p-6 text-red-700">
                    {error}
                </p>
            )}

            {loading && (
                <p className="p-6 text-muted-foreground">Loading image...</p>
            )}

            {document && (
                <main className="grid min-h-0 flex-1 grid-cols-1 md:grid-cols-[minmax(300px,38%)_minmax(0,1fr)]">
                    <section className="min-h-0 border-b md:border-b-0 md:border-r">
                        <XrayReviewInsights
                            patientId={patientId}
                            clinicalDocumentId={documentId}
                        />
                    </section>
                    <section className="relative flex min-h-[50vh] min-w-0 items-center justify-center overflow-hidden bg-slate-950/5 p-4 md:min-h-0">
                        <XrayReviewImage
                            document={document}
                            scale={scale}
                            onLoadError={(imageError) =>
                                setError(imageError.message)
                            }
                        />
                        <div className="absolute right-4 top-1/2 z-10 flex -translate-y-1/2 flex-col gap-2 rounded-xl border bg-background/90 p-2 shadow-lg backdrop-blur">
                            <Button
                                variant="tertiary"
                                size="sm"
                                onClick={() =>
                                    setScale((current) =>
                                        Math.max(0.5, current - 0.2)
                                    )
                                }
                                disabled={scale <= 0.5}
                                aria-label="Zoom out"
                            >
                                <ZoomOut className="h-4 w-4" />
                            </Button>
                            <Button
                                variant="tertiary"
                                size="sm"
                                onClick={() => setScale(1)}
                                disabled={scale === 1}
                            >
                                {Math.round(scale * 100)}%
                            </Button>
                            <Button
                                variant="tertiary"
                                size="sm"
                                onClick={() =>
                                    setScale((current) =>
                                        Math.min(3, current + 0.2)
                                    )
                                }
                                disabled={scale >= 3}
                                aria-label="Zoom in"
                            >
                                <ZoomIn className="h-4 w-4" />
                            </Button>
                        </div>
                    </section>
                </main>
            )}
        </div>
    );
}
