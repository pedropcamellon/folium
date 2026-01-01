"use client";

import { useParams } from "next/navigation";
import useSWR from "swr";

import { API_ENDPOINTS, fetcher } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { PatientClinicalDocumentsPanel } from "@/components/clinicalDocuments/PatientClinicalDocumentsPanel";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import PatientHistoryTimeline from "@/components/dashboard/PatientHistoryTimeline";

import { Patient, PatientInteraction } from "@/types";

export default function PatientPage() {
    const params = useParams();
    const id = typeof params.id === "string" ? params.id : Array.isArray(params.id) ? params.id[0] : "";

    const { data: patient, error: patientError, isLoading: patientLoading } = useSWR<Patient>(id ? API_ENDPOINTS.patient(id) : null, fetcher);
    const { data: interactions, error: interactionsError, isLoading: interactionsLoading } = useSWR<PatientInteraction[]>(id ? API_ENDPOINTS.interactionsByPatient(id) : null, fetcher);

    if (patientLoading || interactionsLoading) {
        return <DashboardLayout><div className="p-6">Loading...</div></DashboardLayout>;
    }
    if (patientError || !patient) {
        return <DashboardLayout><div className="p-6 text-red-600">Patient not found.</div></DashboardLayout>;
    }
    if (interactionsError || !interactions) {
        return <DashboardLayout><div className="p-6 text-red-600">Failed to load interactions.</div></DashboardLayout>;
    }
    const totalInteractions = Array.isArray(interactions) ? interactions.length : 0;
    const recent = Array.isArray(interactions) ? interactions.slice(0, 3) : [];

    return (
        <DashboardLayout>
            <div className="p-6">
                <Card className="p-8">
                    <h2 className="text-xl font-bold mb-2">Patient Portal</h2>
                    <div className="mb-4">
                        <div className="font-semibold">{patient.firstName} {patient.lastName}</div>
                        <div className="text-sm text-slate-500">MRN: {patient.medicalRecordNumber} | Gender: {patient.gender} | DOB: {new Date(patient.dateOfBirth).toLocaleDateString()}</div>
                        <div className="text-sm text-slate-500">Contact: {patient.contactInfo}</div>
                    </div>

                    <div>
                        <h3 className="font-semibold mb-2">Documents</h3>
                        <PatientClinicalDocumentsPanel patientId={patient.id} />
                    </div>

                    <div className="mb-4 flex gap-4">
                        <div className="bg-blue-50 rounded p-3 flex-1">
                            <div className="text-xs text-slate-500">Total Interactions</div>
                            <div className="text-2xl font-bold text-blue-700">{totalInteractions}</div>
                        </div>
                        <div className="bg-green-50 rounded p-3 flex-1">
                            <div className="text-xs text-slate-500">Recent Activity</div>
                            <ul className="text-sm mt-1">
                                {recent.map(i => <li key={i.id}>{i.title} <span className="text-xs text-slate-400">({i.type})</span></li>)}
                                {recent.length === 0 && <li className="text-slate-400">No recent activity</li>}
                            </ul>
                        </div>
                    </div>
                    <div>
                        <h3 className="font-semibold mb-2">Interaction Timeline</h3>
                        <PatientHistoryTimeline interactions={interactions} />
                    </div>
                </Card>
            </div>
        </DashboardLayout>
    );
}
