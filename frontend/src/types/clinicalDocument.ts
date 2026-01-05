export type ClinicalDocumentType =
  | 'ClinicalNote'
  | 'LabResult'
  | 'ImagingReport'
  | 'Prescription'
  | 'AdministrativeForm'
  | 'VisitSummary'
  | 'PatientUpload'
  | 'BillingCoding'
  | 'CommunicationMessage';

export interface ClinicalDocumentBase {
  id: string;
  patientId: string;
  type: ClinicalDocumentType;
  title: string;
  summary?: string;
  createdAt: string;
  updatedAt?: string;
  createdBy: string;
  updatedBy?: string;
  metadata?: Record<string, any>;
  // File attachment fields (optional - only present for uploaded documents)
  fileUrl?: string;
  fileName?: string;
  fileSize?: number;
  mimeType?: string;
}

export type ClinicalNoteFormat = 'SOAP' | 'FreeText' | 'Structured';

export interface ClinicalNoteDocument extends ClinicalDocumentBase {
  typeLabel: 'ClinicalNote';
  content: string;
  format: ClinicalNoteFormat;
}

export type LabResultStatus = 'Normal' | 'High' | 'Low' | 'Critical' | 'Pending';

export interface LabResultDocument extends ClinicalDocumentBase {
  typeLabel: 'LabResult';
  testName: string;
  resultValue: string;
  unit?: string;
  status: LabResultStatus;
}

// Add other document types as needed, all extending ClinicalDocumentBase

export type ClinicalDocument = ClinicalNoteDocument | LabResultDocument; // | ImagingReportDocument | ...
