"use client";

import { useParams } from "next/navigation";

import PatientDetail from "@/components/dashboard/PatientDetail";

export default function PatientRoute() {
    const params = useParams<{ id: string }>();

    return <PatientDetail id={params.id} />;
}
