"use client";

import DashboardLayout from "./DashboardLayout";
import MetricsCards from "./widgets/MetricsCards";
import PatientsSection from "./widgets/PatientsSection";

export default function Dashboard() {
    return (
        <DashboardLayout>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600 mt-1">
                    Welcome back! Here's an overview of your practice.
                </p>
            </div>
            <MetricsCards />
            <PatientsSection />
        </DashboardLayout>
    );
}
