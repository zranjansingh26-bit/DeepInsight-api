"use client";

import * as React from "react";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { nav, site } from "@/lib/site";
import { cn } from "@/lib/utils";

export function Nav() {
  const [open, setOpen] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);
  const [activeSection, setActiveSection] = React.useState("home");

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  React.useEffect(() => {
    const handleScroll = () => {
      const sections = ["features", "how-it-works", "testimonials", "pricing"];
      const scrollPosition = window.scrollY + 120;

      if (window.scrollY < 100) {
        setActiveSection("home");
        return;
      }

      let currentActive = "home";
      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            currentActive = section;
            break;
          }
        }
      }
      setActiveSection(currentActive);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    setOpen(false);
    if (href.startsWith("#")) {
      e.preventDefault();
      const targetId = href.slice(1);

      if (!targetId) {
        window.scrollTo({
          top: 0,
          behavior: "smooth"
        });
        setActiveSection("home");
        return;
      }

      const element = document.getElementById(targetId);
      if (element) {
        const offset = 80;
        const elementPosition = element.getBoundingClientRect().top + window.scrollY;
        const offsetPosition = elementPosition - offset;

        window.scrollTo({
          top: offsetPosition,
          behavior: "smooth"
        });
        setActiveSection(targetId);
      }
    }
  };

  return (
    <header className="absolute inset-x-0 top-6 z-50 px-4 sm:top-10">
      <div
        className={cn(
          "mx-auto flex max-w-5xl items-center justify-between gap-3 rounded-[32px] px-6 py-3 transition-all duration-500",
          scrolled
            ? "border border-white/10 bg-navy-950/80 shadow-soft backdrop-blur-xl"
            : "border border-white/10 bg-white/5 shadow-[0_8px_40px_-12px_rgba(0,0,0,0.4)] backdrop-blur-md"
        )}
      >
        {/* Logo */}
        <a href="#" onClick={(e) => handleLinkClick(e, "#")} className="inline-flex items-center gap-2">
          <span className="font-display text-lg font-medium tracking-tight text-white sm:text-xl">
            {site.name}
          </span>
        </a>

        {/* Desktop nav links */}
        <nav className="hidden items-center lg:flex lg:gap-4 xl:gap-6">
          {nav.map((link) => {
            const isHome = link.href === "#";
            const isActive = isHome ? activeSection === "home" : activeSection === link.href.slice(1);
            return (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleLinkClick(e, link.href)}
                className={cn(
                  "text-sm transition-all px-3 py-1.5 rounded-full",
                  isActive
                    ? "text-white bg-white/10 font-semibold shadow-inner"
                    : "text-white/70 font-normal hover:text-white"
                )}
              >
                {link.label}
              </a>
            );
          })}
        </nav>

        {/* CTA */}
        <div className="flex items-center gap-2">
          <a href="/login" className="hidden sm:inline-flex text-sm font-medium text-white/80 hover:text-white px-4 py-2 transition-colors">
            Sign In
          </a>
          <Button size="sm" className="hidden sm:inline-flex px-6 rounded-full bg-brand-500 text-white font-medium hover:bg-brand-400 border border-brand-400/50 shadow-[0_0_15px_rgba(99,102,241,0.5)]" asChild>
            <a href="/signup">Try Now</a>
          </Button>
          <button
            aria-label="Toggle menu"
            className="grid h-9 w-9 place-items-center rounded-full border border-white/15 bg-white/5 text-white hover:bg-white/10 lg:hidden"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="mx-auto mt-2 max-w-4xl overflow-hidden rounded-3xl border border-white/10 bg-navy-900/95 shadow-lift backdrop-blur lg:hidden">
          <div className="flex flex-col gap-1 p-3">
            {nav.map((link) => {
              const isHome = link.href === "#";
              const isActive = isHome ? activeSection === "home" : activeSection === link.href.slice(1);
              return (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={(e) => handleLinkClick(e, link.href)}
                  className={cn(
                    "rounded-xl px-4 py-3 text-base font-medium transition-colors",
                    isActive
                      ? "bg-brand-500/20 text-brand-300 font-semibold"
                      : "text-white/80 hover:bg-white/5 hover:text-white"
                  )}
                >
                  {link.label}
                </a>
              );
            })}
            <Button asChild className="mt-2 w-full justify-center bg-brand-500 hover:bg-brand-400 border border-brand-400/50">
              <a href="/signup" onClick={() => setOpen(false)}>
                Try Now
              </a>
            </Button>
            <a href="/login" onClick={() => setOpen(false)} className="mt-2 w-full text-center py-2.5 rounded-xl border border-white/10 text-white hover:bg-white/5 transition-colors block text-sm font-medium">
              Sign In
            </a>
          </div>
        </div>
      )}
    </header>
  );
}
