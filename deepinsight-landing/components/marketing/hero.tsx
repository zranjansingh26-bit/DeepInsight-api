"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Container } from "@/components/ui/container";
import { partners } from "@/lib/site";

export function Hero() {
  return (
    <section className="relative isolate overflow-hidden bg-navy-950 pt-48 pb-20 sm:pt-56 lg:pb-28">
      {/* Layered background */}
      <BackgroundLayers />

      <Container className="relative text-center z-10">
        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="mx-auto max-w-4xl font-display text-4xl sm:text-5xl lg:text-[4rem] font-medium text-white tracking-tight leading-[1.1] text-balance"
        >
          Unlock Powerful Market
          <span className="block">
            Insights With AI
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="mx-auto mt-8 max-w-xl text-sm sm:text-base leading-relaxed text-white/60 font-light"
        >
          Transform your business strategy with data-driven
          <br className="hidden sm:block" />
          predictions and sentiment analysis
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mt-10 flex flex-col items-center justify-center gap-4"
        >
          <div className="flex flex-col sm:flex-row items-center gap-4">
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
          <p className="text-[10px] text-white/40 -mt-1 mr-auto sm:mr-0 sm:-ml-28">
            *No credit card require
          </p>
        </motion.div>

        {/* Partner strip */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.3 }}
          className="mt-28 sm:mt-36"
        >
          <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6 opacity-40 grayscale transition-opacity hover:opacity-80">
            {/* Hardcoding simple SVG approximations or text for the logos to match the screenshot */}
            <span className="flex items-center gap-2 font-display text-lg font-semibold tracking-tight text-white">
              aws
            </span>
            <span className="flex items-center gap-2 font-display text-lg font-medium text-white">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><rect x="4" y="12" width="4" height="8" rx="1"/><rect x="10" y="4" width="4" height="16" rx="1"/><rect x="16" y="8" width="4" height="12" rx="1"/></svg>
              Google Analytics
            </span>
            <span className="flex items-center gap-2 font-display text-lg font-medium text-white">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
              Grok
            </span>
            <span className="flex items-center gap-2 font-display text-lg font-medium text-white">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
              OpenAI
            </span>
            <span className="flex items-center gap-2 font-display text-lg font-medium tracking-wide text-white">
              <span className="h-4 w-4 rounded-full border-2 border-current"></span>
              Polymath
            </span>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}

function BackgroundLayers() {
  return (
    <>
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-20 bg-navy-950"
      />
      {/* Central glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-[-20%] -z-10 h-[800px] w-[1000px] -translate-x-1/2 rounded-full"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(59,130,246,0.15) 0%, rgba(30,58,138,0.05) 40%, transparent 70%)",
          filter: "blur(40px)",
        }}
      />
      {/* Vertical light rays matching screenshot */}
      <LightRays />
    </>
  );
}

function LightRays() {
  // Creating a set of broad vertical stripes with varying opacities to match the image background
  const rays = [
    { left: "0%", width: "10%", opacity: 0.05 },
    { left: "10%", width: "8%", opacity: 0.1 },
    { left: "18%", width: "12%", opacity: 0.15 },
    { left: "30%", width: "6%", opacity: 0.08 },
    { left: "36%", width: "14%", opacity: 0.2 },
    { left: "50%", width: "10%", opacity: 0.12 },
    { left: "60%", width: "15%", opacity: 0.18 },
    { left: "75%", width: "8%", opacity: 0.07 },
    { left: "83%", width: "10%", opacity: 0.15 },
    { left: "93%", width: "7%", opacity: 0.05 },
  ];

  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 -z-10 overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-navy-950/20 to-navy-950 z-10" />
      {rays.map((r, i) => (
        <div
          key={i}
          className="absolute top-0 h-full bg-gradient-to-b from-brand-600 to-transparent"
          style={{
            left: r.left,
            width: r.width,
            opacity: r.opacity,
            mixBlendMode: "screen",
          }}
        />
      ))}
    </div>
  );
}
