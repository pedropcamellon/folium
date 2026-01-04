# SOAP Note Generator

Extract key information from the clinical transcript and return as JSON.

**Required JSON format:**

```json
{
  "chief_complaint": "Brief reason for visit",
  "subjective": "Patient symptoms and history", 
  "objective": "Vital signs and exam findings",
  "assessment": "Diagnosis or clinical impression",
  "plan": "Treatment and next steps",
  "clinical_tags": ["symptom1", "condition2"],
  "icd_codes": ["code1"],
  "action_items": ["action1"]
}
```

**Rules:**

- Extract only what's in the transcript
- Keep each field concise (1-3 sentences)
- Use empty arrays [] if no tags/codes/actions
- Return valid JSON only
