import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import { DataStatus } from "@/hooks/usePatients";

import type { Patient } from "@/types";

interface PatientTableProps {
    patients: Patient[] | undefined;
    status: DataStatus;
    onEdit: (patient: Patient) => void;
    onDelete: (patient: Patient) => void;
}

export function PatientTable({
    patients,
    status,
    onEdit,
    onDelete,
}: PatientTableProps) {
    const isLoading =
        status === DataStatus.LOADING || status === DataStatus.IDLE;
    return (
        <div className="rounded-lg border overflow-x-auto bg-white">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>MRN</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Date of Birth</TableHead>
                        <TableHead>Gender</TableHead>
                        <TableHead>Contact</TableHead>
                        <TableHead>Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {isLoading &&
                        Array.from({ length: 5 }).map((_, i) => (
                            <TableRow key={i}>
                                <TableCell colSpan={6}>
                                    <Skeleton className="h-6 w-full" />
                                </TableCell>
                            </TableRow>
                        ))}
                    {patients && patients.length === 0 && (
                        <TableRow>
                            <TableCell colSpan={6} className="text-slate-400">
                                No patients found.
                            </TableCell>
                        </TableRow>
                    )}
                    {patients &&
                        patients.map((patient) => (
                            <TableRow
                                key={patient.id}
                                className="transition-all duration-200 hover:bg-slate-50"
                            >
                                <TableCell>
                                    {patient.medicalRecordNumber}
                                </TableCell>
                                <TableCell>
                                    {patient.firstName} {patient.lastName}
                                </TableCell>
                                <TableCell>
                                    {new Date(
                                        patient.dateOfBirth
                                    ).toLocaleDateString()}
                                </TableCell>
                                <TableCell>{patient.gender}</TableCell>
                                <TableCell>{patient.contactInfo}</TableCell>
                                <TableCell>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => onEdit(patient)}
                                    >
                                        Edit
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="destructive"
                                        className="ml-2"
                                        onClick={() => onDelete(patient)}
                                    >
                                        Delete
                                    </Button>
                                    <a href={`/patients/${patient.id}`}>
                                        <Button
                                            size="sm"
                                            variant="secondary"
                                            className="ml-2"
                                        >
                                            View History
                                        </Button>
                                    </a>
                                </TableCell>
                            </TableRow>
                        ))}
                </TableBody>
            </Table>
        </div>
    );
}
