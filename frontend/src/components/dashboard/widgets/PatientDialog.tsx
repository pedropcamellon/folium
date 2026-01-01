import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

import type { Patient } from "@/types";

interface PatientDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    patient: Patient | null;
    onSave: (formData: PatientFormData) => Promise<boolean>;
    submitting: boolean;
    errorMsg: string | null;
}

export interface PatientFormData {
    medicalRecordNumber: string;
    firstName: string;
    lastName: string;
    dateOfBirth: string;
    gender: string;
    contactInfo: string;
}

const emptyForm: PatientFormData = {
    medicalRecordNumber: "",
    firstName: "",
    lastName: "",
    dateOfBirth: "",
    gender: "",
    contactInfo: "",
};

export function PatientDialog({
    open,
    onOpenChange,
    patient,
    onSave,
    submitting,
    errorMsg,
}: PatientDialogProps) {
    const [form, setForm] = useState<PatientFormData>(emptyForm);

    const isEditing = patient !== null;

    // Populate form when patient changes
    useEffect(() => {
        if (patient) {
            setForm({
                medicalRecordNumber: patient.medicalRecordNumber,
                firstName: patient.firstName,
                lastName: patient.lastName,
                dateOfBirth: patient.dateOfBirth.split("T")[0],
                gender: patient.gender,
                contactInfo: patient.contactInfo,
            });
        } else {
            setForm(emptyForm);
        }
    }, [patient]);

    const handleFormChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const success = await onSave(form);
        if (success) {
            setForm(emptyForm);
            onOpenChange(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{isEditing ? "Edit Patient" : "Add New Patient"}</DialogTitle>
                </DialogHeader>
                <form className="space-y-3 mt-2" onSubmit={handleSubmit}>
                    <Input
                        name="medicalRecordNumber"
                        placeholder="MRN"
                        value={form.medicalRecordNumber}
                        onChange={handleFormChange}
                        required
                    />
                    <div className="flex gap-2">
                        <Input
                            name="firstName"
                            placeholder="First Name"
                            value={form.firstName}
                            onChange={handleFormChange}
                            required
                        />
                        <Input
                            name="lastName"
                            placeholder="Last Name"
                            value={form.lastName}
                            onChange={handleFormChange}
                            required
                        />
                    </div>
                    <Input
                        name="dateOfBirth"
                        type="date"
                        placeholder="Date of Birth"
                        value={form.dateOfBirth}
                        onChange={handleFormChange}
                        required
                    />
                    <select
                        name="gender"
                        value={form.gender}
                        onChange={handleFormChange}
                        required
                        className="w-full border rounded px-3 py-2"
                    >
                        <option value="" disabled>
                            Gender
                        </option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                    <Input
                        name="contactInfo"
                        placeholder="Contact Info"
                        value={form.contactInfo}
                        onChange={handleFormChange}
                        required
                    />
                    {errorMsg && <div className="text-red-600 text-sm">{errorMsg}</div>}
                    <div className="flex justify-end">
                        <Button type="submit" disabled={submitting}>
                            {submitting
                                ? isEditing
                                    ? "Updating..."
                                    : "Adding..."
                                : isEditing
                                    ? "Update Patient"
                                    : "Add Patient"}
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
}
