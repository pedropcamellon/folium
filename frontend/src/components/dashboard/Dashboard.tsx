"use client";

import DashboardLayout from "./DashboardLayout";
import MetricsCards from "./widgets/MetricsCards";
import PatientsSection from "./widgets/PatientsSection";

export default function Dashboard() {
    return (
        <DashboardLayout>
            <MetricsCards />
            <PatientsSection />
        </DashboardLayout>
    );
}
