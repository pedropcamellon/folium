import { Suspense } from "react";

import PatientRoute from "@/components/dashboard/PatientRoute";
import { IS_STATIC_DEMO } from "@/lib/demo-routing";

export function generateStaticParams() {
    return IS_STATIC_DEMO ? [{ id: "demo" }] : [];
}

export default function PatientPage() {
    return (
        <Suspense fallback={<div className="p-6">Loading patient...</div>}>
            <PatientRoute />
        </Suspense>
    );
}
