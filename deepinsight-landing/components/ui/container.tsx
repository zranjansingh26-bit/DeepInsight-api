import * as React from "react";
import { cn } from "@/lib/utils";

export function Container({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("container max-w-6xl px-5 sm:px-6 lg:px-8", className)}
      {...props}
    >
      {children}
    </div>
  );
}
