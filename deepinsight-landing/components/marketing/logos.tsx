import { Container } from "@/components/ui/container";
import { trustedLogos } from "@/lib/site";

export function Logos() {
  return (
    <section className="border-y border-violet-100/70 bg-white/40 py-10 backdrop-blur">
      <Container>
        <p className="text-center text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
          Trusted by analysts and operators at
        </p>
        <div className="mt-6 grid grid-cols-2 items-center justify-items-center gap-x-10 gap-y-6 sm:grid-cols-3 lg:grid-cols-6">
          {trustedLogos.map((logo) => (
            <span
              key={logo}
              className="font-display text-lg font-semibold tracking-tight text-slate-300 grayscale transition-colors duration-300 hover:text-violet-700"
            >
              {logo}
            </span>
          ))}
        </div>
      </Container>
    </section>
  );
}
