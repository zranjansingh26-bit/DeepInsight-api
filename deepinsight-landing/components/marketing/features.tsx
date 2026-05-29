"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { Container } from "@/components/ui/container";

export function Features() {
  return (
    <section id="features" className="py-24 sm:py-32 bg-white">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl sm:text-4xl lg:text-[2.5rem] font-medium text-ink tracking-tight text-balance">
            Advanced <Sparkles className="inline-block h-6 w-6 text-brand-500 mx-1" /> Features That Empower Your Business
          </h2>
          <p className="mt-4 text-sm text-slate-500 uppercase tracking-widest font-semibold max-w-md mx-auto">
            HARNESS THE POWER OF AI TO TRANSFORM YOUR MARKET RESEARCH AND STRATEGY
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {/* Top Left: Import Export Performance (Dot Matrix) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="rounded-[2rem] border border-slate-100 bg-white p-6 sm:p-8 shadow-sm flex flex-col justify-between h-72"
          >
            <div className="flex justify-between items-start">
              <h3 className="font-display text-sm font-semibold text-ink">Import Export Performance</h3>
            </div>
            <div className="flex-1 flex items-end justify-center mt-4">
              <DotMatrixChart />
            </div>
          </motion.div>

          {/* Top Right: Conversion Rate (Bar Chart) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-[2rem] border border-slate-100 bg-white p-6 sm:p-8 shadow-sm flex flex-col justify-between h-72"
          >
            <div className="flex justify-between items-start">
              <h3 className="font-display text-sm font-semibold text-ink">Conversion Rate</h3>
              <span className="text-2xl font-bold text-ink tracking-tight">72,5%</span>
            </div>
            <div className="flex-1 flex items-end mt-4">
              <BarChart />
            </div>
          </motion.div>

          {/* Bottom Left: Performance Index S&P 500 (Line/Area Chart equivalent) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="rounded-[2rem] border border-slate-100 bg-white p-6 sm:p-8 shadow-sm flex flex-col justify-between h-72 md:col-span-2"
          >
            <div className="flex justify-between items-center">
              <h3 className="font-display text-sm font-semibold text-ink">Performance Index S&P 500 <span className="ml-2 text-xs font-normal text-emerald-500">+1.5%</span></h3>
              <div className="flex gap-2">
                <span className="h-2 w-2 rounded-full bg-brand-500"></span>
                <span className="h-2 w-2 rounded-full bg-slate-300"></span>
                <span className="h-2 w-2 rounded-full bg-slate-300"></span>
              </div>
            </div>
            <div className="flex-1 mt-6 w-full">
              <LineChart />
            </div>
          </motion.div>
        </div>
      </Container>
    </section>
  );
}

function DotMatrixChart() {
  // A simple grid of dots, some filled solid, some light
  const rows = 4;
  const cols = 9;
  return (
    <div className="w-full flex justify-between gap-1 items-end h-full pt-4">
      {Array.from({ length: cols }).map((_, c) => (
        <div key={c} className="flex flex-col gap-1.5 sm:gap-2">
          {Array.from({ length: rows }).map((_, r) => {
            const isFilled = Math.random() > 0.4 || (c < 3 && r > 0);
            return (
              <div
                key={r}
                className={`w-4 h-4 sm:w-6 sm:h-6 rounded-full ${
                  isFilled ? "bg-brand-600" : "bg-brand-100"
                }`}
              />
            );
          })}
        </div>
      ))}
      <div className="flex flex-col gap-1.5 sm:gap-2 ml-2 sm:ml-4 text-[10px] text-slate-400 font-medium justify-between py-1">
        <span>US</span>
        <span>UK</span>
        <span>CA</span>
        <span>JP</span>
      </div>
    </div>
  );
}

function BarChart() {
  const heights = [40, 60, 100, 70, 85];
  return (
    <div className="w-full flex justify-between items-end h-full gap-2">
      {heights.map((h, i) => (
        <div key={i} className="flex flex-col items-center gap-2 w-full">
          <motion.div
            initial={{ height: 0 }}
            whileInView={{ height: `${h}%` }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, delay: 0.2 + i * 0.1 }}
            className={`w-full rounded-t-xl ${
              i === 2 ? "bg-brand-600" : "bg-brand-600"
            }`}
          />
        </div>
      ))}
    </div>
  );
}

function LineChart() {
  return (
    <svg viewBox="0 0 400 100" className="w-full h-full overflow-visible" preserveAspectRatio="none">
      <defs>
        <linearGradient id="lineGrad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#4F46E5" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#4F46E5" stopOpacity="0" />
        </linearGradient>
      </defs>
      {/* Grid lines */}
      <line x1="0" y1="20" x2="400" y2="20" stroke="#f1f5f9" strokeWidth="1" />
      <line x1="0" y1="50" x2="400" y2="50" stroke="#f1f5f9" strokeWidth="1" />
      <line x1="0" y1="80" x2="400" y2="80" stroke="#f1f5f9" strokeWidth="1" />
      
      {/* Line path */}
      <path
        d="M0 60 C50 60, 80 30, 120 40 C160 50, 180 80, 220 70 C260 60, 280 20, 320 25 C360 30, 380 50, 400 50"
        fill="none"
        stroke="#4F46E5"
        strokeWidth="3"
        strokeLinecap="round"
      />
      
      {/* Fill path */}
      <path
        d="M0 60 C50 60, 80 30, 120 40 C160 50, 180 80, 220 70 C260 60, 280 20, 320 25 C360 30, 380 50, 400 50 L400 100 L0 100 Z"
        fill="url(#lineGrad)"
      />
      
      {/* Data points */}
      <circle cx="120" cy="40" r="4" fill="#fff" stroke="#4F46E5" strokeWidth="2" />
      <circle cx="220" cy="70" r="4" fill="#fff" stroke="#4F46E5" strokeWidth="2" />
      <circle cx="320" cy="25" r="5" fill="#4F46E5" />
      
      {/* X axis labels */}
      <text x="0" y="115" fontSize="10" fill="#94a3b8">Jan</text>
      <text x="80" y="115" fontSize="10" fill="#94a3b8">Feb</text>
      <text x="160" y="115" fontSize="10" fill="#94a3b8">Mar</text>
      <text x="240" y="115" fontSize="10" fill="#94a3b8">Apr</text>
      <text x="320" y="115" fontSize="10" fill="#4F46E5" fontWeight="bold">May</text>
      <text x="380" y="115" fontSize="10" fill="#94a3b8">Jun</text>
    </svg>
  );
}
