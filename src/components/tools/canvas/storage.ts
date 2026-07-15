import type { Camera } from "./useInfiniteCanvas";
import type { Stroke, StrokeKind, Tool } from "./ink";
import type { Kind, Item } from "../manipulatives/types";
import type { BackgroundImage, BoardDocV2, CanvasBackground } from "./types";

/**
 * localStorage persistence for the unified canvas document (v2), plus a
 * one-time migration from the three legacy keys:
 *
 *   pnp-whiteboard-ink        { v: 1, strokes, camera }
 *   pnp-whiteboard-settings   { pages, background }
 *   pnp.manipulatives.board.v1  { version: 1, items, strokes?, camera, savedAt }
 *
 * Migration only runs when the v2 key is absent, and the legacy keys are
 * deleted only after a successful v2 write — imported PDFs can be large, so
 * a quota failure must never destroy the teacher's old board. On a quota
 * failure the save retries without pages so ink and pieces still persist.
 */

const VALID_KINDS: Kind[] = [
  "counter",
  "fraction",
  "algebra",
  "baseten",
  "numberline",
  "colortile",
  "cuisenaire",
  "fractioncircle",
  "patternblock",
  "linkingcube",
  "pvdisk",
  "hundredboard",
  "xyboard",
  "geoboard",
  "clock",
  "rekenrek",
  "bead",
];
const VALID_STROKE_KINDS: StrokeKind[] = ["path", "line", "rect", "ellipse", "text"];
const VALID_BACKGROUNDS: CanvasBackground[] = ["blank", "dots", "grid", "coordinate"];

const LEGACY_WHITEBOARD_INK = "pnp-whiteboard-ink";
const LEGACY_WHITEBOARD_SETTINGS = "pnp-whiteboard-settings";
const LEGACY_MANIPULATIVES = "pnp.manipulatives.board.v1";
// Short-lived per-route v2 keys from when whiteboard and manipulatives were
// separate entry points; folded into the single board doc on first load.
const PRIOR_V2_KEYS = ["pnp.board.v2.whiteboard", "pnp.board.v2.manipulatives"];

export interface BoardStateV2 {
  items: Item[];
  strokes: Stroke[];
  pages: BackgroundImage[];
  background: CanvasBackground;
  gridSnap: boolean;
  camera: Camera | null;
}

const EMPTY: BoardStateV2 = {
  items: [],
  strokes: [],
  pages: [],
  background: "dots",
  gridSnap: true,
  camera: null,
};

function finite(...ns: unknown[]): boolean {
  return ns.every((n) => typeof n === "number" && Number.isFinite(n));
}

/** Defensive per-item validation — drops anything malformed or from a
 *  future/unknown schema rather than letting it crash the board. */
function validItem(raw: unknown): raw is Item {
  if (!raw || typeof raw !== "object") return false;
  const it = raw as Record<string, unknown>;
  if (typeof it.id !== "string") return false;
  if (typeof it.kind !== "string" || !VALID_KINDS.includes(it.kind as Kind)) return false;
  if (!finite(it.x, it.y, it.rot, it.z)) return false;
  return true;
}

function validStroke(raw: unknown): raw is Stroke {
  if (!raw || typeof raw !== "object") return false;
  const s = raw as Record<string, unknown>;
  if (typeof s.id !== "string" || typeof s.points !== "string") return false;
  if (typeof s.color !== "string" || !finite(s.width)) return false;
  if (typeof s.kind !== "string" || !VALID_STROKE_KINDS.includes(s.kind as StrokeKind)) return false;
  return true;
}

function validPage(raw: unknown): raw is BackgroundImage {
  if (!raw || typeof raw !== "object") return false;
  const p = raw as Record<string, unknown>;
  return (
    typeof p.id === "string" &&
    typeof p.href === "string" &&
    finite(p.x, p.y, p.width, p.height)
  );
}

function validCamera(raw: unknown): raw is Camera {
  if (!raw || typeof raw !== "object") return false;
  const c = raw as Record<string, unknown>;
  return finite(c.tx, c.ty, c.zoom);
}

function parseV2(raw: string): BoardStateV2 | null {
  try {
    const doc = JSON.parse(raw) as Partial<BoardDocV2>;
    if (doc.version !== 2) return null;
    return {
      items: Array.isArray(doc.items) ? doc.items.filter(validItem) : [],
      strokes: Array.isArray(doc.strokes) ? doc.strokes.filter(validStroke) : [],
      pages: Array.isArray(doc.pages) ? doc.pages.filter(validPage) : [],
      background: VALID_BACKGROUNDS.includes(doc.background as CanvasBackground)
        ? (doc.background as CanvasBackground)
        : "dots",
      gridSnap: typeof doc.gridSnap === "boolean" ? doc.gridSnap : true,
      camera: validCamera(doc.camera) ? doc.camera : null,
    };
  } catch {
    return null;
  }
}

// ────────── legacy readers ──────────

/** Legacy whiteboard: strokes already use the canonical shape (older saves
 *  may predate `kind`/`tool` — default them to freehand pen paths). */
function readLegacyWhiteboard(): BoardStateV2 | null {
  let found = false;
  const state: BoardStateV2 = { ...EMPTY };
  try {
    const rawInk = window.localStorage.getItem(LEGACY_WHITEBOARD_INK);
    if (rawInk) {
      const saved = JSON.parse(rawInk);
      if (Array.isArray(saved?.strokes)) {
        state.strokes = (saved.strokes as Array<Record<string, unknown>>)
          .map((s) => ({
            opacity: 1,
            tool: "pen" as Tool,
            ...s,
            kind: (s.kind ?? "path") as StrokeKind,
          }))
          .filter(validStroke);
        found = true;
      }
      if (validCamera(saved?.camera)) state.camera = saved.camera;
    }
  } catch {
    /* corrupt ink — skip it, settings may still be fine */
  }
  try {
    const rawSettings = window.localStorage.getItem(LEGACY_WHITEBOARD_SETTINGS);
    if (rawSettings) {
      const s = JSON.parse(rawSettings);
      if (Array.isArray(s?.pages)) {
        state.pages = (s.pages as unknown[]).filter(validPage);
        found = true;
      }
      if (VALID_BACKGROUNDS.includes(s?.background)) {
        state.background = s.background;
        found = true;
      }
    }
  } catch {
    /* corrupt settings — keep whatever the ink key gave us */
  }
  return found ? state : null;
}

/** Legacy manipulatives: items carry over as-is; its simpler ink strokes
 *  ({ pts }) map onto the canonical stroke shape ({ points, kind: "path" }). */
function readLegacyManipulatives(): BoardStateV2 | null {
  try {
    const raw = window.localStorage.getItem(LEGACY_MANIPULATIVES);
    if (!raw) return null;
    const doc = JSON.parse(raw);
    if (doc?.version !== 1 || !Array.isArray(doc.items)) return null;
    const strokes: Stroke[] = (Array.isArray(doc.strokes) ? doc.strokes : [])
      .map((s: Record<string, unknown>) => ({
        id: String(s.id ?? ""),
        kind: "path" as StrokeKind,
        points: String(s.pts ?? ""),
        color: String(s.color ?? "#111827"),
        width: typeof s.width === "number" ? s.width : 3,
        opacity: 1,
        tool: "pen" as Tool,
      }))
      .filter(validStroke);
    return {
      ...EMPTY,
      items: (doc.items as unknown[]).filter(validItem),
      strokes,
      camera: validCamera(doc.camera) ? doc.camera : null,
    };
  } catch {
    return null;
  }
}

function hasContent(s: BoardStateV2): boolean {
  return s.items.length > 0 || s.strokes.length > 0 || s.pages.length > 0;
}

/** Fold several old boards into one. Items/strokes/pages concatenate
 *  (strokes deduped by id); background, snap, and camera come from the
 *  first board in the list that set them — callers order the candidates
 *  by priority. */
function mergeStates(states: BoardStateV2[]): BoardStateV2 {
  const merged: BoardStateV2 = { ...EMPTY, items: [], strokes: [], pages: [] };
  const strokeIds = new Set<string>();
  for (const [i, s] of states.entries()) {
    merged.items.push(...s.items);
    for (const st of s.strokes) {
      if (strokeIds.has(st.id)) continue;
      strokeIds.add(st.id);
      merged.strokes.push(st);
    }
    merged.pages.push(...s.pages);
    if (i === 0) {
      merged.background = s.background;
      merged.gridSnap = s.gridSnap;
    }
    if (!merged.camera && s.camera) merged.camera = s.camera;
  }
  return merged;
}

// ────────── public API ──────────

/** Load the single board doc. When it's absent, migrate by folding in
 *  every earlier board that exists — the short-lived per-route v2 keys and
 *  the original whiteboard / manipulatives keys — then delete those keys
 *  only after the new doc is safely written. */
export function loadBoard(docKey: string): BoardStateV2 {
  if (typeof window === "undefined") return { ...EMPTY };
  try {
    const raw = window.localStorage.getItem(docKey);
    if (raw) {
      const parsed = parseV2(raw);
      if (parsed) return parsed;
    }
  } catch {
    return { ...EMPTY };
  }

  // Gather every prior board, highest priority first.
  const candidates: BoardStateV2[] = [];
  for (const key of PRIOR_V2_KEYS) {
    try {
      const raw = window.localStorage.getItem(key);
      const parsed = raw ? parseV2(raw) : null;
      if (parsed && hasContent(parsed)) candidates.push(parsed);
    } catch {
      /* skip unreadable candidate */
    }
  }
  const wb = readLegacyWhiteboard();
  if (wb && hasContent(wb)) candidates.push(wb);
  const manip = readLegacyManipulatives();
  if (manip && hasContent(manip)) candidates.push(manip);
  if (candidates.length === 0) return { ...EMPTY };

  const merged = mergeStates(candidates);
  if (saveBoard(docKey, merged, Date.now())) {
    try {
      for (const key of PRIOR_V2_KEYS) window.localStorage.removeItem(key);
      window.localStorage.removeItem(LEGACY_WHITEBOARD_INK);
      window.localStorage.removeItem(LEGACY_WHITEBOARD_SETTINGS);
      window.localStorage.removeItem(LEGACY_MANIPULATIVES);
    } catch {
      /* ignore */
    }
  }
  return merged;
}

/** Persist the board. Returns true when the write stuck. On a quota
 *  failure (large imported PDFs) retries without pages so ink + pieces
 *  still save. */
export function saveBoard(docKey: string, state: BoardStateV2, savedAt: number): boolean {
  if (typeof window === "undefined") return false;
  const doc: BoardDocV2 = { version: 2, ...state, savedAt };
  try {
    window.localStorage.setItem(docKey, JSON.stringify(doc));
    return true;
  } catch {
    try {
      window.localStorage.setItem(docKey, JSON.stringify({ ...doc, pages: [] }));
      return true;
    } catch {
      return false;
    }
  }
}

export function clearBoard(docKey: string): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(docKey);
  } catch {
    /* ignore */
  }
}
