import * as React from "react";
import { cn } from "@/lib/utils";

export function Badge({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border border-violet-200 bg-violet-50/80 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-violet-700",
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
