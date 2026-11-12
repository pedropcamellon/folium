"use client";

import { useParams, useSearchParams } from "next/navigation";

import PatientDetail from "@/components/dashboard/PatientDetail";
import { IS_STATIC_DEMO } from "@/lib/demo-routing";

export default function PatientRoute() {
    const params = useParams<{ id: string }>();
    const searchParams = useSearchParams();
    const id = IS_STATIC_DEMO ? searchParams.get("id") ?? "" : params.id;

    return <PatientDetail id={id} />;
}
