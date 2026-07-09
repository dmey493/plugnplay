"use client";

import { useState } from "react";
import { useUser } from "@/lib/use-user";

/**
 * Header chip showing the fake-logged-in user.
 *
 * Three states:
 *   - hydrating (user === undefined): renders nothing so SSR + CSR markup
 *     match. Once the effect fires we know which state we're in.
 *   - logged out (user === null): shows a small "Sign in" button that
 *     opens the name-prompt modal.
 *   - logged in (user.name set): shows the name + a tiny menu (change
 *     name, sign out).
 *
 * No real auth — this is a name kept in localStorage. The whole chip
 * will swap out for a proper session reader when Supabase / NextAuth
 * lands. The component intentionally stays tiny so swapping it doesn't
 * ripple anywhere else.
 */
export default function UserChip() {
  const { user, login, logout } = useUser();
  const [open, setOpen] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [draft, setDraft] = useState("");

  if (user === undefined) return null;

  if (user === null) {
    return (
      <>
        <button
          type="button"
          onClick={() => setRenaming(true)}
          className="rounded-md border border-white/20 px-3 py-1.5 text-xs font-semibold text-white/80 transition-colors hover:bg-white/10 hover:text-white"
          title="Sign in (fake — no password)"
        >
          Sign in
        </button>
        {renaming && (
          <NamePrompt
            initial=""
            title="What name should classes save under?"
            blurb="There's no real login yet — this just labels your saved classes so they survive a refresh. We'll swap this for a real account when auth lands."
            onCancel={() => setRenaming(false)}
            onConfirm={(name) => {
              login(name);
              setRenaming(false);
            }}
          />
        )}
      </>
    );
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-md border border-white/20 px-3 py-1.5 text-xs font-semibold text-white/80 transition-colors hover:bg-white/10 hover:text-white"
        title="Signed in (fake — saved locally)"
      >
        <span
          aria-hidden="true"
          className="flex h-5 w-5 items-center justify-center rounded-full bg-pnp-accent text-[0.65rem] font-bold text-white"
        >
          {user.name.charAt(0).toUpperCase() || "?"}
        </span>
        <span className="hidden sm:inline">{user.name}</span>
        <svg
          width="10" height="10" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-[60]" onClick={() => setOpen(false)} aria-hidden="true" />
          <div
            role="menu"
            className="absolute right-0 top-full z-[70] mt-2 w-48 rounded-md border border-pnp-gray-200 bg-white py-1 text-sm shadow-lg"
          >
            <button
              role="menuitem"
              type="button"
              onClick={() => {
                setDraft(user.name);
                setRenaming(true);
                setOpen(false);
              }}
              className="block w-full px-3 py-2 text-left text-pnp-gray-700 hover:bg-pnp-gray-50"
            >
              Change name
            </button>
            <button
              role="menuitem"
              type="button"
              onClick={() => {
                logout();
                setOpen(false);
              }}
              className="block w-full px-3 py-2 text-left text-pnp-gray-700 hover:bg-pnp-gray-50"
            >
              Sign out
            </button>
          </div>
        </>
      )}

      {renaming && (
        <NamePrompt
          initial={draft || user.name}
          title="Change your display name"
          blurb="Just updates the label on your saved classes."
          onCancel={() => setRenaming(false)}
          onConfirm={(name) => {
            login(name);
            setRenaming(false);
          }}
        />
      )}
    </div>
  );
}

function NamePrompt({
  initial,
  title,
  blurb,
  onCancel,
  onConfirm,
}: {
  initial: string;
  title: string;
  blurb: string;
  onCancel: () => void;
  onConfirm: (name: string) => void;
}) {
  const [value, setValue] = useState(initial);
  const trimmed = value.trim();

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="user-chip-prompt-title"
      className="fixed inset-0 z-[80] flex items-center justify-center bg-pnp-navy/40 p-4"
      onClick={onCancel}
    >
      <div
        className="w-full max-w-sm rounded-lg bg-white p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="user-chip-prompt-title" className="font-heading text-lg font-bold text-pnp-navy">
          {title}
        </h2>
        <p className="mt-1 text-sm text-pnp-gray-600">{blurb}</p>
        <form
          className="mt-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (!trimmed) return;
            onConfirm(trimmed);
          }}
        >
          <label className="block">
            <span className="sr-only">Your name</span>
            <input
              type="text"
              autoFocus
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="e.g. Ms. Rivera"
              className="w-full rounded-md border border-pnp-gray-300 bg-white px-3 py-2 text-sm text-pnp-navy outline-none transition-colors placeholder:text-pnp-gray-500 focus:border-pnp-accent focus:ring-2 focus:ring-pnp-accent/30"
            />
          </label>
          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onCancel}
              className="rounded-md border border-pnp-gray-300 bg-white px-3 py-1.5 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!trimmed}
              className="rounded-md bg-pnp-accent px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-pnp-accent-hover disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
