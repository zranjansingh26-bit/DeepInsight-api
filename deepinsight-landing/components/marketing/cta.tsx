"use client";

import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { Container } from "@/components/ui/container";

export function CTA() {
  return (
    <section className="py-24 bg-white">
      <Container>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="relative isolate overflow-hidden rounded-[2.5rem] bg-navy-950 px-8 py-20 sm:px-16 sm:py-24 max-w-5xl mx-auto"
        >
          {/* Subtle gradient bursts inside the CTA */}
          <div className="absolute top-0 right-0 -mr-24 -mt-24 h-64 w-64 rounded-full bg-brand-600/20 blur-[60px]"></div>
          <div className="absolute bottom-0 left-0 -ml-24 -mb-24 h-64 w-64 rounded-full bg-brand-500/20 blur-[60px]"></div>

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-10">
            <div className="max-w-xl">
              <h2 className="font-display text-3xl sm:text-4xl lg:text-[2.5rem] font-medium text-white text-balance tracking-tight leading-[1.1]">
                Revolutionize <Sparkles className="inline-block h-6 w-6 text-brand-400 mx-1" /> Your
                <br className="hidden sm:block" />
                Strategy With AI
                <br className="hidden sm:block" />
                Analytics
              </h2>
              <p className="mt-6 text-sm sm:text-base text-white/60">
                AI analytics that drive smarter decisions
                <br className="hidden sm:block" />
                and success.
              </p>
            </div>
            
            <div className="flex flex-col items-start gap-4">
              <div className="flex flex-wrap items-center gap-4">
                <a
                  href="/signup"
                  className="inline-flex h-11 items-center justify-center rounded-full bg-brand-500 px-8 text-sm font-medium text-white shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all hover:bg-brand-400"
                >
                  Free Trial
                </a>
                <a
                  href="#demo"
                  className="inline-flex h-11 items-center justify-center rounded-full border border-white/20 bg-transparent px-8 text-sm font-medium text-white transition-all hover:bg-white/5"
                >
                  Watch Demo &rsaquo;
                </a>
              </div>
              <p className="text-[10px] text-white/40 pl-2">
                *No credit card require
              </p>
            </div>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}
