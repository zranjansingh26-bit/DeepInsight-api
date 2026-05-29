"use client";

import { motion } from "framer-motion";
import { Container } from "@/components/ui/container";
import { stats } from "@/lib/site";

export function Stats() {
  return (
    <section className="relative isolate overflow-hidden py-20">
      <div className="absolute inset-0 -z-10 bg-violet-gradient" />
      <div
        aria-hidden
        className="hero-grain pointer-events-none absolute inset-0 -z-10 opacity-30 mix-blend-overlay"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -left-20 top-0 -z-10 h-72 w-72 rounded-full bg-violet-400/40 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -right-20 bottom-0 -z-10 h-72 w-72 rounded-full bg-violet-300/30 blur-3xl"
      />
      <Container>
        <div className="grid grid-cols-2 gap-y-10 sm:grid-cols-4">
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.07 }}
              className="text-center"
            >
              <p className="font-display text-5xl font-semibold text-white sm:text-6xl">
                {s.value}
              </p>
              <p className="mt-2 text-xs font-semibold uppercase tracking-[0.18em] text-violet-200">
                {s.label}
              </p>
            </motion.div>
          ))}
        </div>
      </Container>
    </section>
  );
}
