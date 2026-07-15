"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import Button from "@/components/ui/Button";

type DropItem = { label: string; href: string; soon?: boolean };

const SUBJECT_ITEMS: DropItem[] = [
  { label: "Math", href: "/math" },
  { label: "Science", href: "/science" },
];

function SoonChip({ onDark = false }: { onDark?: boolean }) {
  return (
    <span
      className={`rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
        onDark ? "bg-white/10 text-white/70" : "bg-pnp-gray-100 text-pnp-gray-600"
      }`}
    >
      Soon
    </span>
  );
}

function DropdownMenu({ label, items }: { label: string; items: DropItem[] }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="flex items-center gap-1.5 rounded-lg px-4 py-2 text-base font-semibold text-white/80 transition-colors hover:bg-white/10 hover:text-white"
      >
        {label}
        <svg
          width="12"
          height="8"
          viewBox="0 0 12 8"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        >
          <path d="M1 1.5l5 5 5-5" />
        </svg>
      </button>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 min-w-[220px] overflow-hidden rounded-lg bg-white py-2 shadow-xl">
          {items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setOpen(false)}
              className="flex items-center justify-between gap-2 px-5 py-3 text-base font-medium text-pnp-navy transition-colors hover:bg-pnp-gray-50"
            >
              {item.label}
              {item.soon && <SoonChip />}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-pnp-navy">
      <div className="mx-auto flex max-w-[1296px] items-center justify-between px-4 py-3 md:px-6">
        {/* Logo — enlarged for presence in the sticky header. */}
        <Link href="/" className="flex-shrink-0" aria-label="Plug N Play home">
          <Image
            src="/logo.png"
            alt="Plug N Play"
            width={400}
            height={100}
            preload
            className="h-16 w-auto md:h-20"
          />
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-1 md:flex">
          <DropdownMenu label="Subjects" items={SUBJECT_ITEMS} />
          <Link
            href="/library"
            className="rounded-lg px-4 py-2 text-base font-semibold text-white/80 transition-colors hover:bg-white/10 hover:text-white"
          >
            Strategies
          </Link>
          <Link
            href="/classes"
            className="rounded-lg px-4 py-2 text-base font-semibold text-white/80 transition-colors hover:bg-white/10 hover:text-white"
          >
            Classes
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          {/* CTA routes through the shared Button. Label kept distinct from
              "Strategies" (/library) so the two destinations read clearly. */}
          <div className="hidden md:block">
            <Button href="/math/units" tier="primary" size="small">
              Browse units
            </Button>
          </div>

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="flex h-10 w-10 items-center justify-center rounded-lg text-white md:hidden"
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            ) : (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M3 12h18M3 6h18M3 18h18" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile nav */}
      {mobileOpen && (
        <nav className="border-t border-white/10 px-4 pb-4 md:hidden">
          <p className="px-4 py-2 text-xs font-bold uppercase tracking-widest text-white/50">
            Subjects
          </p>
          {SUBJECT_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className="flex items-center justify-between rounded-lg px-6 py-3 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white"
            >
              {item.label}
              {item.soon && <SoonChip onDark />}
            </Link>
          ))}
          <Link
            href="/library"
            onClick={() => setMobileOpen(false)}
            className="block rounded-lg px-6 py-3 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white"
          >
            Strategies
          </Link>
          <Link
            href="/classes"
            onClick={() => setMobileOpen(false)}
            className="block rounded-lg px-6 py-3 text-sm font-medium text-white/80 transition-colors hover:bg-white/10 hover:text-white"
          >
            Classes
          </Link>
          <div className="mt-3 px-2">
            <Button
              href="/math/units"
              tier="primary"
              fullWidth
              onClick={() => setMobileOpen(false)}
            >
              Browse units
            </Button>
          </div>
        </nav>
      )}
    </header>
  );
}
