"use client";

import { Container } from "@/components/ui/container";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { useCases } from "@/lib/site";

export function UseCases() {
  return (
    <section id="usecases" className="section">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="eyebrow">Built for every team</span>
          <h2 className="mt-5 section-title text-balance">
            One platform.{" "}
            <span className="gradient-text">Every team.</span>
          </h2>
          <p className="mt-5 lead">
            From ecommerce to multi-location operations, DeepInsight ships
            with workflows tuned for the way each team actually decides.
          </p>
        </div>

        <Tabs defaultValue={useCases[0].key} className="mt-12">
          <div className="flex justify-center">
            <TabsList>
              {useCases.map((u) => (
                <TabsTrigger key={u.key} value={u.key}>
                  {u.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          {useCases.map((u) => (
            <TabsContent key={u.key} value={u.key}>
              <div className="mx-auto max-w-5xl rounded-3xl border border-violet-100 bg-white/90 p-8 shadow-soft sm:p-10">
                <div className="grid gap-8 lg:grid-cols-3">
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-violet-700">
                      Persona
                    </p>
                    <p className="mt-2 font-display text-2xl font-semibold text-ink">
                      {u.persona}
                    </p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-rose-500">
                      Pain
                    </p>
                    <p className="mt-2 text-[15px] leading-relaxed text-slate-600">
                      {u.pain}
                    </p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-600">
                      Outcome with DeepInsight
                    </p>
                    <p className="mt-2 text-[15px] leading-relaxed text-slate-600">
                      {u.outcome}
                    </p>
                  </div>
                </div>
              </div>
            </TabsContent>
          ))}
        </Tabs>
      </Container>
    </section>
  );
}
