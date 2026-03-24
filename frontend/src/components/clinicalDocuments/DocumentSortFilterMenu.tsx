import { ClinicalDocumentType } from "@/types/clinicalDocument";
import { CommonListSortOption } from "@/types/sort";
import { ArrowUpDown, ChevronDown } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuRadioGroup,
    DropdownMenuRadioItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const DOCUMENT_TYPES: ClinicalDocumentType[] = [
    "ClinicalNote",
    "LabResult",
    "ImagingReport",
    "Prescription",
    "AdministrativeForm",
    "VisitSummary",
    "PatientUpload",
    "BillingCoding",
    "CommunicationMessage",
];

const TYPE_LABELS: Record<ClinicalDocumentType, string> = {
    ClinicalNote: "Clinical Note",
    LabResult: "Lab Result",
    ImagingReport: "Imaging Report",
    Prescription: "Prescription",
    AdministrativeForm: "Admin Form",
    VisitSummary: "Visit Summary",
    PatientUpload: "Patient Upload",
    BillingCoding: "Billing/Coding",
    CommunicationMessage: "Communication",
};

interface DocumentSortFilterMenuProps {
    sortBy: CommonListSortOption;
    selectedTypes: ClinicalDocumentType[];
    onSortChange: (sort: CommonListSortOption) => void;
    onTypeToggle: (type: ClinicalDocumentType) => void;
    onClearFilters: () => void;
}

export function DocumentSortFilterMenu({
    sortBy,
    selectedTypes,
    onSortChange,
    onTypeToggle,
    onClearFilters,
}: DocumentSortFilterMenuProps) {
    const hasActiveFilters =
        selectedTypes.length > 0 || sortBy !== "createdAt-desc";

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                    <ArrowUpDown className="w-4 h-4 mr-2" />
                    Sort & Filter
                    {hasActiveFilters && (
                        <span className="ml-1 bg-primary text-primary-foreground rounded-full w-5 h-5 text-xs flex items-center justify-center">
                            {selectedTypes.length || "•"}
                        </span>
                    )}
                    <ChevronDown className="w-4 h-4 ml-1" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Sort By</DropdownMenuLabel>
                <DropdownMenuRadioGroup
                    value={sortBy}
                    onValueChange={(value) =>
                        onSortChange(value as CommonListSortOption)
                    }
                >
                    <DropdownMenuRadioItem value="createdAt-desc">
                        Date Created (Newest)
                    </DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="createdAt-asc">
                        Date Created (Oldest)
                    </DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="updatedAt-desc">
                        Last Modified
                    </DropdownMenuRadioItem>
                    <DropdownMenuRadioItem value="title-asc">
                        Title (A-Z)
                    </DropdownMenuRadioItem>
                </DropdownMenuRadioGroup>

                <DropdownMenuSeparator />

                <DropdownMenuLabel className="flex items-center justify-between">
                    Filter by Type
                    {selectedTypes.length > 0 && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                                e.stopPropagation();
                                onClearFilters();
                            }}
                            className="h-6 text-xs px-2"
                        >
                            Clear
                        </Button>
                    )}
                </DropdownMenuLabel>
                {DOCUMENT_TYPES.map((type) => (
                    <DropdownMenuCheckboxItem
                        key={type}
                        checked={selectedTypes.includes(type)}
                        onCheckedChange={() => onTypeToggle(type)}
                    >
                        {TYPE_LABELS[type]}
                    </DropdownMenuCheckboxItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
