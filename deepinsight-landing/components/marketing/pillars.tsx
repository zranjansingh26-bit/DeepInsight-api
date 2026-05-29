"use client";

import { motion } from "framer-motion";
import { Check, Cpu, MessageSquareText } from "lucide-react";
import { Container } from "@/components/ui/container";
import { pillars } from "@/lib/site";

const ICONS = [Cpu, MessageSquareText];

export function Pillars() {
  return (
    <section id="pillars" className="section bg-cloud/60">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="eyebrow">The platform</span>
          <h2 className="mt-5 section-title text-balance">
            Two engines.{" "}
            <span className="gradient-text">One product.</span>
          </h2>
          <p className="mt-5 lead">
            The rigour of a data scientist and the voice of a senior analyst -
            wired together so neither can lie to the other.
          </p>
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-2">
          {pillars.map((pillar, idx) => {
            const Icon = ICONS[idx];
            return (
              <motion.article
                key={pillar.title}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.7, delay: idx * 0.1, ease: [0.16, 1, 0.3, 1] }}
                className="relative overflow-hidden rounded-3xl border border-violet-100 bg-white/90 p-8 shadow-soft transition-shadow hover:shadow-lift"
              >
                <div
                  aria-hidden
                  className="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-violet-200/40 blur-3xl"
                />
                <div className="flex items-center gap-3">
                  <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-violet-gradient text-white shadow-glow">
                    <Icon className="h-5 w-5" />
                  </span>
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-violet-700">
                      {pillar.eyebrow}
                    </p>
                    <p className="font-display text-sm font-semibold text-slate-400">
                      {pillar.subtitle}
                    </p>
                  </div>
                </div>

                <h3 className="mt-6 font-display text-display-3 font-semibold text-ink">
                  {pillar.title}
                </h3>
                <p className="mt-3 text-[15px] leading-relaxed text-slate-500">
                  {pillar.body}
                </p>

                <ul className="mt-6 grid gap-2.5">
                  {pillar.bullets.map((b) => (
                    <li
                      key={b}
                      className="flex items-start gap-3 text-sm text-slate-600"
                    >
                      <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700">
                        <Check className="h-3 w-3" strokeWidth={3} />
                      </span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </motion.article>
            );
          })}
        </div>
      </Container>
    </section>
  );
}
