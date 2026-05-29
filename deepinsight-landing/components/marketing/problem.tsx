"use client";

import { motion } from "framer-motion";
import { Sheet, Users, Layers } from "lucide-react";
import { Container } from "@/components/ui/container";
import { problems } from "@/lib/site";

const ICON = { Sheet, Users, Layers } as const;

export function Problem() {
  return (
    <section className="section">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="eyebrow">The opportunity</span>
          <h2 className="mt-5 section-title text-balance">
            Built for businesses with data{" "}
            <span className="gradient-text">but no analysts.</span>
          </h2>
          <p className="mt-5 lead">
            Three walls keep great decisions out of reach. DeepInsight is the
            shortcut around all three.
          </p>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {problems.map((p, idx) => {
            const Icon = ICON[p.icon as keyof typeof ICON];
            return (
              <motion.div
                key={p.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.6, delay: idx * 0.1, ease: [0.16, 1, 0.3, 1] }}
                className="card-soft"
              >
                <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-50 text-violet-700 ring-1 ring-violet-200">
                  <Icon className="h-5 w-5" />
                </span>
                <h3 className="mt-5 font-display text-xl font-semibold text-ink">
                  {p.title}
                </h3>
                <p className="mt-3 text-[15px] leading-relaxed text-slate-500">
                  {p.body}
                </p>
              </motion.div>
            );
          })}
        </div>
      </Container>
    </section>
  );
}
