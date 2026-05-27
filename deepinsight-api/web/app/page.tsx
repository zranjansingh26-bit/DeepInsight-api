"use client";

import { motion } from "framer-motion";
import { ArrowRight, Activity, Cpu, Lock, Zap, PieChart, MessagesSquare } from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-300 selection:bg-indigo-500/30 overflow-hidden">
      {/* Dynamic Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-[20%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-[20%] w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[150px]" />
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay" />
      </div>

      {/* Navbar */}
      <nav className="relative z-50 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center text-white font-bold text-xl relative overflow-hidden group">
            <span className="relative z-10">D</span>
            <div className="absolute inset-0 bg-gradient-to-t from-indigo-600 to-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <span className="font-bold text-xl text-white tracking-tight">DeepInsights</span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-medium">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#models" className="hover:text-white transition-colors">ML Lab</a>
          <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium hover:text-white transition-colors">
            Sign In
          </Link>
          <Link href="/signup" className="text-sm font-medium bg-white text-black px-4 py-2 rounded-full hover:bg-slate-200 transition-colors">
            Start Free Trial
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 pt-24 pb-32 px-4 text-center max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium mb-8">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
            DeepInsights v2.0 is now live
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight mb-8 leading-tight">
            Turn raw data into <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
              predictive intelligence
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed">
            Upload your datasets and let our enterprise-grade AI automatically clean, model, forecast, and generate board-ready reports in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link 
              href="/signup"
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-full font-medium text-lg transition-all shadow-[0_0_40px_rgba(79,70,229,0.3)] hover:shadow-[0_0_60px_rgba(79,70,229,0.5)]"
            >
              Start 14-day free trial <ArrowRight size={20} />
            </Link>
            <button className="flex items-center gap-2 px-8 py-4 rounded-full font-medium text-lg border border-slate-700 hover:bg-slate-800 transition-all">
              View Demo
            </button>
          </div>
        </motion.div>

        {/* Dashboard Preview mockup */}
        <motion.div 
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="mt-24 relative mx-auto max-w-5xl"
        >
          <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-transparent to-transparent z-20" />
          <div className="glass-panel p-2 rounded-2xl border border-slate-800 shadow-2xl relative z-10 overflow-hidden bg-slate-900/50">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800/80 bg-slate-900/80">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
              </div>
            </div>
            {/* Fake dashboard content */}
            <div className="p-8 grid grid-cols-3 gap-6 opacity-60">
              <div className="col-span-2 space-y-6">
                <div className="h-64 rounded-xl bg-gradient-to-br from-slate-800 to-slate-800/40 border border-slate-700/50 flex items-end p-6 gap-2">
                  {[40, 70, 45, 90, 65, 120, 85].map((h, i) => (
                    <motion.div 
                      key={i}
                      initial={{ height: 0 }}
                      animate={{ height: h }}
                      transition={{ duration: 1, delay: 0.5 + (i * 0.1) }}
                      className="flex-1 bg-indigo-500/80 rounded-t-sm"
                    />
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="h-32 rounded-xl bg-slate-800/50 border border-slate-700/50" />
                  <div className="h-32 rounded-xl bg-slate-800/50 border border-slate-700/50" />
                </div>
              </div>
              <div className="col-span-1 space-y-6">
                <div className="h-[410px] rounded-xl bg-slate-800/30 border border-slate-700/50 p-6 flex flex-col">
                  <div className="w-24 h-4 bg-slate-700 rounded mb-6" />
                  <div className="flex-1 space-y-4">
                    <div className="w-full h-12 bg-indigo-500/10 border border-indigo-500/20 rounded-lg flex items-center px-4 gap-3">
                      <div className="w-6 h-6 rounded bg-indigo-500/30" />
                      <div className="w-32 h-2 bg-indigo-500/40 rounded" />
                    </div>
                    <div className="w-full h-12 bg-slate-800/50 rounded-lg" />
                    <div className="w-full h-12 bg-slate-800/50 rounded-lg" />
                    <div className="w-full h-12 bg-slate-800/50 rounded-lg" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </main>
      
      {/* Feature Grid */}
      <section id="features" className="py-24 relative z-10 border-t border-slate-800/50 bg-slate-900/20">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Everything you need to scale analytics</h2>
            <p className="text-slate-400">Replaces 5 different tools with one seamless AI workflow.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Cpu className="w-6 h-6 text-indigo-400" />}
              title="AutoML Model Lab"
              desc="Train, compare, and optimize models across Classification, Regression, and Clustering automatically."
            />
            <FeatureCard 
              icon={<Activity className="w-6 h-6 text-purple-400" />}
              title="Dynamic Forecasting"
              desc="Advanced SARIMA, Exponential Smoothing, and Prophet models with automatic seasonality detection."
            />
            <FeatureCard 
              icon={<MessagesSquare className="w-6 h-6 text-pink-400" />}
              title="ChatGPT for Data"
              desc="Chat with your datasets. Ask questions in plain English and get instant charts, code, and insights."
            />
            <FeatureCard 
              icon={<PieChart className="w-6 h-6 text-emerald-400" />}
              title="Report Co-Creation"
              desc="Generate PowerPoint and PDF board decks instantly with AI-written executive summaries."
            />
            <FeatureCard 
              icon={<Zap className="w-6 h-6 text-yellow-400" />}
              title="Asynchronous Scale"
              desc="Powered by Celery and Redis to handle massive datasets without freezing your browser."
            />
            <FeatureCard 
              icon={<Lock className="w-6 h-6 text-blue-400" />}
              title="Enterprise Security"
              desc="Multi-tenant workspaces, SSO integrations, and SOC-2 ready audit logging built-in."
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
  return (
    <div className="glass-panel p-8 rounded-2xl border border-slate-800 hover:border-slate-700 transition-colors group">
      <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{desc}</p>
    </div>
  );
}
