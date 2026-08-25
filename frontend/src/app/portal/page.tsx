"use client";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

import { permissions } from "@/lib/permissions";

import { useAuth } from "@/hooks/useAuth";

const portalCards = [
    {
        title: "Last Visit",
        value: "Mar 18, 2026",
        description:
            "Annual wellness follow-up with updated medication review and care plan.",
    },
    {
        title: "Lab Results",
        value: "2 new",
        description:
            "Your latest bloodwork and metabolic panel are ready to review.",
    },
    {
        title: "Check-In",
        value: "Ready",
        description:
            "Complete intake questions before your next appointment to save time at arrival.",
    },
];

export default function PortalPage() {
    const { user } = useAuth();

    return (
        <DashboardLayout requiredPermissions={[permissions.portalRead]}>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">
                    Patient Portal
                </h1>
                <p className="mt-1 text-gray-600">
                    Review recent care activity, stay on top of results, and
                    prepare for upcoming visits.
                </p>
            </div>
            <div className="mb-8 grid gap-6 md:grid-cols-3">
                {portalCards.map((card) => (
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
            <Card className="p-6">
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div>
                        <div className="text-sm font-medium text-slate-500">
                            Next Appointment
                        </div>
                        <div className="mt-2 text-xl font-semibold text-slate-900">
                            Apr 02, 2026 at 9:30 AM
                        </div>
                        <p className="mt-2 text-sm text-slate-600">
                            Family medicine follow-up with Dr. Rivera at
                            Folium Clinic.
                        </p>
                    </div>
                    <div className="flex flex-col gap-3 sm:flex-row">
                        <Button size="lg" variant="primary">
                            Start Check-In
                        </Button>
                        <Button size="lg" variant="tertiary">
                            View Visit Details
                        </Button>
                    </div>
                </div>
            </Card>
        </DashboardLayout>
    );
}
