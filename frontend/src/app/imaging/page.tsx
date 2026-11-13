"use client";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import PatientsSection from "@/components/dashboard/widgets/PatientsSection";

import { permissions } from "@/lib/permissions";

export default function ImagingPage() {
    return (
        <DashboardLayout
            requiredPermissions={[
                permissions.documentsRead,
                permissions.patientsRead,
            ]}
        >
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Imaging AI</h1>
                <p className="mt-1 text-gray-600">
                    Select a patient with View History. In Clinical Documents,
                    upload or open an X-ray image, then choose X-ray review.
                </p>
                <p className="mt-2 text-sm text-muted-foreground">
                    Research-only second-look findings, not a diagnosis.
                    Provider review is required.
                </p>
            </div>
            <PatientsSection description="Select a patient to access their X-ray images and saved reviews." />
        </DashboardLayout>
    );
}
