"use client";

import { useEffect, useRef, useState } from "react";
import type { PointerEvent } from "react";

import type { ClinicalDocumentAttachmentView } from "@/types/clinicalDocument";

interface XrayReviewImageProps {
    document: ClinicalDocumentAttachmentView;
    scale: number;
    onLoadError?: (error: Error) => void;
}

export function XrayReviewImage({
    document,
    scale,
    onLoadError,
}: XrayReviewImageProps) {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [dragging, setDragging] = useState(false);
    const dragStart = useRef<{
        pointerId: number;
        clientX: number;
        clientY: number;
        x: number;
        y: number;
    } | null>(null);

    useEffect(() => {
        setPosition({ x: 0, y: 0 });
    }, [document.fileUrl]);

    useEffect(() => {
        if (scale <= 1) setPosition({ x: 0, y: 0 });
    }, [scale]);

    const handlePointerDown = (event: PointerEvent<HTMLImageElement>) => {
        if (scale <= 1 || event.button !== 0) return;

        event.preventDefault();
        event.currentTarget.setPointerCapture(event.pointerId);
        dragStart.current = {
            pointerId: event.pointerId,
            clientX: event.clientX,
            clientY: event.clientY,
            ...position,
        };
        setDragging(true);
    };

    const handlePointerMove = (event: PointerEvent<HTMLImageElement>) => {
        const start = dragStart.current;
        if (!start || start.pointerId !== event.pointerId) return;

        setPosition({
            x: start.x + event.clientX - start.clientX,
            y: start.y + event.clientY - start.clientY,
        });
    };

    const handlePointerEnd = (event: PointerEvent<HTMLImageElement>) => {
        if (dragStart.current?.pointerId !== event.pointerId) return;
        dragStart.current = null;
        setDragging(false);
    };

    return (
        <div className="flex h-full w-full items-center justify-center">
            <img
                src={document.fileUrl}
                alt={document.title}
                draggable={false}
                onPointerDown={handlePointerDown}
                onPointerMove={handlePointerMove}
                onPointerUp={handlePointerEnd}
                onPointerCancel={handlePointerEnd}
                onError={() =>
                    onLoadError?.(new Error("Failed to load image"))
                }
                style={{
                    transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
                    maxWidth: "100%",
                    maxHeight: "80vh",
                    width: "auto",
                    height: "auto",
                    transformOrigin: "center",
                    touchAction: scale > 1 ? "none" : "auto",
                }}
                className={`object-contain ${
                    scale > 1
                        ? dragging
                            ? "cursor-grabbing"
                            : "cursor-grab"
                        : ""
                }`}
            />
        </div>
    );
}
