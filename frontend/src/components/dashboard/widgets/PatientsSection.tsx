"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import { DataStatus, usePatients } from "@/hooks/usePatients";

import type { Patient } from "@/types";

import { PatientDialog } from "./PatientDialog";
import { PatientTable } from "./PatientTable";

export default function PatientsSection() {
    const {
        patients,
        status,
        submitting,
        errorMsg,
        createPatient,
        updatePatient,
        deletePatient,
    } = usePatients();

    console.log("PatientsSection render:", {
        patients,
        status,
        hasData: !!patients,
    });

    const [dialogOpen, setDialogOpen] = useState(false);
    const [selectedPatient, setSelectedPatient] = useState<Patient | null>(
        null
    );

    const handleSave = async (formData: any) => {
        if (selectedPatient) {
            return await updatePatient(selectedPatient.id, formData);
        } else {
            return await createPatient(formData);
        }
    };

    const handleEdit = (patient: Patient) => {
        setSelectedPatient(patient);
        setDialogOpen(true);
    };

    const handleDelete = async (patient: Patient) => {
        if (
            confirm(`Delete patient ${patient.firstName} ${patient.lastName}?`)
        ) {
            await deletePatient(patient.id);
        }
    };

    const handleAddNew = () => {
        setSelectedPatient(null);
        setDialogOpen(true);
    };

    // Show error state
    if (status === DataStatus.ERROR) {
        return (
            <div className="mb-8 animate-fade-in">
                <Card className="p-6">
                    <h2 className="text-lg font-semibold mb-4">Patients</h2>
                    <div className="text-red-600 mb-2">
                        Unable to connect to backend service.
                    </div>
                    <div className="text-slate-400">
                        Patient management is temporarily unavailable.
                    </div>
                </Card>
            </div>
        );
    }

    return (
        <div className="mb-8 animate-fade-in">
            <Card className="p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold">Patients</h2>
                    <Button variant="default" onClick={handleAddNew}>
                        Add Patient
                    </Button>
                </div>
                <PatientTable
                    patients={patients}
                    status={status}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                />
                <PatientDialog
                    open={dialogOpen}
                    onOpenChange={setDialogOpen}
                    patient={selectedPatient}
                    onSave={handleSave}
                    submitting={submitting}
                    errorMsg={errorMsg}
                />
            </Card>
        </div>
    );
}
