# Clinical Summaries Guide

## Overview

The AI-powered summarization feature transforms clinical transcripts and notes into structured, professional summaries. Summaries can be generated instantly and edited as needed.

## Generating Summaries

### From Voice Transcripts

1. Record a voice note (see [Voice Notes Guide](voice-notes.md))
2. Wait for transcription to complete
3. Click the **Generate Summary** button
4. AI processes transcript (typically 2-3 seconds)
5. Structured summary appears in the summary section

### From Manual Notes

1. Create or open an interaction
2. Type notes in the interaction fields
3. Click **Generate Summary**
4. AI creates summary from your text
5. Review and edit as needed

### AI Processing

- **Processing Time**: 2-3 seconds per summary
- **Model**: Azure OpenAI GPT-4.1-nano (or Claude 3 Haiku)
- **Cost**: ~$0.18 per 1 million tokens (very economical)
- **Format**: SOAP note or narrative clinical note

## Summary Structure

### SOAP Format

**S - Subjective**: Patient's chief complaint, history of present illness, symptoms

**O - Objective**: Vital signs, physical exam findings, test results

**A - Assessment**: Diagnosis, clinical impression, differential diagnosis

**P - Plan**: Treatment plan, medications, follow-up instructions

### Additional Fields

- **Clinical Tags**: Key medical concepts extracted
- **ICD Codes**: Suggested diagnosis codes (if applicable)
- **Action Items**: Follow-up tasks, labs to order, referrals

## Editing Summaries

### Manual Editing

1. Locate the summary section in the interaction modal
2. Click the **Edit** button (pencil icon)
3. Modify any text in the summary field
4. Click **Save** to persist changes
5. Click **Cancel** to discard edits

### Tips for Editing

Add patient-specific details AI might miss  
Correct any medication names or dosages  
Refine diagnosis codes for billing accuracy  
Add follow-up instructions specific to patient  
Remove any hallucinated or incorrect information  

## Summary Quality

### AI Strengths

- Extracting key clinical information from transcripts
- Organizing information into SOAP format
- Identifying medical terminology and concepts
- Generating professional, concise language

### AI Limitations

- May miss nuanced clinical details
- Cannot verify factual accuracy (always review!)
- May hallucinate information not in transcript
- Cannot replace clinical judgment

**Always review and edit AI-generated summaries before finalizing!**

## Regenerating Summaries

1. Edit the original transcript or notes
2. Click **Generate Summary** again
3. New summary replaces the previous one
4. Previous summary is not saved (edit instead of regenerating)

## Providers & Configuration

### Available AI Providers

**Azure OpenAI** (Default):

- Model: GPT-4.1-nano
- Speed: ~2.7 seconds
- Cost: $0.18/1M tokens
- Quality: Excellent

**AWS Bedrock**:

- Model: Claude 3 Haiku
- Speed: ~3 seconds
- Cost: Similar
- Quality: Excellent

**Local LLM**:

- Model: MediPhi-Clinical (GGUF)
- Speed: Varies by hardware
- Cost: Free (self-hosted)
- Quality: Good for basic summaries

*Contact your administrator to change AI providers*

## Common Workflows

### Workflow 1: Quick Visit Summary

**Scenario**: Provider needs immediate summary after appointment

1. Complete patient visit
2. Record voice note with key details (1-2 minutes)
3. Wait for transcription (1 second)
4. Click **Generate Summary**
5. Wait for summary (2-3 seconds)
6. Quick review and minor edits if needed
7. Save interaction

**Duration**: < 3 minutes total

### Workflow 2: End-of-Day Batch Summaries

**Scenario**: Provider recorded voice notes throughout day, now generating summaries

1. Open first patient interaction with transcript
2. Generate summary
3. Review and edit while waiting
4. Save and move to next patient
5. Repeat for all patients seen that day

**Duration**: 2-3 minutes per patient

### Workflow 3: Complex Case Documentation

**Scenario**: Lengthy patient encounter with multiple issues

1. Record detailed voice notes (5-10 minutes total)
2. Review and edit transcript for accuracy
3. Add any additional manual notes (vitals, measurements)
4. Generate AI summary
5. Carefully review summary section by section
6. Edit assessment and plan to add clinical reasoning
7. Add ICD codes and action items
8. Save interaction

**Duration**: 10-15 minutes

## Summary Privacy & Compliance

- Summaries are stored securely with patient records
- AI processing uses HIPAA-compliant providers
- No patient data is shared with external services (when using local LLM)
- Audit logs track all summary generation and edits

## Best Practices

**Generate summaries promptly** - Right after visit while details are fresh  
**Always review before finalizing** - AI is a tool, not a replacement for clinical judgment  
**Edit for specificity** - Add patient-specific context AI might miss  
**Use consistent formatting** - Helps with billing and record keeping  
**Include action items** - Labs to order, follow-ups, referrals  
**Check medication accuracy** - Verify drug names, dosages, frequencies  

## Troubleshooting

**Summary generation fails:**

- Check that transcript or notes exist
- Verify AI service is configured (contact admin)
- Try again (may be temporary service issue)
- Check for error messages in console

**Summary is incomplete or inaccurate:**

- Review source transcript for clarity
- Edit transcript before regenerating
- Manually edit summary to add missing details
- Consider dictating more structured notes

**Summary is too long or verbose:**

- Manually edit to condense
- Provide more concise voice notes
- Contact admin about prompt tuning

**Summary doesn't match transcript:**

- Verify correct transcript was used
- Check for AI hallucinations (compare closely)
- Report systematic issues to administrator
- Manually edit to correct

---
**Last Updated**: January 5, 2026
