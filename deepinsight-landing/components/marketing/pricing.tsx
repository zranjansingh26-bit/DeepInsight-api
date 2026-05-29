"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { plans } from "@/lib/site";
import { cn } from "@/lib/utils";

export function Pricing() {
  const [annual, setAnnual] = React.useState(true);

  return (
    <section id="pricing" className="section bg-cloud/60">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="eyebrow">Pricing</span>
          <h2 className="mt-5 section-title text-balance">
            Simple pricing,{" "}
            <span className="gradient-text">scaling with your team.</span>
          </h2>
          <p className="mt-5 lead">
            Start free for 14 days. No credit card. Cancel anytime. Annual
            plans save you 20%.
          </p>

          <div className="mt-8 inline-flex items-center gap-2 rounded-full border border-violet-100 bg-white/80 p-1.5 shadow-soft backdrop-blur">
            <button
              onClick={() => setAnnual(false)}
              className={cn(
                "rounded-full px-4 py-1.5 text-sm font-semibold transition-colors",
                !annual
                  ? "bg-violet-gradient text-white shadow-glow"
                  : "text-slate-500 hover:text-violet-700"
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setAnnual(true)}
              className={cn(
                "inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-semibold transition-colors",
                annual
                  ? "bg-violet-gradient text-white shadow-glow"
                  : "text-slate-500 hover:text-violet-700"
              )}
            >
              Annual
              <span
                className={cn(
                  "rounded-full px-1.5 py-0.5 text-[10px] font-bold",
                  annual
                    ? "bg-white/20 text-white"
                    : "bg-violet-100 text-violet-700"
                )}
              >
                –20%
              </span>
            </button>
          </div>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-4">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6, delay: i * 0.07 }}
              className={cn(
                "relative flex flex-col rounded-3xl border bg-white/95 p-7 shadow-soft transition-all duration-300 hover:-translate-y-1 hover:shadow-lift",
                plan.highlighted
                  ? "border-violet-300 ring-2 ring-violet-200"
                  : "border-violet-100"
              )}
            >
              {"ribbon" in plan && plan.ribbon && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-violet-gradient px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-white shadow-glow">
                  {plan.ribbon}
                </span>
              )}

              <div>
                <p className="font-display text-xl font-semibold text-ink">
                  {plan.name}
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  {plan.description}
                </p>
              </div>

              <div className="mt-6 flex items-end gap-1">
                {plan.price === null ? (
                  <span className="font-display text-3xl font-semibold text-ink">
                    Custom
                  </span>
                ) : (
                  <>
                    <span className="font-display text-5xl font-semibold text-ink">
                      ${annual ? plan.annual : plan.price}
                    </span>
                    <span className="pb-2 text-sm text-slate-400">
                      {plan.cadence}
                    </span>
                  </>
                )}
              </div>
              {plan.price !== null && annual && (
                <p className="mt-1 text-xs text-slate-400">
                  Billed annually · ${(plan.annual as number) * 12}/yr
                </p>
              )}

              <Button
                className="mt-6 w-full justify-center"
                variant={plan.highlighted ? "primary" : "ghost"}
                asChild
              >
                <a href="/signup">{plan.cta}</a>
              </Button>

              <ul className="mt-7 space-y-3 border-t border-violet-100 pt-7 text-sm">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-3 text-slate-600">
                    <span className="mt-0.5 inline-flex h-5 w-5 items-center justify-center rounded-full bg-violet-100 text-violet-700">
                      <Check className="h-3 w-3" strokeWidth={3} />
                    </span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        <p className="mt-8 text-center text-sm text-slate-400">
          All plans include unlimited analyses, JSON / HTML / PDF reports, and
          multi-LLM chat. Need something custom?{" "}
          <a
            href="#"
            className="font-semibold text-violet-700 hover:text-violet-800"
          >
            Talk to sales →
          </a>
        </p>
      </Container>
    </section>
  );
}
