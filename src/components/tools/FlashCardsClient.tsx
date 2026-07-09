"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import Button from "@/components/ui/Button";
import { ArrowRightIcon } from "@/components/ui/icons";

/**
 * Voice-powered math fact flash cards.
 *
 * Flow:
 *   1. Configure: pick operation (+ − × ÷), max operand, and card count.
 *   2. Practice: each card shows "a op b = ?" — tap the mic (or auto-listen),
 *      speak the answer, and the app parses the spoken words into a number
 *      and compares to the expected answer.
 *   3. Summary: shows score and lets you redo or change settings.
 *
 * Speech recognition uses the browser-native Web Speech API
 * (`SpeechRecognition` / `webkitSpeechRecognition`), so it works on
 * Chromebooks in Chrome/Edge with no API key or external service. Firefox
 * doesn't support it well; we degrade to a typed-answer fallback.
 */

type Operation = "+" | "-" | "*" | "/";

interface FlashCard {
  a: number;
  b: number;
  op: Operation;
  answer: number;
}

/** A card the student got wrong, with what they said/typed. Shown on the
 *  summary screen so feedback happens once at the end (the user's request),
 *  not per-card. */
interface MissedEntry {
  card: FlashCard;
  said: string;
  parsedAs: number | null;
}

interface Options {
  operation: Operation | "mixed";
  maxOperand: number;
  cardCount: number;
}

// Minimal type for the browser Speech Recognition API. The DOM types ship
// the prefixed `webkitSpeechRecognition` only via lib.dom.d.ts in newer
// TypeScript releases; we declare just what we touch to stay portable.
//
// `resultIndex` is the spec-defined index of the FIRST result that changed
// in this event — critical for continuous mode, where `results` keeps every
// historical utterance from the start of the session.
interface SpeechRecognitionResultListLike {
  length: number;
  [i: number]: { isFinal: boolean; 0: { transcript: string } };
}
interface SpeechRecognitionResultEventLike {
  resultIndex: number;
  results: SpeechRecognitionResultListLike;
}
interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((e: SpeechRecognitionResultEventLike) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

const OP_SYMBOL: Record<Operation, string> = {
  "+": "+",
  "-": "−",
  "*": "×",
  "/": "÷",
};

const OP_LABEL: Record<Operation, string> = {
  "+": "Addition",
  "-": "Subtraction",
  "*": "Multiplication",
  "/": "Division",
};

export default function FlashCardsClient() {
  const [mode, setMode] = useState<"config" | "practice" | "done">("config");
  const [options, setOptions] = useState<Options>({
    operation: "+",
    maxOperand: 12,
    cardCount: 10,
  });
  const [cards, setCards] = useState<FlashCard[]>([]);
  const [index, setIndex] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [missed, setMissed] = useState<MissedEntry[]>([]);

  // Speech state — owned at the top level so we can wipe it between cards.
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState(""); // live in-progress transcript
  const [speechError, setSpeechError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  // Refs that mirror the latest card we're listening for. The recognition
  // handler binds once and reads these via .current so it never goes stale
  // across card advances — no need to tear down + restart per card.
  const indexRef = useRef(0);
  const answerRef = useRef<number | null>(null);
  const cardRef = useRef<FlashCard | null>(null);
  const modeRef = useRef<"config" | "practice" | "done">("config");
  // Tells onend whether to auto-restart (true while practice is live) or to
  // let the session end (false when we leave practice mode or the page).
  const keepListeningRef = useRef(false);
  // Highest result index we've already scored. In continuous mode the event's
  // `results` collection keeps every utterance since the session started, so
  // without this guard a "five" said on card 1 would be re-judged against
  // every later card. We bump this whenever we accept a final result, and
  // reset it back to -1 whenever a new session starts.
  const processedFinalIndexRef = useRef(-1);

  // Session timer — for the "race the clock" challenge angle. Both refs are
  // wall-clock ms (Date.now()). `now` is a ticking state value that re-renders
  // the elapsed display while practicing; it freezes the moment we set
  // sessionEndRef in scoreAndAdvance's last-card path.
  const sessionStartRef = useRef<number | null>(null);
  const sessionEndRef = useRef<number | null>(null);
  const [now, setNow] = useState(0);

  // Feature detection runs once. `null` while we're still checking.
  const speechSupported = useMemo(() => {
    if (typeof window === "undefined") return null;
    const w = window as typeof window & {
      SpeechRecognition?: new () => SpeechRecognitionLike;
      webkitSpeechRecognition?: new () => SpeechRecognitionLike;
    };
    return Boolean(w.SpeechRecognition || w.webkitSpeechRecognition);
  }, []);

  // ───── Card generation ─────
  const startSession = useCallback(() => {
    const next = generateCards(options);
    setCards(next);
    setIndex(0);
    setCorrect(0);
    setMissed([]);
    setInterim("");
    setSpeechError(null);
    // Fresh session — reset the dedup cursor so we start from scratch.
    processedFinalIndexRef.current = -1;
    // Stamp the session clock. Render uses (sessionEndRef ?? now) - start.
    const t = Date.now();
    sessionStartRef.current = t;
    sessionEndRef.current = null;
    setNow(t);
    setMode("practice");
  }, [options]);

  // ───── Speech recognition (continuous, always-on while practicing) ─────
  //
  // We run a single SpeechRecognition session for the whole practice mode.
  // continuous=true keeps the mic open across utterances; interimResults=true
  // lets us show partial transcripts live for snappy visual feedback. The
  // browser still chunks user speech into final results — we only ACT on
  // final results so we don't mis-judge a half-spoken number.
  //
  // The session persists across card advances. The result handler reads the
  // current card/answer from refs (kept in sync via the effect below) so it
  // never goes stale. If the browser auto-stops the session (some Chrome
  // versions do after ~60s of silence), onend re-starts it as long as we
  // still want to listen.
  // Shared score+advance helper. Called from the interim path, the final
  // path, and the typed-input path. Captures sessionEndRef the moment we
  // run out of cards so the on-screen timer freezes.
  const scoreAndAdvance = useCallback(
    (card: FlashCard, said: string, parsedAs: number) => {
      if (parsedAs === card.answer) {
        setCorrect((c) => c + 1);
      } else {
        setMissed((m) => [...m, { card, said, parsedAs }]);
      }
      setInterim("");
      setIndex((idx) => {
        if (idx + 1 >= cards.length) {
          sessionEndRef.current = Date.now();
          setMode("done");
          return idx;
        }
        return idx + 1;
      });
    },
    [cards.length]
  );

  const stopListening = useCallback(() => {
    keepListeningRef.current = false;
    const r = recognitionRef.current;
    if (r) {
      try { r.abort(); } catch { /* noop */ }
    }
    recognitionRef.current = null;
    setListening(false);
  }, []);

  const startContinuousListening = useCallback(() => {
    if (!speechSupported) return;
    // Don't double-start — if a session is already live, leave it alone.
    if (recognitionRef.current) return;
    const w = window as typeof window & {
      SpeechRecognition?: new () => SpeechRecognitionLike;
      webkitSpeechRecognition?: new () => SpeechRecognitionLike;
    };
    const Ctor = w.SpeechRecognition ?? w.webkitSpeechRecognition;
    if (!Ctor) return;
    const r = new Ctor();
    r.lang = "en-US";
    r.continuous = true;
    r.interimResults = true;
    r.maxAlternatives = 1;
    r.onresult = (e) => {
      // In continuous mode the event's `results` collection keeps EVERY
      // utterance since the session started. We must only look at entries
      // that are new in this event AND that we haven't already scored.
      const results = e.results;
      const start = Math.max(
        e.resultIndex ?? 0,
        processedFinalIndexRef.current + 1
      );
      let lastInterim = "";
      for (let i = start; i < results.length; i++) {
        const r0 = results[i];
        const text = r0[0].transcript;
        const card = cardRef.current;
        if (!card) continue;

        // ───── Interim path (the speed boost) ─────
        // Browsers fire interim results as the speech is still being
        // recognised, ~200-400ms BEFORE the final result lands (end-of-
        // utterance silence detection). We can shortcut that delay for
        // CORRECT answers: if the interim already parses to the expected
        // answer, advance now. We deliberately do NOT accept wrong answers
        // from interim because the engine might still be mid-revision
        // ("twenty" en route to "twenty five") — waiting for the final
        // there avoids false-wrong commits.
        if (!r0.isFinal) {
          lastInterim = text;
          const interimGuess = parseSpokenNumber(text);
          if (interimGuess !== null && interimGuess === card.answer) {
            // Consume this entry early. The eventual final for the same
            // index will be filtered out by processedFinalIndexRef.
            processedFinalIndexRef.current = i;
            scoreAndAdvance(card, text, interimGuess);
            return;
          }
          continue;
        }

        // ───── Final path ─────
        processedFinalIndexRef.current = i;
        const guess = parseSpokenNumber(text);
        if (guess === null) {
          // Unparseable utterance — keep listening, don't advance. The
          // student can re-speak the answer; we don't punish noise.
          continue;
        }
        scoreAndAdvance(card, text, guess);
        // Only one advance per event so a fast utterance double can't
        // race two cards in one tick.
        return;
      }
      setInterim(lastInterim);
    };
    r.onerror = (e) => {
      if (e.error === "not-allowed" || e.error === "service-not-allowed") {
        setSpeechError("Microphone access denied. Enable mic permission and reload.");
        keepListeningRef.current = false;
      } else if (e.error === "no-speech" || e.error === "aborted") {
        // Normal — onend will restart if we still want to listen.
      } else {
        // Network errors, etc — log and rely on onend's restart attempt.
        // (Don't bubble these as user-visible errors; they'd flash and clear.)
        // eslint-disable-next-line no-console
        console.warn("SpeechRecognition error:", e.error);
      }
    };
    r.onend = () => {
      recognitionRef.current = null;
      // If we still want to listen (practice mode is active) and the page is
      // visible, immediately re-start. A short timeout dodges a Chrome quirk
      // where calling start() inside onend can throw "InvalidStateError".
      if (keepListeningRef.current && modeRef.current === "practice") {
        setTimeout(() => {
          if (keepListeningRef.current && modeRef.current === "practice") {
            startContinuousListening();
          }
        }, 50);
      } else {
        setListening(false);
        setInterim("");
      }
    };
    recognitionRef.current = r;
    keepListeningRef.current = true;
    // Each fresh SpeechRecognition instance gets its own `results` array that
    // starts at index 0, so reset the processed-index here too (watchdog
    // restarts after onend hit this path otherwise stale).
    processedFinalIndexRef.current = -1;
    setListening(true);
    try {
      r.start();
    } catch {
      // start() can throw if called twice quickly — onend will re-arm.
    }
  }, [speechSupported, scoreAndAdvance]);

  // Skip-button advance. Counts as a "missed" entry with no spoken answer
  // so the student can see what they skipped on the summary.
  const advance = useCallback(() => {
    setInterim("");
    setSpeechError(null);
    const card = cardRef.current;
    if (card) {
      setMissed((m) => [...m, { card, said: "(skipped)", parsedAs: null }]);
    }
    setIndex((i) => {
      if (i + 1 >= cards.length) {
        sessionEndRef.current = Date.now();
        setMode("done");
        return i;
      }
      return i + 1;
    });
  }, [cards.length]);

  // Manual typed-answer fallback (also used if voice isn't supported).
  // Routes through scoreAndAdvance so timer & summary behavior match the
  // voice path exactly.
  const submitTyped = useCallback(
    (raw: string) => {
      const card = cards[index];
      if (!card) return;
      const guess = Number.parseFloat(raw.trim());
      if (Number.isNaN(guess)) {
        setSpeechError(`"${raw}" isn't a number.`);
        return;
      }
      scoreAndAdvance(card, raw.trim(), guess);
    },
    [cards, index, scoreAndAdvance]
  );

  // Keep refs in sync with the latest state so the continuous-listening
  // handler always reads the active card without re-binding.
  useEffect(() => { indexRef.current = index; }, [index]);
  useEffect(() => {
    const card = cards[index] ?? null;
    cardRef.current = card;
    answerRef.current = card?.answer ?? null;
  }, [cards, index]);
  useEffect(() => { modeRef.current = mode; }, [mode]);

  // Auto-start the continuous session when entering practice mode, and tear
  // it down when leaving (to "done" or back to config). One session covers
  // every card, so there's no per-card mic restart.
  useEffect(() => {
    if (mode !== "practice") return;
    if (!speechSupported) return;
    startContinuousListening();
    return () => {
      stopListening();
    };
  }, [mode, speechSupported, startContinuousListening, stopListening]);

  // Tick the session clock. 200ms is fast enough that the displayed seconds
  // never look out of date and slow enough to stay cheap on re-renders. Only
  // runs while practicing — the moment we hit "done", scoreAndAdvance has
  // already pinned sessionEndRef, so the displayed value freezes.
  useEffect(() => {
    if (mode !== "practice") return;
    const id = setInterval(() => setNow(Date.now()), 200);
    return () => clearInterval(id);
  }, [mode]);

  // Wall-clock elapsed since startSession. Uses the frozen end time when
  // sessionEndRef has been set (last card just resolved), otherwise tracks
  // `now` which the tick effect above keeps fresh.
  const elapsedMs =
    sessionStartRef.current === null
      ? 0
      : (sessionEndRef.current ?? now) - sessionStartRef.current;

  // Keyboard: → to skip (Space is no longer needed — listening is always on).
  useEffect(() => {
    if (mode !== "practice") return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") {
        e.preventDefault();
        advance();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [mode, advance]);

  // Tear down recognition on unmount so we don't leak the mic.
  useEffect(() => {
    return () => {
      stopListening();
    };
  }, [stopListening]);

  // ───────── Render ─────────
  return (
    <div className="flex min-h-screen flex-col bg-pnp-gray-50 text-pnp-gray-900">
      <div className="flex shrink-0 items-center justify-between border-b border-pnp-gray-200 bg-white px-4 py-3">
        <Link
          href="/math"
          className="inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-sm font-semibold text-pnp-gray-700 transition-colors hover:bg-pnp-gray-100"
        >
          <svg
            width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to Math
        </Link>
        <h1 className="font-heading text-lg font-bold text-pnp-navy">Flash Cards</h1>
        {mode === "practice" ? (
          <div className="flex items-center gap-4 font-mono text-sm">
            <span className="tabular-nums text-pnp-blue">
              {formatElapsed(elapsedMs)}
            </span>
            <span className="text-pnp-gray-500">
              {index + 1} / {cards.length}
            </span>
          </div>
        ) : (
          <span className="w-24" />
        )}
      </div>

      <main className="flex flex-1 flex-col items-center justify-center px-6 py-10">
        {mode === "config" && (
          <ConfigPanel
            options={options}
            setOptions={setOptions}
            speechSupported={speechSupported}
            onStart={startSession}
          />
        )}

        {mode === "practice" && cards.length > 0 && (
          <PracticeCard
            card={cards[index]}
            interim={interim}
            listening={listening}
            speechSupported={speechSupported}
            speechError={speechError}
            onSubmitTyped={submitTyped}
            onSkip={advance}
          />
        )}

        {mode === "done" && (
          <SummaryPanel
            total={cards.length}
            correct={correct}
            missed={missed}
            elapsedMs={elapsedMs}
            onRedo={() => {
              setMode("config");
              setCards([]);
              setIndex(0);
            }}
            onAgain={startSession}
          />
        )}
      </main>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Config panel
// ─────────────────────────────────────────────────────────────────────

function ConfigPanel({
  options,
  setOptions,
  speechSupported,
  onStart,
}: {
  options: Options;
  setOptions: (o: Options) => void;
  speechSupported: boolean | null;
  onStart: () => void;
}) {
  return (
    <div className="w-full max-w-xl rounded-2xl bg-white p-8 shadow-md">
      <h2 className="font-heading text-2xl font-extrabold text-pnp-navy">
        Set up your practice
      </h2>
      <p className="mt-1 text-sm text-pnp-gray-500">
        Pick the operation, the maximum operand, and how many cards. Speak the answer or type it.
      </p>

      <section className="mt-6">
        <Label>Operation</Label>
        <div className="mt-2 grid grid-cols-5 gap-2">
          {(["+", "-", "*", "/", "mixed"] as const).map((op) => (
            <button
              key={op}
              type="button"
              onClick={() => setOptions({ ...options, operation: op })}
              className={`rounded-lg border px-3 py-2 text-base font-bold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                options.operation === op
                  ? "border-pnp-accent bg-pnp-accent text-white"
                  : "border-pnp-gray-300 bg-white text-pnp-gray-700 hover:bg-pnp-gray-50"
              }`}
            >
              {op === "mixed" ? "Mixed" : OP_SYMBOL[op]}
            </button>
          ))}
        </div>
      </section>

      <section className="mt-6">
        <Label>Largest operand (1 – 20)</Label>
        <div className="mt-2 flex items-center gap-4">
          <input
            type="range"
            min={1}
            max={20}
            value={options.maxOperand}
            onChange={(e) => setOptions({ ...options, maxOperand: Number(e.target.value) })}
            className="flex-1 accent-pnp-accent"
          />
          <span className="w-12 text-center font-mono text-lg font-bold">
            {options.maxOperand}
          </span>
        </div>
      </section>

      <section className="mt-6">
        <Label>How many cards</Label>
        <div className="mt-2 grid grid-cols-5 gap-2">
          {[5, 10, 15, 20, 30].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setOptions({ ...options, cardCount: n })}
              className={`rounded-lg border px-3 py-2 text-base font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pnp-accent focus-visible:ring-offset-2 ${
                options.cardCount === n
                  ? "border-pnp-accent bg-pnp-accent text-white"
                  : "border-pnp-gray-300 bg-white text-pnp-gray-700 hover:bg-pnp-gray-50"
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      </section>

      {speechSupported === false && (
        <p className="mt-5 rounded-md bg-pnp-yellow/30 px-3 py-2 text-sm text-pnp-gray-700">
          Voice input isn&apos;t available in this browser. You&apos;ll type answers instead. Chrome or Edge is recommended for the speaking mode.
        </p>
      )}

      <div className="mt-8">
        <Button tier="primary" fullWidth onClick={onStart}>
          Start practice
        </Button>
      </div>
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
      {children}
    </div>
  );
}

/**
 * Format a millisecond duration as the shortest reasonable display:
 *   – under one minute: `12.3s`
 *   – one minute or more: `1:23.4`
 * Tenths-of-seconds precision so the ticking display feels alive without
 * jittering wildly.
 */
function formatElapsed(ms: number): string {
  if (!isFinite(ms) || ms <= 0) return "0.0s";
  const totalSecs = ms / 1000;
  if (totalSecs < 60) return `${totalSecs.toFixed(1)}s`;
  const mins = Math.floor(totalSecs / 60);
  const secs = totalSecs - mins * 60;
  return `${mins}:${secs.toFixed(1).padStart(4, "0")}`;
}

// ─────────────────────────────────────────────────────────────────────
// Practice card
// ─────────────────────────────────────────────────────────────────────

function PracticeCard({
  card,
  interim,
  listening,
  speechSupported,
  speechError,
  onSubmitTyped,
  onSkip,
}: {
  card: FlashCard;
  interim: string;
  listening: boolean;
  speechSupported: boolean | null;
  speechError: string | null;
  onSubmitTyped: (raw: string) => void;
  onSkip: () => void;
}) {
  const [typed, setTyped] = useState("");
  useEffect(() => setTyped(""), [card]);

  return (
    <div className="flex w-full max-w-2xl flex-col items-center">
      {/* The card itself. No per-card reveal — we just show the problem and
          move on the moment the answer is parsed (right or wrong). Summary
          screen handles all feedback at the end. */}
      <div className="relative w-full rounded-3xl bg-white px-10 py-14 shadow-lg ring-1 ring-pnp-gray-200">
        <div className="flex items-center justify-center gap-6 font-heading text-7xl font-extrabold tabular-nums text-pnp-navy md:text-8xl">
          <span>{card.a}</span>
          <span className="text-pnp-gray-500">{OP_SYMBOL[card.op]}</span>
          <span>{card.b}</span>
          <span className="text-pnp-gray-500">=</span>
          <span className="min-w-[2ch] text-center text-pnp-gray-300">?</span>
        </div>
      </div>

      {/* Always-on status row. No mic button — just speak. */}
      <div className="mt-8 flex w-full flex-col items-center gap-3">
        {speechSupported !== false ? (
          <div
            className={`flex items-center gap-3 rounded-full px-5 py-2.5 text-sm font-semibold ${
              listening
                ? "bg-pnp-accent/10 text-pnp-accent"
                : "bg-pnp-gray-100 text-pnp-gray-500"
            }`}
            role="status"
            aria-live="polite"
          >
            <span className="relative inline-flex h-3 w-3">
              {listening && (
                <span className="absolute inset-0 inline-flex h-3 w-3 animate-ping rounded-full bg-pnp-accent opacity-60" />
              )}
              <span
                className={`relative inline-flex h-3 w-3 rounded-full ${
                  listening ? "bg-pnp-accent" : "bg-pnp-gray-400"
                }`}
              />
            </span>
            {listening ? "Listening — just say the answer" : "Mic off"}
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              onSubmitTyped(typed);
            }}
            className="flex w-full max-w-sm gap-2"
          >
            <input
              type="text"
              inputMode="numeric"
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              autoFocus
              className="flex-1 rounded-lg border border-pnp-gray-300 px-4 py-3 text-xl font-bold focus:border-pnp-accent focus:outline-none"
              placeholder="Type the answer"
            />
            <Button type="submit" tier="primary">
              Check
            </Button>
          </form>
        )}

        {/* Live interim transcript — shows partial speech as the browser
            recognises it, so the student can tell the mic is hearing them.
            Cleared on every advance, so it's only visible mid-utterance. */}
        {speechSupported !== false && interim && (
          <div className="text-sm italic text-pnp-gray-500" aria-hidden="true">
            &ldquo;{interim}&rdquo;
          </div>
        )}

        {speechError && (
          <p className="text-sm text-pnp-red">{speechError}</p>
        )}

        <div className="mt-2">
          <Button
            tier="tertiary"
            onClick={onSkip}
            trailingIcon={<ArrowRightIcon size={15} />}
          >
            Skip
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Summary panel
// ─────────────────────────────────────────────────────────────────────

function SummaryPanel({
  total,
  correct,
  missed,
  elapsedMs,
  onRedo,
  onAgain,
}: {
  total: number;
  correct: number;
  missed: MissedEntry[];
  elapsedMs: number;
  onRedo: () => void;
  onAgain: () => void;
}) {
  const pct = total > 0 ? Math.round((correct / total) * 100) : 0;
  // Cards-per-minute pace — the headline "challenge" metric.
  const minutes = elapsedMs / 60000;
  const cpm = minutes > 0 ? Math.round(total / minutes) : 0;
  return (
    <div className="w-full max-w-xl rounded-2xl bg-white p-8 text-center shadow-md">
      <h2 className="font-heading text-2xl font-extrabold text-pnp-navy">All done</h2>
      <div className="mt-4 font-mono text-6xl font-bold tabular-nums text-pnp-navy">
        {correct} / {total}
      </div>
      <div className="text-sm text-pnp-gray-500">{pct}% correct</div>

      <div className="mt-4 flex items-center justify-center gap-6 text-sm">
        <div>
          <div className="font-mono text-2xl font-bold tabular-nums text-pnp-blue">
            {formatElapsed(elapsedMs)}
          </div>
          <div className="text-xs uppercase tracking-wider text-pnp-gray-500">Total time</div>
        </div>
        <div>
          <div className="font-mono text-2xl font-bold tabular-nums text-pnp-blue">
            {cpm}
          </div>
          <div className="text-xs uppercase tracking-wider text-pnp-gray-500">Cards / min</div>
        </div>
      </div>

      {missed.length > 0 && (
        <div className="mt-6 text-left">
          <div className="text-sm font-bold uppercase tracking-wider text-pnp-gray-500">
            Missed
          </div>
          <ul className="mt-2 divide-y divide-pnp-gray-100 rounded-lg border border-pnp-gray-200 bg-pnp-gray-50">
            {missed.map((m, i) => (
              <li key={i} className="flex flex-col gap-1 px-4 py-2 sm:flex-row sm:items-center sm:justify-between">
                <span className="font-mono">
                  {m.card.a} {OP_SYMBOL[m.card.op]} {m.card.b}
                </span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="text-pnp-gray-500">
                    you said{" "}
                    <span className="font-mono italic text-pnp-red">
                      {m.parsedAs !== null ? m.parsedAs : m.said}
                    </span>
                  </span>
                  <span className="text-pnp-gray-300">→</span>
                  <span className="font-mono font-bold text-pnp-green">{m.card.answer}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-8 flex justify-center gap-3">
        <Button tier="secondary" onClick={onRedo}>
          Change settings
        </Button>
        <Button tier="primary" onClick={onAgain}>
          New set
        </Button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// Card generation
// ─────────────────────────────────────────────────────────────────────

function generateCards(opts: Options): FlashCard[] {
  const out: FlashCard[] = [];
  const operations: Operation[] =
    opts.operation === "mixed" ? ["+", "-", "*", "/"] : [opts.operation];
  for (let i = 0; i < opts.cardCount; i++) {
    const op = operations[Math.floor(Math.random() * operations.length)];
    out.push(makeCard(op, opts.maxOperand));
  }
  return out;
}

function makeCard(op: Operation, max: number): FlashCard {
  const rnd = (lo: number, hi: number) =>
    Math.floor(Math.random() * (hi - lo + 1)) + lo;
  let a: number, b: number, answer: number;
  switch (op) {
    case "+":
      a = rnd(0, max);
      b = rnd(0, max);
      answer = a + b;
      break;
    case "-":
      a = rnd(0, max);
      b = rnd(0, a); // keep answer non-negative for basic-facts level
      answer = a - b;
      break;
    case "*":
      a = rnd(0, max);
      b = rnd(0, max);
      answer = a * b;
      break;
    case "/":
      // Build a / b with a clean integer quotient: pick b and quotient first.
      b = rnd(1, Math.max(1, max));
      answer = rnd(0, max);
      a = b * answer;
      break;
  }
  return { a, b, op, answer };
}

// ─────────────────────────────────────────────────────────────────────
// Spoken-number parser
// ─────────────────────────────────────────────────────────────────────
//
// Accepts both digit strings ("12", "-3") and English number words
// ("twelve", "negative three", "twenty-five", "one hundred twenty").
// Returns null if the input doesn't parse to a single number.

const ONES: Record<string, number> = {
  zero: 0, oh: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6,
  seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12,
  thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17,
  eighteen: 18, nineteen: 19,
};

const TENS: Record<string, number> = {
  twenty: 20, thirty: 30, forty: 40, fourty: 40, fifty: 50, sixty: 60,
  seventy: 70, eighty: 80, ninety: 90,
};

export function parseSpokenNumber(input: string): number | null {
  if (!input) return null;
  let text = input.toLowerCase().trim();
  // Normalize: hyphens and "and" are noise, "minus" reads as negative.
  text = text.replace(/-/g, " ").replace(/\band\b/g, " ");

  // Direct digit string first — handles "12", "-3", "144".
  const digitMatch = text.match(/^-?\s*(\d+)\s*$/);
  if (digitMatch) {
    const n = parseInt(digitMatch[1], 10);
    return text.startsWith("-") ? -n : n;
  }

  const negative = /\b(negative|minus)\b/.test(text);
  text = text.replace(/\b(negative|minus)\b/g, "").trim();

  // Empty after stripping → not a number.
  if (!text) return null;

  const words = text.split(/\s+/).filter(Boolean);
  let total = 0;
  let current = 0;
  let touched = false;
  for (const word of words) {
    if (word in ONES) {
      current += ONES[word];
      touched = true;
    } else if (word in TENS) {
      current += TENS[word];
      touched = true;
    } else if (word === "hundred") {
      if (current === 0) current = 1;
      current *= 100;
      touched = true;
    } else if (word === "thousand") {
      if (current === 0) current = 1;
      total += current * 1000;
      current = 0;
      touched = true;
    } else if (/^-?\d+$/.test(word)) {
      // A digit run inside a word stream — accept it as a chunk.
      current += parseInt(word, 10);
      touched = true;
    } else {
      // Unknown word → bail; better to reject than mis-parse.
      return null;
    }
  }
  if (!touched) return null;
  total += current;
  return negative ? -total : total;
}
