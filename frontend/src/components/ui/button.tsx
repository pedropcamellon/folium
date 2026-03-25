import * as React from "react";

import { Slot } from "@radix-ui/react-slot";
import { type VariantProps, cva } from "class-variance-authority";
import { LoaderCircle } from "lucide-react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
    "relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
    {
        variants: {
            variant: {
                primary:
                    "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
                default:
                    "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
                secondary:
                    "border border-border bg-secondary text-secondary-foreground hover:bg-secondary/80",
                tertiary:
                    "border border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground",
                outline:
                    "border border-border bg-background text-foreground hover:bg-accent hover:text-accent-foreground",
                ghost: "text-foreground hover:bg-accent hover:text-accent-foreground",
                link: "text-primary underline-offset-4 hover:underline",
                "danger-primary":
                    "bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
                destructive:
                    "bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
                "danger-tertiary":
                    "border border-destructive bg-background text-destructive hover:bg-destructive hover:text-white focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
                "danger-ghost":
                    "text-destructive hover:bg-destructive hover:text-white focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
            },
            size: {
                default: "h-10 px-4 py-2 has-[>svg]:px-3",
                sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
                md: "h-10 px-4 py-2 has-[>svg]:px-3",
                lg: "h-12 rounded-md px-6 has-[>svg]:px-4",
                icon: "size-10",
                "icon-sm": "size-8",
                "icon-md": "size-10",
            },
            fullWidth: {
                true: "w-full",
            },
        },
        defaultVariants: {
            variant: "primary",
            size: "default",
            fullWidth: false,
        },
    }
);

function Button({
    className,
    variant,
    size,
    fullWidth,
    asChild = false,
    isLoading = false,
    loadingText,
    disabled,
    children,
    ...props
}: React.ComponentProps<"button"> &
    VariantProps<typeof buttonVariants> & {
        asChild?: boolean;
        fullWidth?: boolean;
        isLoading?: boolean;
        loadingText?: string;
    }) {
    const Comp = asChild ? Slot : "button";

    return (
        <Comp
            data-slot="button"
            aria-busy={isLoading || undefined}
            className={cn(
                buttonVariants({ variant, size, fullWidth, className })
            )}
            disabled={Comp === "button" ? disabled || isLoading : undefined}
            {...props}
        >
            <span
                className={cn(
                    "inline-flex items-center gap-2",
                    isLoading && "opacity-0"
                )}
            >
                {children}
            </span>
            {isLoading && (
                <span className="absolute inset-0 flex items-center justify-center gap-2">
                    <LoaderCircle
                        className="size-4 animate-spin"
                        aria-hidden="true"
                    />
                    {loadingText ? <span>{loadingText}</span> : null}
                </span>
            )}
        </Comp>
    );
}

export { Button, buttonVariants };
