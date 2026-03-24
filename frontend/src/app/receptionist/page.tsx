"use client";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import PatientsSection from "@/components/dashboard/widgets/PatientsSection";
import { Card } from "@/components/ui/card";

import { permissions } from "@/lib/permissions";

export default function ReceptionistPage() {
    return (
        <DashboardLayout requiredPermissions={[permissions.voiceRecord]}>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">
                    Receptionist Workspace
                </h1>
                <p className="mt-1 text-gray-600">
                    Intake-first view for patient coordination, front-desk
                    context, and voice capture.
                </p>
            </div>
            <div className="mb-8 grid gap-6 md:grid-cols-3">
                <Card className="p-5">
                    <div className="text-sm font-medium text-slate-500">
                        Patient Intake
                    </div>
                    <div className="mt-3 text-2xl font-semibold text-slate-900">
                        Enabled
                    </div>
                    <p className="mt-2 text-sm text-slate-600">
                        Review and maintain front-desk patient context without
                        exposing admin-only tools.
                    </p>
                </Card>
                <Card className="p-5">
                    <div className="text-sm font-medium text-slate-500">
                        Voice Notes
                    </div>
                    <div className="mt-3 text-2xl font-semibold text-slate-900">
                        Available
                    </div>
                    <p className="mt-2 text-sm text-slate-600">
                        Reception staff can participate in the capture workflow
                        without clinical summary access.
                    </p>
                </Card>
                <Card className="p-5">
                    <div className="text-sm font-medium text-slate-500">
                        Clinical Summaries
                    </div>
                    <div className="mt-3 text-2xl font-semibold text-slate-900">
                        Restricted
                    </div>
                    <p className="mt-2 text-sm text-slate-600">
                        Summarization and higher-risk clinical actions remain
                        hidden and blocked at the API layer.
                    </p>
                </Card>
            </div>
            <PatientsSection description="Reception access is limited to intake-oriented patient workflows." />
        </DashboardLayout>
    );
}
