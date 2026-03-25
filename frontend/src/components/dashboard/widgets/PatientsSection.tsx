"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import { hasPermission, permissions } from "@/lib/permissions";

import { useAuth } from "@/hooks/useAuth";
import { DataStatus, usePatients } from "@/hooks/usePatients";

import type { Patient } from "@/types";

import { PatientDialog } from "./PatientDialog";
import { PatientTable } from "./PatientTable";

interface PatientsSectionProps {
    title?: string;
    description?: string;
}

export default function PatientsSection({
    title = "Patients",
    description,
}: PatientsSectionProps) {
    const { user } = useAuth();
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
    const canCreate = hasPermission(user, permissions.patientsCreate);
    const canEdit = hasPermission(user, permissions.patientsUpdate);
    const canDelete = hasPermission(user, permissions.patientsDelete);

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
                    <h2 className="text-lg font-semibold mb-4">{title}</h2>
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
                    <div>
                        <h2 className="text-lg font-semibold">{title}</h2>
                        {description && (
                            <p className="mt-1 text-sm text-slate-500">
                                {description}
                            </p>
                        )}
                    </div>
                    {canCreate && (
                        <Button variant="primary" onClick={handleAddNew}>
                            Add Patient
                        </Button>
                    )}
                </div>
                <PatientTable
                    patients={patients}
                    status={status}
                    canEdit={canEdit}
                    canDelete={canDelete}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                />
                {(canCreate || canEdit) && (
                    <PatientDialog
                        open={dialogOpen}
                        onOpenChange={setDialogOpen}
                        patient={selectedPatient}
                        onSave={handleSave}
                        submitting={submitting}
                        errorMsg={errorMsg}
                    />
                )}
            </Card>
        </div>
    );
}
