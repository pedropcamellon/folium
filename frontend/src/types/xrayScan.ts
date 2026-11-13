export type XrayScanStatus = "PENDING" | "PROCESSING" | "COMPLETE" | "FAILED";

export interface XrayFinding {
    label: string;
    score: number;
}

export interface XrayScanResult {
    findings: XrayFinding[];
    modelRepository: string;
    modelRevision: string;
    reviewRequired: boolean;
    disclaimer: string;
}

export interface XrayScan {
    id: string;
    patientId: string;
    clinicalDocumentId: string;
    status: XrayScanStatus;
    result: XrayScanResult | null;
    failureMessage: string | null;
}
