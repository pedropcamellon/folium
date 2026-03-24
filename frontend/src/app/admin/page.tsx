"use client";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import PatientsSection from "@/components/dashboard/widgets/PatientsSection";
import { Card } from "@/components/ui/card";

import { permissions } from "@/lib/permissions";

const adminCards = [
    {
        title: "System Health",
        value: "Protected",
        description:
            "Storage tests and summarization health endpoints are restricted to admin-level permissions.",
    },
    {
        title: "User Governance",
        value: "Ready",
        description:
            "The UI now reserves an admin-specific surface for user management and audit-facing controls.",
    },
    {
        title: "Access Governance",
        value: "Role-aware",
        description:
            "Administrative tools are separated from clinical workflows and exposed only to authorized users.",
    },
];

export default function AdminPage() {
    return (
        <DashboardLayout requiredPermissions={[permissions.usersRead]}>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">
                    Admin Panel
                </h1>
                <p className="mt-1 text-gray-600">
                    Operational view for governance, access control, and
                    platform readiness.
                </p>
            </div>
            <div className="mb-8 grid gap-6 md:grid-cols-3">
                {adminCards.map((card) => (
                    <Card key={card.title} className="p-5">
                        <div className="text-sm font-medium text-slate-500">
                            {card.title}
                        </div>
                        <div className="mt-3 text-2xl font-semibold text-slate-900">
                            {card.value}
                        </div>
                        <p className="mt-2 text-sm text-slate-600">
                            {card.description}
                        </p>
                    </Card>
                ))}
            </div>
            <PatientsSection description="Admins can inspect the same operational data while retaining elevated governance permissions." />
        </DashboardLayout>
    );
}
