import { Suspense } from "react";

import PatientRoute from "@/components/dashboard/PatientRoute";

export default function PatientPage() {
    return (
        <Suspense fallback={<div className="p-6">Loading patient...</div>}>
            <PatientRoute />
        </Suspense>
    );
}
