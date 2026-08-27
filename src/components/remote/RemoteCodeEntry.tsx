"use client";

import { useEffect, useRef, useState } from "react";
import {
  ROOM_CODE_ALPHABET,
  ROOM_CODE_LENGTH,
  normaliseRoomCode,
} from "@/lib/classroom/remote-codes";

/**
 * Four-character code entry. Single big input that accepts only valid
 * alphabet chars (uppercased automatically) and auto-submits when the
 * user reaches the full length.
 *
 * Keeping it as a single input (rather than 4 split boxes) avoids fiddly
 * focus-management on mobile keyboards and lets paste-and-go work cleanly
 * from QR-shared text messages.
 */
interface Props {
  initialCode: string;
  connecting: boolean;
  error?: string;
  onSubmit: (code: string) => void;
}

export default function RemoteCodeEntry({
  initialCode,
  connecting,
  error,
  onSubmit,
}: Props) {
  const [code, setCode] = useState(initialCode);
  const inputRef = useRef<HTMLInputElement | null>(null);

  // Autofocus on mount so the keyboard pops on phones.
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Auto-submit when full length is reached. Skips while we're already
  // connecting so a rapid second submit doesn't fire.
  useEffect(() => {
    if (connecting) return;
    if (code.length === ROOM_CODE_LENGTH) onSubmit(code);
    // We deliberately omit onSubmit from deps to dodge re-fires when the
    // parent recreates the callback — `code` length is the only signal
    // that should drive an auto-submit.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [code, connecting]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-pnp-gray-50 px-6 text-pnp-gray-900">
      <div className="w-full max-w-sm rounded-2xl bg-white p-7 shadow-md">
        <h1 className="font-heading text-2xl font-extrabold text-pnp-navy">
          Pair your phone
        </h1>
        <p className="mt-1 text-sm text-pnp-gray-500">
          Enter the 4-character code shown on the projection.
        </p>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!connecting) onSubmit(code);
          }}
          className="mt-5"
        >
          <input
            ref={inputRef}
            type="text"
            inputMode="text"
            autoCapitalize="characters"
            autoCorrect="off"
            spellCheck={false}
            value={code}
            onChange={(e) => setCode(normaliseRoomCode(e.target.value))}
            maxLength={ROOM_CODE_LENGTH}
            placeholder="????"
            aria-label="Room code"
            className="w-full rounded-xl border-2 border-pnp-gray-200 bg-pnp-gray-50 px-4 py-4 text-center font-mono text-5xl font-extrabold tracking-[0.35em] tabular-nums focus:border-pnp-blue focus:outline-none"
          />
          <div className="mt-1 text-center text-xs text-pnp-gray-500">
            Letters and numbers only — no <span className="font-mono">I O 0 1</span>.
          </div>

          {error && (
            <p className="mt-3 rounded-md bg-pnp-red/10 px-3 py-2 text-center text-sm text-pnp-red">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={connecting || code.length !== ROOM_CODE_LENGTH}
            className={`mt-5 w-full rounded-xl py-3 text-lg font-bold shadow-sm transition-colors ${
              connecting || code.length !== ROOM_CODE_LENGTH
                ? "cursor-not-allowed bg-pnp-gray-200 text-pnp-gray-500"
                : "bg-pnp-blue text-white hover:bg-pnp-navy"
            }`}
          >
            {connecting ? "Connecting…" : "Pair"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-pnp-gray-500">
          Tip: the QR code on the projection deep-links straight here.
        </p>
        {/* Single-source-of-truth hint about the alphabet so accidental
            paste of "IO0l" gets a friendly reason it's empty. */}
        <p className="sr-only">
          Allowed characters: {ROOM_CODE_ALPHABET}.
        </p>
      </div>
    </div>
  );
}
