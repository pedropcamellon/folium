"use client";

import { useEffect, useState } from "react";

import { type XrayScan, XrayScanStatus } from "@/types/xrayScan";

import { Button } from "@/components/ui/button";

import {
    createXrayScan,
    getXrayScan,
    listXrayScans,
} from "@/services/xrayScanService";

import { XrayScanFindingsTable } from "./XrayScanFindingsTable";

interface XrayReviewInsightsProps {
    patientId: string;
    clinicalDocumentId: string;
}

export function XrayReviewInsights({
    patientId,
    clinicalDocumentId,
}: XrayReviewInsightsProps) {
    const [scan, setScan] = useState<XrayScan | null>(null);
    const [loadingScan, setLoadingScan] = useState(true);
    const [startingScan, setStartingScan] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const scanId = scan?.id;
    const scanStatus = scan?.status;

    useEffect(() => {
        let active = true;
        setScan(null);
        setLoadingScan(true);
        setError(null);

        void listXrayScans(patientId)
            .then((scans) => {
                if (!active) return;
                const latestScan = scans
                    .filter(
                        (candidate) =>
                            candidate.clinicalDocumentId === clinicalDocumentId
                    )
                    .sort(
                        (left, right) =>
                            Date.parse(right.createdAt) -
                            Date.parse(left.createdAt)
                    )[0];
                setScan(latestScan ?? null);
            })
            .catch((loadError) => {
                if (active) {
                    setError(
                        loadError instanceof Error
                            ? loadError.message
                            : "Could not load X-ray review"
                    );
                }
            })
            .finally(() => {
                if (active) setLoadingScan(false);
            });

        return () => {
            active = false;
        };
    }, [clinicalDocumentId, patientId]);

    useEffect(() => {
        if (
            !scanId ||
            scanStatus === XrayScanStatus.COMPLETE ||
            scanStatus === XrayScanStatus.FAILED
        ) {
            return;
        }

        let active = true;
        const poll = async () => {
            try {
                const updatedScan = await getXrayScan(scanId, patientId);
                if (active) {
                    setScan(updatedScan);
                    setError(null);
                }
            } catch (pollError) {
                if (active) {
                    setError(
                        pollError instanceof Error
                            ? pollError.message
                            : "Could not retrieve X-ray review status"
                    );
                }
            }
        };
        const timer = window.setInterval(() => void poll(), 2000);
        void poll();

        return () => {
            active = false;
            window.clearInterval(timer);
        };
    }, [patientId, scanId, scanStatus]);

    const handleRunScan = async () => {
        setStartingScan(true);
        setError(null);
        try {
            const newScan = await createXrayScan({
                patientId,
                clinicalDocumentId,
            });
            setScan(newScan);
        } catch (scanError) {
            setError(
                scanError instanceof Error
                    ? scanError.message
                    : "Could not start X-ray review"
            );
        } finally {
            setStartingScan(false);
        }
    };

    return (
        <aside className="flex h-full min-h-0 flex-col gap-4 overflow-y-auto p-5">
            <div>
                <h3 className="text-lg font-semibold">Insights</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                    This model does not diagnose disease or locate nodules;
                    provider review is required.
                </p>
                <p className="text-xs text-muted-foreground">
                    Model scores are shown as percentages for readability. They
                    are not calibrated probabilities or disease likelihoods.
                </p>
            </div>

            {error && (
                <p role="alert" className="text-sm text-red-700">
                    {error}
                </p>
            )}

            {loadingScan && (
                <p className="text-sm text-muted-foreground">
                    Loading saved review...
                </p>
            )}

            {!loadingScan &&
                (!scan ||
                    scan.status === XrayScanStatus.FAILED ||
                    scan.status === XrayScanStatus.COMPLETE) && (
                    <Button
                        size="sm"
                        className="self-start"
                        onClick={handleRunScan}
                        disabled={startingScan}
                    >
                        {startingScan
                            ? "Starting scan..."
                            : scan?.status === XrayScanStatus.FAILED
                              ? "Retry scan"
                              : scan?.status === XrayScanStatus.COMPLETE
                                ? "Run again"
                                : "Run scan"}
                    </Button>
                )}

            {scan && (
                <p className="text-sm font-medium">
                    Scan status: {scan.status}
                </p>
            )}

            {scan?.status === XrayScanStatus.COMPLETE && scan.result && (
                <div className="space-y-3">
                    <p className="font-semibold">Needs provider review</p>
                    <XrayScanFindingsTable result={scan.result} />
                </div>
            )}

            {scan?.status === XrayScanStatus.FAILED && scan.failureMessage && (
                <p role="alert" className="text-sm text-red-700">
                    {scan.failureMessage}
                </p>
            )}
        </aside>
    );
}
