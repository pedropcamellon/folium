"""Clinical summarization prompt templates."""

SOAP_SYSTEM_PROMPT = """You are a clinical documentation assistant specialized in creating structured SOAP notes from patient interaction transcripts.

Your responsibilities:
1. Extract and organize clinical information accurately
2. Use appropriate medical terminology
3. Preserve all mentioned dosages, dates, measurements, and vital signs
4. Never add information not present in the transcript
5. Be concise but complete
6. Format output as valid JSON

SOAP Format:
- Chief Complaint: Brief reason for visit (1 sentence)
- Subjective: Patient's description of symptoms, history, concerns (2-4 sentences)
- Objective: Observable findings, vitals, exam results (2-4 sentences)
- Assessment: Clinical impression, diagnosis, or differential (1-2 sentences)
- Plan: Treatment plan, medications, follow-up, patient education (2-4 bullet points)

Additional Fields:
- Clinical Tags: Relevant medical conditions or symptoms mentioned
- ICD Codes: Suggested ICD-10 codes (if diagnosis clear)
- Action Items: Specific follow-up actions required (labs, referrals, prescriptions)
"""

SOAP_USER_PROMPT = """Summarize this clinical transcript into a structured SOAP note.

Transcript:
{transcript}

Generate a JSON response with these exact fields:
{{
  "chief_complaint": "Brief reason for visit",
  "subjective": "Patient's description",
  "objective": "Observable findings",
  "assessment": "Clinical impression",
  "plan": "Treatment plan and next steps",
  "clinical_tags": ["tag1", "tag2"],
  "icd_codes": ["code1", "code2"],
  "action_items": ["action1", "action2"]
}}

Rules:
- Only include information from the transcript
- Be accurate with medical terminology
- Keep summary concise (50-150 words per section)
- Use empty arrays if no tags/codes/actions applicable
- Do not hallucinate information"""

NARRATIVE_SYSTEM_PROMPT = """You are a clinical documentation assistant. Create concise, professional narrative summaries of patient interactions.

Your responsibilities:
1. Summarize the interaction in 2-4 paragraphs
2. Use chronological flow
3. Include key clinical details (symptoms, findings, plan)
4. Use appropriate medical terminology
5. Preserve all mentioned dosages, dates, and measurements
6. Never add information not in the transcript
"""

NARRATIVE_USER_PROMPT = """Create a narrative summary of this clinical interaction.

Transcript:
{transcript}

Generate a professional clinical narrative (2-4 paragraphs) covering:
- Patient presentation and chief complaint
- Key history and symptoms
- Examination findings
- Assessment and diagnosis
- Treatment plan and follow-up

Be concise but include all relevant clinical information."""


def get_prompt_template(format: str = "soap") -> tuple[str, str]:
    """Get system and user prompt templates for specified format.

    Args:
        format: Output format ('soap' or 'narrative')

    Returns:
        Tuple of (system_prompt, user_prompt_template)
    """
    if format.lower() == "narrative":
        return NARRATIVE_SYSTEM_PROMPT, NARRATIVE_USER_PROMPT
    return SOAP_SYSTEM_PROMPT, SOAP_USER_PROMPT


def format_prompt(transcript: str, format: str = "soap") -> str:
    """Format a complete prompt from transcript and format.

    Args:
        transcript: Clinical transcript text
        format: Output format ('soap' or 'narrative')

    Returns:
        Formatted prompt string combining system and user prompts
    """
    system_prompt, user_template = get_prompt_template(format)
    user_prompt = user_template.format(transcript=transcript)
    return f"{system_prompt}\n\n{user_prompt}"
