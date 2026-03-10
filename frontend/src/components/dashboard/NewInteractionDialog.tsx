/**
 * Dialog orchestrator for creating new patient interactions
 * Combines useInteractionForm hook with InteractionForm UI in a Dialog wrapper
 */

"use client";

import { useState } from "react";

import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";

import { useInteractionForm } from "@/hooks/useInteractionForm";

import { InteractionForm } from "./InteractionForm";

interface NewInteractionDialogProps {
    patientId: string;
    patientName?: string;
}

export function NewInteractionDialog({
    patientId,
    patientName,
}: NewInteractionDialogProps) {
    const [open, setOpen] = useState(false);

    const form = useInteractionForm({
        patientId,
        onSuccess: () => {
            setOpen(false);
        },
    });

    const handleOpenChange = (isOpen: boolean) => {
        setOpen(isOpen);
        if (!isOpen) {
            form.resetForm();
        }
    };

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                <Button>
                    <Plus className="h-4 w-4" />
                    New Interaction
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Add New Interaction</DialogTitle>
                    <DialogDescription>
                        Create a new interaction record
                        {patientName ? ` for ${patientName}` : ""}.
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={form.handleSubmit}>
                    <InteractionForm
                        formData={form.formData}
                        onChange={form.updateField}
                        error={form.error}
                    />

                    <DialogFooter className="mt-6">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => setOpen(false)}
                            disabled={form.loading}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={form.loading}>
                            {form.loading
                                ? "Creating..."
                                : "Create Interaction"}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
