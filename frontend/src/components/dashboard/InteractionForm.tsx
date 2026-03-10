/**
 * Presentational form component for creating/editing interactions
 * Pure UI component - receives data and callbacks from parent
 */
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

import { InteractionFormData } from "@/hooks/useInteractionForm";

import { INTERACTION_TYPES } from "@/constants/interactions";

interface InteractionFormProps {
    formData: InteractionFormData;
    onChange: (field: keyof InteractionFormData, value: string) => void;
    error?: string | null;
}

export function InteractionForm({
    formData,
    onChange,
    error,
}: InteractionFormProps) {
    return (
        <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Interaction Type */}
                <div className="space-y-2">
                    <Label htmlFor="type">
                        Type <span className="text-red-500">*</span>
                    </Label>
                    <Select
                        value={formData.type}
                        onValueChange={(value) => onChange("type", value)}
                    >
                        <SelectTrigger id="type">
                            <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                            {INTERACTION_TYPES.map((t) => (
                                <SelectItem key={t.value} value={t.value}>
                                    {t.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* Interaction Date */}
                <div className="space-y-2">
                    <Label htmlFor="interactionDate">
                        Date & Time <span className="text-red-500">*</span>
                    </Label>
                    <Input
                        id="interactionDate"
                        type="datetime-local"
                        value={formData.interactionDate}
                        onChange={(e) =>
                            onChange("interactionDate", e.target.value)
                        }
                        required
                    />
                </div>
            </div>

            {/* Title */}
            <div className="space-y-2">
                <Label htmlFor="title">
                    Title <span className="text-red-500">*</span>
                </Label>
                <Input
                    id="title"
                    placeholder="e.g., Annual Physical Exam"
                    value={formData.title}
                    onChange={(e) => onChange("title", e.target.value)}
                    required
                />
            </div>

            {/* Description */}
            <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                    id="description"
                    placeholder="Add details about this interaction..."
                    value={formData.description}
                    onChange={(e) => onChange("description", e.target.value)}
                    rows={3}
                />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Location */}
                <div className="space-y-2">
                    <Label htmlFor="location">Location</Label>
                    <Input
                        id="location"
                        placeholder="e.g., Room 301, Main Building"
                        value={formData.location}
                        onChange={(e) => onChange("location", e.target.value)}
                    />
                </div>

                {/* Provider Name */}
                <div className="space-y-2">
                    <Label htmlFor="providerName">Provider Name</Label>
                    <Input
                        id="providerName"
                        placeholder="e.g., Dr. Smith"
                        value={formData.providerName}
                        onChange={(e) =>
                            onChange("providerName", e.target.value)
                        }
                    />
                </div>
            </div>

            {/* Provider ID (optional, for advanced users) */}
            <div className="space-y-2">
                <Label htmlFor="providerId">Provider ID (Optional)</Label>
                <Input
                    id="providerId"
                    placeholder="Provider identifier"
                    value={formData.providerId}
                    onChange={(e) => onChange("providerId", e.target.value)}
                />
            </div>

            {/* Error Display */}
            {error && (
                <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md border border-red-200">
                    {error}
                </div>
            )}
        </div>
    );
}
