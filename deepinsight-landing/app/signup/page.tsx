"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowLeft, Lock, Mail, Sparkles, User } from "lucide-react";
import { site } from "@/lib/site";

export default function SignupPage() {
  const [displayName, setDisplayName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState("");
  const [successMsg, setSuccessMsg] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          display_name: displayName,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Registration failed. Try a different email.");
      }

      // Check if session token was returned directly (auto-confirm enabled)
      if (data.session && data.session.access_token) {
        window.location.href = `http://localhost:8501/?token=${encodeURIComponent(
          data.session.access_token
        )}`;
      } else {
        setSuccessMsg(
          "Account created successfully! Please check your email inbox to verify your account before logging in."
        );
      }
    } catch (err: any) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-navy-950 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 overflow-hidden font-sans">
      {/* Background decoration */}
      <div className="pointer-events-none absolute inset-0 -z-10 bg-navy-950" />
      <div
        className="pointer-events-none absolute left-1/2 top-1/2 -z-10 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(99,102,241,0.1) 0%, rgba(30,58,138,0.02) 50%, transparent 70%)",
          filter: "blur(40px)",
        }}
      />

      <div className="absolute top-8 left-8">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-white/60 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to home
        </Link>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 text-center">
        <h2 className="font-display text-4xl font-semibold text-white tracking-tight">
          Start Your Free Trial
        </h2>
        <p className="mt-2 text-sm text-white/50">
          Create an account and start analyzing in 5 minutes
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="border border-white/10 bg-navy-900/60 shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] backdrop-blur-xl rounded-2xl py-8 px-4 sm:px-10">
          {error && (
            <div className="mb-6 rounded-lg bg-red-500/10 border border-red-500/30 p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          {successMsg ? (
            <div className="text-center space-y-6">
              <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-4 text-sm text-emerald-400">
                {successMsg}
              </div>
              <Link
                href="/login"
                className="w-full flex justify-center items-center gap-2 rounded-lg bg-brand-500 py-3 text-sm font-semibold text-white shadow-[0_0_20px_rgba(99,102,241,0.3)] transition-all hover:bg-brand-400"
              >
                Go to Sign In <Sparkles className="h-4 w-4" />
              </Link>
            </div>
          ) : (
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-white/70 mb-2"
                >
                  Display Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-white/40">
                    <User className="h-4 w-4" />
                  </div>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="Jane Doe"
                    className="block w-full pl-10 rounded-lg bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/20 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors text-sm"
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-white/70 mb-2"
                >
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-white/40">
                    <Mail className="h-4 w-4" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    className="block w-full pl-10 rounded-lg bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/20 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors text-sm"
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-white/70 mb-2"
                >
                  Password (min 6 chars)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-white/40">
                    <Lock className="h-4 w-4" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="block w-full pl-10 rounded-lg bg-white/5 border border-white/10 px-4 py-2.5 text-white placeholder-white/20 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors text-sm"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center items-center gap-2 rounded-lg bg-brand-500 py-3 text-sm font-semibold text-white shadow-[0_0_20px_rgba(99,102,241,0.3)] transition-all hover:bg-brand-400 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
                >
                  {loading ? (
                    "Creating Account..."
                  ) : (
                    <>
                      Register <Sparkles className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>
            </form>
          )}

          <div className="mt-8 pt-6 border-t border-white/5 text-center">
            <p className="text-sm text-white/40">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-medium text-brand-400 hover:text-brand-300 transition-colors"
              >
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
