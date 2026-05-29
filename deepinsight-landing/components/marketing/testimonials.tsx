"use client";

import { motion } from "framer-motion";
import { Sparkles, Layers } from "lucide-react";
import { Container } from "@/components/ui/container";

export function Testimonials() {
  return (
    <section id="testimonials" className="py-24 sm:py-32 bg-white">
      <Container>
        <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Header Area within the grid to match the layout */}
          <div className="lg:col-span-3">
            <h2 className="font-display text-3xl sm:text-4xl lg:text-[2.5rem] font-medium text-ink tracking-tight text-balance">
              Trusted <Sparkles className="inline-block h-6 w-6 text-brand-500 mx-1" /> By Team<br/>Everywhere <span className="inline-block h-6 w-6 rounded-full bg-brand-100 ring-2 ring-white"></span>
            </h2>
            <p className="mt-4 text-sm sm:text-base text-slate-500 max-w-sm">
              AI analytics that drive smarter decisions and success.
            </p>
          </div>

          {/* Large Testimonial Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="rounded-[2rem] border border-slate-100 bg-white p-8 sm:p-12 shadow-sm flex flex-col justify-between h-auto min-h-[300px] lg:col-span-2"
          >
            <p className="font-display text-lg sm:text-xl text-ink leading-relaxed font-medium">
              "Using This AI Solution Has Revolutionized Our Business Strategy. The
              Predictive Capabilities Have Enabled Us To Anticipate Trends And Stay
              Ahead Of The Competition. It's A Game-Changer For Anyone Looking To
              Optimize Their Decision-Making Process."
            </p>
            
            <div className="mt-12 flex items-center gap-4">
              <span className="inline-block h-10 w-10 rounded-full bg-brand-200 overflow-hidden">
                <img src="https://i.pravatar.cc/100?img=4" alt="Avatar" className="h-full w-full object-cover" />
              </span>
              <p className="text-xs sm:text-sm font-semibold text-ink uppercase tracking-wider">
                Richard Roe, Researcher Director
              </p>
            </div>
          </motion.div>

          {/* Right Visual Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="rounded-[2rem] bg-[#E8E8EE] p-6 sm:p-8 shadow-inner flex flex-col h-auto min-h-[300px] relative overflow-hidden"
          >
            <h3 className="font-display text-lg font-semibold text-ink">
              Precision, Clarity, Efficiency.
            </h3>
            
            <div className="flex-1 flex items-end justify-end mt-8 relative">
              {/* Approximating the 3D layered folders with SVG/CSS shapes */}
              <div className="relative w-full h-40 flex items-end justify-center">
                <div className="absolute bottom-0 w-32 h-24 bg-brand-500 rounded-xl transform -rotate-12 translate-x-4 translate-y-4 shadow-lg"></div>
                <div className="absolute bottom-0 w-32 h-24 bg-rose-400 rounded-xl transform -rotate-6 translate-x-2 translate-y-2 shadow-lg"></div>
                <div className="absolute bottom-0 w-32 h-24 bg-amber-300 rounded-xl shadow-lg"></div>
                <div className="absolute bottom-0 w-32 h-24 bg-emerald-400 rounded-xl transform rotate-6 -translate-x-2 translate-y-2 shadow-lg"></div>
                <div className="absolute bottom-0 w-32 h-24 bg-cyan-300 rounded-xl transform rotate-12 -translate-x-4 translate-y-4 shadow-lg"></div>
              </div>
            </div>
          </motion.div>
        </div>
      </Container>
    </section>
  );
}
