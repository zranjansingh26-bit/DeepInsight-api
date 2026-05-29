"use client";

import { motion } from "framer-motion";
import { Play, Sparkles } from "lucide-react";
import { Container } from "@/components/ui/container";

export function Demo() {
  return (
    <section id="demo" className="section">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <span className="eyebrow">See it work</span>
          <h2 className="mt-5 section-title text-balance">
            Watch DeepInsight analyse a 10K-row dataset{" "}
            <span className="gradient-text">in real time.</span>
          </h2>
          <p className="mt-5 lead">
            From file upload to executive narrative in under two minutes. No
            scripts. No data team. Just an answer you can ship.
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.8 }}
          className="relative mx-auto mt-12 max-w-5xl"
        >
          <div className="absolute -inset-8 -z-10 rounded-[40px] bg-violet-gradient opacity-15 blur-3xl" />
          <button className="group relative block w-full overflow-hidden rounded-3xl border border-violet-100 bg-white shadow-lift">
            <div className="aspect-[16/9] bg-violet-gradient">
              <div className="absolute inset-0 grid place-items-center">
                <div className="text-center">
                  <span className="inline-flex h-20 w-20 items-center justify-center rounded-full bg-white text-violet-700 shadow-lift transition-transform duration-300 group-hover:scale-105">
                    <Play className="ml-1 h-8 w-8" fill="currentColor" />
                  </span>
                  <p className="mt-6 font-display text-2xl font-semibold text-white">
                    2-minute product tour
                  </p>
                  <p className="mt-1 text-sm text-violet-100">
                    Upload · Analyse · Chat · Report
                  </p>
                </div>
              </div>
              <div
                aria-hidden
                className="hero-grain absolute inset-0 opacity-25 mix-blend-overlay"
              />
              <div className="absolute left-6 top-6 inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1.5 text-xs font-semibold text-white backdrop-blur">
                <Sparkles className="h-3 w-3" /> Live workflow recording
              </div>
            </div>
          </button>
        </motion.div>
      </Container>
    </section>
  );
}
