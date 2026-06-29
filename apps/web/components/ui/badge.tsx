import * as React from "react";

import { cn } from "@/lib/utils";

export function Badge({ className, tone = "neutral", ...props }: React.HTMLAttributes<HTMLSpanElement> & { tone?: "neutral" | "good" | "warn" | "danger" }) {
  const toneClass = {
    neutral: "bg-muted text-muted-foreground",
    good: "bg-positive/15 text-positive",
    warn: "bg-warning/15 text-warning",
    danger: "bg-danger/15 text-danger"
  }[tone];
  return <span className={cn("inline-flex items-center rounded-md px-2 py-1 text-xs font-medium", toneClass, className)} {...props} />;
}
