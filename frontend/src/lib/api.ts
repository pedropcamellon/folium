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
  patients: `${FASTAPI_BASE_URL}/api/patients`,
  patient: (id: string) => `${FASTAPI_BASE_URL}/api/patients/${id}`,
  
  // Interactions
  interactions: `${FASTAPI_BASE_URL}/api/interactions`,
  interaction: (id: string) => `${FASTAPI_BASE_URL}/api/interactions/${id}`,
  interactionsByPatient: (patientId: string) => `${FASTAPI_BASE_URL}/api/interactions?patientId=${patientId}`,
  interactionNote: (id: string) => `${FASTAPI_BASE_URL}/api/interactions/${id}/note`,
  
  // Clinical Documents
  documents: `${FASTAPI_BASE_URL}/api/clinical-documents`,
  document: (id: string) => `${FASTAPI_BASE_URL}/api/clinical-documents/${id}`,
  documentsByPatient: (patientId: string, types?: string[]) => {
    const typeParam = types ? `&types=${types.join(',')}` : '';
    return `${FASTAPI_BASE_URL}/api/clinical-documents?patientId=${patientId}${typeParam}`;
  },
  documentsByInteraction: (interactionId: string) => 
    `${FASTAPI_BASE_URL}/api/clinical-documents?interactionId=${interactionId}`,
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
