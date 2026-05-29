import { Sparkles } from "lucide-react";
import { Container } from "@/components/ui/container";
import { footerColumns, site } from "@/lib/site";

export function Footer() {
  return (
    <footer className="bg-white pb-12">
      <Container className="max-w-5xl mx-auto">
        <div className="grid gap-12 lg:grid-cols-[1fr_2fr]">
          <div className="max-w-xs">
            <a href="#" className="inline-flex items-center gap-2">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-navy-950">
                <Sparkles className="h-4 w-4 text-white" strokeWidth={2} />
              </span>
              <span className="font-display text-xl font-medium tracking-tight text-ink">
                {site.name}
              </span>
            </a>
            <p className="mt-4 text-xs font-medium text-slate-400 max-w-[150px]">
              Hassle-free AI technology.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-8">
            {footerColumns.map((col) => (
              <div key={col.title}>
                <h3 className="font-display text-sm font-semibold text-ink">
                  {col.title}
                </h3>
                <ul className="mt-4 space-y-3 text-xs font-medium">
                  {col.links.map((l) => (
                    <li key={l.label}>
                      <a
                        href={l.href}
                        className="text-slate-500 transition-colors hover:text-brand-600"
                      >
                        {l.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </Container>
    </footer>
  );
}
