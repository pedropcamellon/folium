// Shared TypeScript definitions

// ============== PORTFOLIO TYPES ==============
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  createdAt: Date;
  updatedAt: Date;
}

// ============== API TYPES ==============
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

// ============== CLINICAL TYPES ==============
export interface ClinicalSummary {
  // Define as needed
}

export interface MedicalImage {
  // Define as needed
}

export interface Patient {
  id: string;
  medicalRecordNumber: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string; // ISO string
  gender: string;
  contactInfo: string;
  medicalImages: MedicalImage[];
  clinicalSummaries: ClinicalSummary[];
}

export enum InteractionType {
  Appointment = 'Appointment',
  Vaccination = 'Vaccination',
  Medication = 'Medication',
  LabWork = 'LabWork',
  Procedure = 'Procedure',
  VoiceNote = 'VoiceNote',
  Imaging = 'Imaging',
  Surgery = 'Surgery',
  Consultation = 'Consultation',
  Emergency = 'Emergency',
  Discharge = 'Discharge',
  Admission = 'Admission'
}

export interface PatientInteraction {
  id: string;
  createdAt: string;
  createdBy: string;
  description: string;
  interactionDate: string;
  isCompliant: boolean;
  location: string;
  metadata: Record<string, any>;
  note?: string; // User-editable note field
  summary?: string;
  structuredSummary?: StructuredSummary;
  chiefComplaint?: string;
  clinicalAssessment?: string;
  treatmentPlan?: string;
  patientId: string;
  providerId: string;
  providerName: string;
  title: string;
  type: InteractionType;
  updatedAt: string;
  updatedBy: string;
}

// ============== SUMMARIZATION TYPES ==============
export interface StructuredSummary {
  chief_complaint: string;
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  clinical_tags: string[];
  icd_codes: string[];
  action_items: string[];
}

export interface SummarizationRequest {
  transcript: string;
  format?: 'soap' | 'narrative';
  interaction_type?: string;
  language?: string;
}

export interface SummarizationResponse {
  summary: string;
  structured_data: StructuredSummary;
  processing_time: number;
  model_used: string;
  provider: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export interface SummarizationHealthResponse {
  status: string;
  service_url: string;
  message?: string;
}