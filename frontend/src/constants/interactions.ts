/**
 * Interaction constants and configuration
 */
import { InteractionType } from "@/types";

/**
 * Available interaction types with display labels
 */
export const INTERACTION_TYPES = [
    { value: InteractionType.Appointment, label: "Appointment" },
    { value: InteractionType.Consultation, label: "Consultation" },
    { value: InteractionType.Procedure, label: "Procedure" },
    { value: InteractionType.LabWork, label: "Lab Work" },
    { value: InteractionType.Imaging, label: "Imaging" },
    { value: InteractionType.Medication, label: "Medication" },
    { value: InteractionType.Vaccination, label: "Vaccination" },
    { value: InteractionType.Surgery, label: "Surgery" },
    { value: InteractionType.Emergency, label: "Emergency" },
    { value: InteractionType.Admission, label: "Admission" },
    { value: InteractionType.Discharge, label: "Discharge" },
    { value: InteractionType.VoiceNote, label: "Voice Note" },
] as const;
