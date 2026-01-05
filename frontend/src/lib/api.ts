/**
 * Central API configuration for FastAPI backend
 * Direct calls to FastAPI (no BFF middleware)
 */

export const FASTAPI_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

/**
 * API endpoints configuration
 */
export const API_ENDPOINTS = {
  // Health
  health: `${FASTAPI_BASE_URL}/health`,

  // Patients
  patients: `${FASTAPI_BASE_URL}/api/v1/patients`,
  patient: (id: string) => `${FASTAPI_BASE_URL}/api/v1/patients/${id}`,

  // Interactions
  interactions: `${FASTAPI_BASE_URL}/api/v1/interactions`,
  interaction: (id: string) => `${FASTAPI_BASE_URL}/api/v1/interactions/${id}`,
  interactionsByPatient: (patientId: string) => `${FASTAPI_BASE_URL}/api/v1/interactions?patientId=${patientId}`,
  interactionNote: (id: string) => `${FASTAPI_BASE_URL}/api/v1/interactions/${id}/note`,
  interactionSummary: (id: string) => `${FASTAPI_BASE_URL}/api/v1/interactions/${id}/summary`,

  // Clinical Documents
  documents: `${FASTAPI_BASE_URL}/api/v1/clinical-documents`,
  document: (id: string) => `${FASTAPI_BASE_URL}/api/v1/clinical-documents/${id}`,
  documentsByPatient: (patientId: string, types?: string[]) => {
    const typeParam = types ? `&types=${types.join(',')}` : '';
    return `${FASTAPI_BASE_URL}/api/v1/clinical-documents?patientId=${patientId}${typeParam}`;
  },
  documentsByInteraction: (interactionId: string) =>
    `${FASTAPI_BASE_URL}/api/v1/clinical-documents?interactionId=${interactionId}`,
  documentUpload: `${FASTAPI_BASE_URL}/api/v1/clinical-documents/upload`,
  documentDownload: (id: string) => `${FASTAPI_BASE_URL}/api/v1/clinical-documents/${id}/download`,
  documentView: (id: string) => `${FASTAPI_BASE_URL}/api/v1/clinical-documents/${id}/view`,

  // Summarization
  summarize: `${FASTAPI_BASE_URL}/api/v1/summarization/test`,
  summarizationHealth: `${FASTAPI_BASE_URL}/api/v1/summarization/health`,
} as const;

/**
 * Generic fetcher for SWR
 */
export const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    const error = new Error('API request failed');
    throw error;
  }
  return res.json();
};
