"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { Container } from "@/components/ui/container";

export function Revolutionize() {
  return (
    <section id="how-it-works" className="py-24 sm:py-32 bg-slate-50/50">
      <Container>
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl sm:text-4xl lg:text-[2.5rem] font-medium text-ink tracking-tight text-balance">
            How <Sparkles className="inline-block h-6 w-6 text-brand-500 mx-1" /> Our AI Tools Revolutionize Your Business
          </h2>
          <p className="mt-4 text-sm sm:text-base text-slate-500 max-w-lg mx-auto">
            Revolutionize your analysis and strategy with AI tools that provide real-time insights, predict trends, and optimize decisions.
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {/* Left Card: Dark Blue */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="rounded-[2rem] bg-navy-900 p-6 sm:p-8 shadow-sm flex flex-col justify-between h-80 relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 -mr-16 -mt-16 h-48 w-48 rounded-full bg-brand-600/30 blur-3xl"></div>
            
            <div className="flex items-center gap-2 mb-6">
              <div className="flex -space-x-2">
                <span className="inline-block h-8 w-8 rounded-full bg-brand-500 ring-2 ring-navy-900 overflow-hidden">
                  <img src="https://i.pravatar.cc/100?img=1" alt="Avatar" className="h-full w-full object-cover" />
                </span>
                <span className="inline-block h-8 w-8 rounded-full bg-brand-400 ring-2 ring-navy-900 overflow-hidden">
                  <img src="https://i.pravatar.cc/100?img=2" alt="Avatar" className="h-full w-full object-cover" />
                </span>
                <span className="inline-block h-8 w-8 rounded-full bg-rose-500 ring-2 ring-navy-900 overflow-hidden">
                  <img src="https://i.pravatar.cc/100?img=3" alt="Avatar" className="h-full w-full object-cover" />
                </span>
              </div>
            </div>

            <p className="font-display text-lg text-white font-medium leading-snug">
              Use AI To Predict Market Trends, Enabling Proactive Decisions And Strategy Adjustments.
            </p>
          </motion.div>

          {/* Middle Card: Predict Trends */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-[2rem] border border-slate-100 bg-white p-6 sm:p-8 shadow-sm flex flex-col justify-between h-80"
          >
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-display text-xl font-semibold text-ink leading-tight">Predict<br/>Trends With AI</h3>
              </div>
              <span className="mt-3 inline-flex items-center rounded-full bg-brand-50 px-2.5 py-0.5 text-[10px] font-semibold text-brand-700">
                Monthly <span className="ml-1 text-[8px]">▼</span>
              </span>
            </div>

            <div>
              <p className="text-xs text-slate-400 font-medium uppercase tracking-wider mb-2">AI Assistant</p>
              <div className="flex items-center gap-2 mb-6">
                <div className="h-8 w-8 rounded-lg bg-brand-600 flex items-center justify-center">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <span className="font-display font-semibold text-ink text-lg">16 <span className="text-sm font-normal text-slate-500">/ Month</span></span>
              </div>
              
              <div className="flex items-center justify-between border-t border-slate-100 pt-4">
                <span className="text-xs font-medium text-slate-500">Productivity Increase</span>
                <span className="inline-flex items-center rounded bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700">
                  2X
                </span>
              </div>
            </div>
          </motion.div>

          {/* Right Card: Optimize Business Decisions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="rounded-[2rem] border border-slate-100 bg-white p-6 sm:p-8 shadow-sm flex flex-col items-center justify-between h-80"
          >
            <div className="w-full">
              <h3 className="font-display text-xl font-semibold text-ink leading-tight">Optimize Business<br/>Decisions</h3>
              <span className="mt-3 inline-flex items-center rounded-full bg-brand-50 px-2.5 py-0.5 text-[10px] font-semibold text-brand-700">
                Option L1 <span className="ml-1 text-[8px]">▼</span>
              </span>
            </div>

            <div className="flex-1 flex flex-col items-center justify-center mt-6 w-full">
              <div className="relative h-32 w-32">
                <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
                  <circle cx="50" cy="50" r="44" stroke="#F1F5F9" strokeWidth="8" fill="none" />
                  <circle
                    cx="50"
                    cy="50"
                    r="44"
                    stroke="#4F46E5"
                    strokeWidth="8"
                    strokeLinecap="round"
                    fill="none"
                    strokeDasharray="276"
                    strokeDashoffset={276 * (1 - 0.75)}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="font-display text-3xl font-bold text-ink tracking-tight">75<span className="text-xs font-medium text-slate-400">/100</span></span>
                </div>
              </div>
              <p className="mt-4 text-[10px] text-slate-400 font-medium">Percentage/Right Decisions</p>
            </div>
          </motion.div>
        </div>
      </Container>
    </section>
  );
}
