# Voice Notes Guide

## Overview

The voice notes feature allows you to quickly record audio during patient interactions. Audio is automatically transcribed using AI, making it easy to capture clinical information hands-free.

## Recording Voice Notes

### Start Recording

1. Open a patient's record
2. Navigate to the **Interactions** tab
3. Click **New Interaction** button
4. In the interaction modal, click the **microphone icon** (🎤)
5. Grant browser permission to access your microphone (first time only)
6. Speak clearly into your microphone
7. The timer shows recording duration

### Stop Recording

1. Click the **stop icon** (⏹️) to end recording
2. Audio is automatically saved and uploaded
3. Wait for transcription to complete (typically 0.5-1 second)

### Audio Tips

**Use a quality microphone** - Built-in laptop mics work, but external mics are better  
**Minimize background noise** - Close doors, turn off fans  
**Speak clearly** - Normal conversational pace works best  
**Stay close to mic** - Within 1-2 feet for best results  
**Use short recordings** - 1-3 minutes per note recommended  

## Transcription

### Automatic Processing

- Transcription starts immediately after recording stops
- Processing time: ~0.5-0.6 seconds per voice note
- Uses Faster Whisper AI model (local, private)
- Transcripts appear in the interaction modal

### Transcription Quality

**Highly Accurate For:**
- Clear speech in quiet environments
- Medical terminology (trained on clinical vocabulary)
- Standard accents (English)

**May Struggle With:**
- Heavy accents or unclear speech
- Extreme background noise
- Multiple speakers talking over each other
- Very quiet audio

### Editing Transcripts

1. Review the generated transcript
2. Click in the transcript text area to edit
3. Correct any errors or add clarifications
4. Changes are saved automatically

## Supported Formats

- **Recording Format**: WebM (browser native)
- **Audio Quality**: 48kHz, mono
- **Max Duration**: 10 minutes per recording
- **Storage**: Secure object storage (MinIO/S3/Azure)

## Privacy & Security

- Audio files are stored securely with encryption
- Transcription is performed locally (no external APIs for voice)
- Only authorized users can access patient audio
- Audio files are linked to specific interactions

## Common Workflows

### Workflow 1: Quick Visit Note

**Scenario**: Provider wants to document a brief follow-up visit

1. Open patient record
2. Click **New Interaction**
3. Select interaction type: "Appointment"
4. Click **microphone icon**
5. Dictate: "Patient here for blood pressure follow-up. BP is 128/82, down from last visit. Continue current medications. Follow up in 3 months."
6. Click **stop**
7. Wait 1 second for transcription
8. Review transcript, make any corrections
9. Click **Generate Summary** for AI summary
10. Save interaction

**Duration**: < 2 minutes

### Workflow 2: Detailed Clinical Note

**Scenario**: Provider documenting complex patient encounter

1. Open patient record during or after visit
2. Click **New Interaction**
3. Record chief complaint segment (1-2 minutes)
4. Review transcript
5. Record history segment (1-2 minutes)
6. Review transcript
7. Record assessment and plan (1-2 minutes)
8. Review transcript
9. Generate AI summary from all transcripts
10. Save interaction

**Duration**: < 10 minutes total

### Workflow 3: Voice + Manual Entry

**Scenario**: Combining voice notes with typed information

1. Start interaction
2. Record audio for subjective/history
3. Manually enter vital signs in structured fields
4. Record audio for assessment and plan
5. Generate summary that combines all information
6. Save interaction

**Duration**: 3-5 minutes

## Troubleshooting

**Microphone not working:**
- Check browser permissions (usually shows icon in address bar)
- Ensure correct microphone selected in browser settings
- Try refreshing the page
- Check system microphone settings

**Transcription fails:**
- Verify audio was recorded (check if file uploaded)
- Try recording again with clearer audio
- Check console for error messages
- Contact administrator if issue persists

**Poor transcription quality:**
- Reduce background noise
- Speak more clearly and slowly
- Check microphone position (closer is better)
- Consider upgrading microphone hardware

**Recording stops unexpectedly:**
- Check browser connection
- Ensure sufficient storage space
- Try shorter recording segments (< 5 minutes)

---
**Last Updated**: January 5, 2026
