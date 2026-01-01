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
  patientId: string;
  providerId: string;
  providerName: string;
  title: string;
  type: InteractionType;
  updatedAt: string;
  updatedBy: string;
}