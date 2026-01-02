/**
 * Summarization service for generating clinical summaries from transcripts
 */

import { API_ENDPOINTS } from "@/lib/api";
import { 
  SummarizationRequest, 
  SummarizationResponse, 
  SummarizationHealthResponse 
} from "@/types";

/**
 * Generate clinical summary from transcript
 */
export async function generateSummary(
  request: SummarizationRequest
): Promise<SummarizationResponse> {
  const res = await fetch(API_ENDPOINTS.summarize, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    let errorMsg = "Failed to generate summary";
    try {
      const err = await res.json();
      errorMsg = err?.detail || err?.message || errorMsg;
    } catch { }
    throw new Error(errorMsg);
  }

  return res.json();
}

/**
 * Check summarization service health
 */
export async function checkSummarizationHealth(): Promise<SummarizationHealthResponse> {
  const res = await fetch(API_ENDPOINTS.summarizationHealth);
  
  if (!res.ok) {
    throw new Error("Summarization service unavailable");
  }

  return res.json();
}

/**
 * Format SOAP summary for display
 */
export function formatSoapSummary(structured: SummarizationResponse['structured_data']): string {
  const parts: string[] = [];

  if (structured.chief_complaint) {
    parts.push(`Chief Complaint: ${structured.chief_complaint}`);
  }

  if (structured.subjective) {
    parts.push(`\nSubjective:\n${structured.subjective}`);
  }

  if (structured.objective) {
    parts.push(`\nObjective:\n${structured.objective}`);
  }

  if (structured.assessment) {
    parts.push(`\nAssessment:\n${structured.assessment}`);
  }

  if (structured.plan) {
    parts.push(`\nPlan:\n${structured.plan}`);
  }

  if (structured.icd_codes && structured.icd_codes.length > 0) {
    parts.push(`\nICD-10 Codes:\n${structured.icd_codes.join('\n')}`);
  }

  if (structured.action_items && structured.action_items.length > 0) {
    parts.push(`\nAction Items:\n${structured.action_items.map(item => `- ${item}`).join('\n')}`);
  }

  return parts.join('\n');
}
