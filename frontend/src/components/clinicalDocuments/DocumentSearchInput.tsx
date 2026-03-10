import { Search, X } from "lucide-react";

import { Input } from "@/components/ui/input";

interface DocumentSearchInputProps {
    value: string;
    onChange: (value: string) => void;
    onClear: () => void;
}

export function DocumentSearchInput({
    value,
    onChange,
    onClear,
}: DocumentSearchInputProps) {
    return (
        <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
                type="text"
                placeholder="Search documents..."
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="pl-10 pr-10 h-8"
            />
            {value && (
                <button
                    onClick={onClear}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    title="Clear search"
                >
                    <X className="w-4 h-4" />
                </button>
            )}
        </div>
    );
}
