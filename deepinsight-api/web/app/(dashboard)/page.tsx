"use client";

import { motion } from "framer-motion";
import { UploadCloud, Activity, Database, Settings, MessageSquare, Plus, LogOut, FileText } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";

export default function Home() {
  const { user, profile, signOut } = useAuth();

  return (
    <div className="min-h-screen flex w-full">
      {/* Sidebar */}
      <motion.aside 
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-64 glass-panel border-r border-slate-700/50 flex flex-col h-screen"
      >
        <div className="p-6">
          <h1 className="text-2xl font-bold gradient-text">DeepInsights</h1>
        </div>
        
        <nav className="flex-1 px-4 space-y-2">
          <NavItem icon={<Database size={20} />} label="Datasets" href="/" active />
          <NavItem icon={<Activity size={20} />} label="Analyses" href="/" />
          <NavItem icon={<MessageSquare size={20} />} label="AI Chat" href="/chat" />
          <NavItem icon={<FileText size={20} />} label="Reports" href="/reports" />
          <NavItem icon={<Settings size={20} />} label="Settings" href="/" />
        </nav>
        
        <div className="p-4 border-t border-slate-700/50">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center font-bold">
              {profile?.display_name?.charAt(0) || user?.email?.charAt(0) || "U"}
            </div>
            <div>
              <p className="text-sm font-medium text-white truncate max-w-[120px]" title={user?.email}>
                {profile?.display_name || user?.email}
              </p>
              <p className="text-xs text-indigo-400 capitalize">{profile?.plan || 'Free'} Plan</p>
            </div>
          </div>
          <button 
            onClick={() => signOut()}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-white">Overview</h2>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <Plus size={18} />
            New Analysis
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard title="Active Datasets" value="12" change="+2 this week" />
          <StatCard title="Models Trained" value="48" change="+5 this week" />
          <StatCard title="API Requests" value="1.2k" change="Normal limits" />
        </div>

        <div className="glass-panel rounded-xl p-8 text-center">
          <UploadCloud className="mx-auto h-16 w-16 text-indigo-400 mb-4" />
          <h3 className="text-xl font-medium text-white mb-2">Upload a new dataset</h3>
          <p className="text-slate-400 mb-6">Drop your CSV, JSON, or Excel file here to start exploring.</p>
          <button className="border border-indigo-500 text-indigo-400 hover:bg-indigo-500/10 px-6 py-2 rounded-lg transition-colors">
            Browse Files
          </button>
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, href = "#", active = false }: { icon: React.ReactNode, label: string, href?: string, active?: boolean }) {
  return (
    <Link href={href} className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${active ? 'bg-indigo-500/20 text-indigo-300' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}>
      {icon}
      <span className="font-medium">{label}</span>
    </Link>
  );
}

function StatCard({ title, value, change }: { title: string, value: string, change: string }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="glass-panel rounded-xl p-6"
    >
      <h3 className="text-sm font-medium text-slate-400">{title}</h3>
      <p className="text-3xl font-bold text-white mt-2">{value}</p>
      <p className="text-xs text-emerald-400 mt-2">{change}</p>
    </motion.div>
  );
}
