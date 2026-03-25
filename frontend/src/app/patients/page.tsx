"use client";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import PatientsSection from "@/components/dashboard/widgets/PatientsSection";

import { permissions } from "@/lib/permissions";

export default function PatientsPage() {
    return (
        <DashboardLayout requiredPermissions={[permissions.patientsRead]}>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
                <p className="text-gray-600 mt-1">
                    View and manage patient records
                </p>
            </div>
            <PatientsSection description="Your access in this workspace is filtered by role and permission." />
        </DashboardLayout>
    );
}
