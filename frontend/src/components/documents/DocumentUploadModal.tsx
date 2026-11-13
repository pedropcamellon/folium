"use client";

import { useEffect, useState } from "react";

// Types
import { ClinicalDocumentCategory } from "@/types/clinicalDocument";
import type {
    XrayScan,
    XrayScanResult,
    XrayScanStatus,
} from "@/types/xrayScan";
import {
    AlertCircle,
    CheckCircle2,
    FileText,
    Image as ImageIcon,
    Upload,
    X,
} from "lucide-react";
import { useDropzone } from "react-dropzone";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

import { uploadDocument } from "@/services/clinicalDocumentService";
import { createXrayScan, getXrayScan } from "@/services/xrayScanService";

interface DocumentUploadModalProps {
    open: boolean;
    onClose: () => void;
    patientId: string;
    onUploadSuccess?: () => void;
}

const DOCUMENT_TYPES: { value: ClinicalDocumentCategory; label: string }[] = [
    { value: "clinical_note", label: "Clinical Note" },
    { value: "external_record", label: "External Record" },
    { value: "visit_summary", label: "Visit Summary" },
    { value: "patient_submission", label: "Patient Submission" },
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_EXTENSIONS = [
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".txt",
    ".docx",
    ".doc",
];

export function DocumentUploadModal({
    open,
    onClose,
    patientId,
    onUploadSuccess,
}: DocumentUploadModalProps) {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [documentType, setDocumentType] =
        useState<ClinicalDocumentCategory>("external_record");
    const [title, setTitle] = useState("");
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState<string | null>(null);
    const [uploadSuccess, setUploadSuccess] = useState(false);
    const [uploadedDocumentId, setUploadedDocumentId] = useState<string | null>(
        null
    );
    const [scanId, setScanId] = useState<string | null>(null);
    const [scanStatus, setScanStatus] = useState<XrayScanStatus | null>(null);
    const [scanResult, setScanResult] = useState<XrayScanResult | null>(null);
    const [scanError, setScanError] = useState<string | null>(null);

    useEffect(() => {
        if (
            !scanId ||
            !scanStatus ||
            scanStatus === "COMPLETE" ||
            scanStatus === "FAILED"
        ) {
            return;
        }

        let active = true;
        const poll = async () => {
            try {
                const scan: XrayScan = await getXrayScan(scanId, patientId);
                if (!active) return;
                setScanStatus(scan.status);
                setScanResult(scan.result);
                setScanError(scan.failureMessage);
            } catch (error) {
                if (active) {
                    setScanError(
                        error instanceof Error
                            ? error.message
                            : "Could not retrieve scan status"
                    );
                }
            }
        };
        const timer = window.setInterval(() => void poll(), 2000);
        void poll();

        return () => {
            active = false;
            window.clearInterval(timer);
        };
    }, [patientId, scanId, scanStatus]);

    const onDrop = (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (!file) return;

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            setUploadError(
                `File size must be less than ${MAX_FILE_SIZE / 1024 / 1024}MB`
            );
            return;
        }

        // Validate file extension
        const extension = `.${file.name.split(".").pop()?.toLowerCase()}`;
        if (!ALLOWED_EXTENSIONS.includes(extension)) {
            setUploadError(
                `File type not allowed. Allowed types: ${ALLOWED_EXTENSIONS.join(", ")}`
            );
            return;
        }

        setSelectedFile(file);
        setTitle(file.name.replace(/\.[^/.]+$/, "")); // Remove extension
        setUploadError(null);
        setUploadSuccess(false);
        setUploadedDocumentId(null);
        setScanId(null);
        setScanStatus(null);
        setScanResult(null);
        setScanError(null);
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            "application/pdf": [".pdf"],
            "image/jpeg": [".jpg", ".jpeg"],
            "image/png": [".png"],
            "text/plain": [".txt"],
            "application/msword": [".doc"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                [".docx"],
        },
        multiple: false,
        maxSize: MAX_FILE_SIZE,
    });

    const handleUpload = async () => {
        if (!selectedFile || !title) return;

        setIsUploading(true);
        setUploadError(null);
        setUploadProgress(0);

        try {
            const document = await uploadDocument({
                file: selectedFile,
                patientId,
                category: documentType,
                title,
                onProgress: setUploadProgress,
            });

            setUploadedDocumentId(document.id);
            setUploadSuccess(true);
            setUploadProgress(100);
            if (selectedFile.type.startsWith("image/")) {
                onUploadSuccess?.();
            } else {
                window.setTimeout(() => {
                    onUploadSuccess?.();
                    handleClose();
                }, 1500);
            }
        } catch (error) {
            setUploadError(
                error instanceof Error ? error.message : "Upload failed"
            );
            setUploadProgress(0);
        } finally {
            setIsUploading(false);
        }
    };

    const handleRunXrayScan = async () => {
        if (!uploadedDocumentId) return;
        setScanId(null);
        setScanError(null);
        setScanResult(null);
        setScanStatus("PENDING");
        try {
            const scan = await createXrayScan({
                patientId,
                clinicalDocumentId: uploadedDocumentId,
            });
            setScanId(scan.id);
            setScanStatus(scan.status);
            onUploadSuccess?.();
        } catch (error) {
            setScanStatus(null);
            setScanError(
                error instanceof Error
                    ? error.message
                    : "Could not start X-ray review"
            );
        }
    };

    const handleClose = () => {
        if (isUploading) return; // Prevent closing during upload
        setSelectedFile(null);
        setTitle("");
        setUploadProgress(0);
        setUploadError(null);
        setUploadSuccess(false);
        setUploadedDocumentId(null);
        setScanId(null);
        setScanStatus(null);
        setScanResult(null);
        setScanError(null);
        onClose();
    };

    const getFileIcon = () => {
        if (!selectedFile)
            return <FileText className="w-8 h-8 text-muted-foreground" />;

        const mimeType = selectedFile.type;
        if (mimeType.startsWith("image/")) {
            return <ImageIcon className="w-8 h-8 text-blue-500" />;
        }
        return <FileText className="w-8 h-8 text-red-500" />;
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent className="max-w-2xl">
                <DialogHeader>
                    <DialogTitle>Upload Clinical Document</DialogTitle>
                    <DialogDescription>
                        Upload a file and provide document details. Maximum file
                        size: 10MB
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    {/* File Dropzone */}
                    {!selectedFile && (
                        <div
                            {...getRootProps()}
                            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                                isDragActive
                                    ? "border-primary bg-primary/5"
                                    : "border-muted-foreground/25 hover:border-primary"
                            }`}
                        >
                            <input {...getInputProps()} />
                            <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                            {isDragActive ? (
                                <p className="text-sm text-muted-foreground">
                                    Drop the file here...
                                </p>
                            ) : (
                                <div>
                                    <p className="text-sm font-medium mb-1">
                                        Drag & drop a file here, or click to
                                        select
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                        PDF, JPEG, PNG, TXT, DOC, DOCX (max
                                        10MB)
                                    </p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Selected File Preview */}
                    {selectedFile && !uploadSuccess && (
                        <div className="border rounded-lg p-4 flex items-center gap-3">
                            {getFileIcon()}
                            <div className="flex-1 min-w-0">
                                <p className="font-medium truncate">
                                    {selectedFile.name}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                    {(selectedFile.size / 1024).toFixed(2)} KB
                                </p>
                            </div>
                            {!isUploading && (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        setSelectedFile(null);
                                        setTitle("");
                                    }}
                                >
                                    <X className="w-4 h-4" />
                                </Button>
                            )}
                        </div>
                    )}

                    {/* Upload Success */}
                    {uploadSuccess && (
                        <div className="border border-green-500 bg-green-50 rounded-lg p-4 flex items-center gap-3">
                            <CheckCircle2 className="w-6 h-6 text-green-600" />
                            <div>
                                <p className="font-medium text-green-900">
                                    Upload successful!
                                </p>
                                <p className="text-sm text-green-700">
                                    Document has been uploaded to patient
                                    record.
                                </p>
                            </div>
                        </div>
                    )}

                    {uploadSuccess &&
                        selectedFile?.type.startsWith("image/") && (
                            <section
                                className="space-y-3 rounded-lg border p-4"
                                aria-live="polite"
                            >
                                <p className="text-sm text-muted-foreground">
                                    Optional research-only second-look. This
                                    model does not diagnose disease or locate
                                    nodules; provider review is required.
                                </p>
                                {!scanId && (
                                    <Button onClick={handleRunXrayScan}>
                                        Run X-ray review
                                    </Button>
                                )}
                                {scanStatus && (
                                    <p className="text-sm font-medium">
                                        Review status: {scanStatus}
                                    </p>
                                )}
                                {scanStatus === "FAILED" && (
                                    <Button
                                        variant="secondary"
                                        onClick={handleRunXrayScan}
                                    >
                                        Retry review
                                    </Button>
                                )}
                                {scanError && (
                                    <p
                                        role="alert"
                                        className="text-sm text-red-700"
                                    >
                                        {scanError}
                                    </p>
                                )}
                                {scanResult && (
                                    <div className="space-y-2">
                                        <p className="font-semibold">
                                            Needs provider review
                                        </p>
                                        <p className="text-sm text-muted-foreground">
                                            Scores are not calibrated
                                            probabilities. Model:{" "}
                                            {scanResult.modelRepository} @{" "}
                                            {scanResult.modelRevision}
                                        </p>
                                        <ul className="space-y-1 text-sm">
                                            {scanResult.findings.map(
                                                (finding) => (
                                                    <li key={finding.label}>
                                                        {finding.label}: model
                                                        score{" "}
                                                        {finding.score.toFixed(
                                                            3
                                                        )}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                        <p className="text-xs text-muted-foreground">
                                            {scanResult.disclaimer}
                                        </p>
                                    </div>
                                )}
                            </section>
                        )}

                    {/* Error Message */}
                    {uploadError && (
                        <div className="border border-red-500 bg-red-50 rounded-lg p-4 flex items-center gap-3">
                            <AlertCircle className="w-6 h-6 text-red-600" />
                            <p className="text-sm text-red-900">
                                {uploadError}
                            </p>
                        </div>
                    )}

                    {/* Document Type */}
                    {selectedFile && !uploadSuccess && (
                        <>
                            <div className="space-y-2">
                                <Label htmlFor="document-type">
                                    Document Type
                                </Label>
                                <Select
                                    value={documentType}
                                    onValueChange={(value) =>
                                        setDocumentType(
                                            value as ClinicalDocumentCategory
                                        )
                                    }
                                >
                                    <SelectTrigger id="document-type">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {DOCUMENT_TYPES.map((type) => (
                                            <SelectItem
                                                key={type.value}
                                                value={type.value}
                                            >
                                                {type.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Title */}
                            <div className="space-y-2">
                                <Label htmlFor="title">Title *</Label>
                                <Input
                                    id="title"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    placeholder="Document title"
                                    disabled={isUploading}
                                />
                            </div>

                            {/* Upload Progress */}
                            {isUploading && (
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span>Uploading...</span>
                                        <span>{uploadProgress}%</span>
                                    </div>
                                    <Progress value={uploadProgress} />
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Footer Actions */}
                <div className="flex justify-end gap-2 mt-4">
                    <Button
                        variant="secondary"
                        onClick={handleClose}
                        disabled={isUploading}
                    >
                        {uploadSuccess ? "Close" : "Cancel"}
                    </Button>
                    {selectedFile && !uploadSuccess && (
                        <Button
                            onClick={handleUpload}
                            disabled={!title || isUploading}
                            isLoading={isUploading}
                            loadingText="Uploading..."
                        >
                            Upload Document
                        </Button>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
