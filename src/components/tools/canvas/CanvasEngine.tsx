"use client";

// KaTeX stylesheet for math-text rendering. Imported here (not in the shared
// projection DrawingOverlay) so it only loads on canvas-tool routes, keeping
// it out of the projection bundle. The katex JS itself is lazy-loaded below.
import "katex/dist/katex.min.css";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import Button from "@/components/ui/Button";
import Tray from "../manipulatives/Tray";
import ItemView, { type ItemFx } from "../manipulatives/ItemView";
import SelectionOverlay, { type BBox } from "../manipulatives/SelectionOverlay";
import ContextMenu from "../manipulatives/ContextMenu";
import { makeItem, type Sample } from "../manipulatives/registry";
import { GRID, itemSize, rotatedHalfExtent } from "../manipulatives/constants";
import { snapToGrid, snapRotation, rotationStep, snapToNeighbors, snapToVertices, intersectsRect } from "../manipulatives/snap";
import { exportRects, printBoardToPdf } from "./exportPdf";
import { useInfiniteCanvas } from "./useInfiniteCanvas";
import {
  StrokeShape,
  isShapeTool,
  constrainShape,
  pointsToList,
  eraserHits,
  TEXT_FONT_WORLD,
  PEN_COLORS,
  HIGHLIGHTER_COLOR,
  type Tool,
  type Stroke,
  type StrokeKind,
} from "./ink";
import TextDock from "./TextEditor";
import { loadBoard, saveBoard, clearBoard } from "./storage";
import type { BackgroundImage, CanvasBackground } from "./types";
import {
  WORLD_PAGE_WIDTH,
  WORLD_PAGE_GAP,
  renderPdf,
  renderImage,
} from "./pdfImport";
import type { Item } from "../manipulatives/types";

/**
 * The unified canvas engine behind the Whiteboard and Manipulatives tools.
 *
 * One infinite SVG world under one camera, layered background pattern →
 * imported PDF/image pages → manipulative items → ink. The two routes are
 * thin shells over this component: Whiteboard opens with the manipulatives
 * tray collapsed, Manipulatives with it open — each with its own persisted
 * document (docKey), migrated once from the legacy per-tool localStorage
 * keys.
 *
 * Interaction is a single pointer mode machine. Priority at pointer down:
 * gesture (2 fingers) > pan (space) > active ink tool > item drag > marquee.
 * The "select" tool is the default, so manipulative dragging/marquee feel
 * is unchanged; picking any ink tool routes pointerdowns to drawing instead
 * of item hit-testing. Undo/redo is whole-board snapshots (items + strokes
 * + pages), which makes erasing and page removal undoable for free.
 */

type CanvasTool = "select" | Tool;

// Interaction modes for the single pointer pipeline.
type Mode = "idle" | "pan" | "gesture" | "drag" | "marquee" | "rotate" | "draw" | "textdrag" | "textscale";

/** A text label being written or re-edited. Plain text is typed directly
 *  on the canvas (inline caret at wx,wy); math is typed in the dock. */
interface EditingText {
  id: string;
  wx: number;
  wy: number;
  value: string; // LaTeX source (math mode); plain text lives in the DOM caret
  isMath: boolean;
  existing: boolean; // re-editing a placed label vs. writing a new one
  fontSize: number;
  color: string;
}

// One undo step — the full committed board. Boards are a few dozen small
// objects plus stroke strings (pages are shared by reference between
// snapshots), so whole-state snapshots are cheap and simple.
interface Snapshot {
  items: Item[];
  strokes: Stroke[];
  pages: BackgroundImage[];
}

const BG_OPTIONS: { key: CanvasBackground; label: string; icon: React.ReactNode }[] = [
  {
    key: "blank",
    label: "Blank",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <rect x="4" y="4" width="16" height="16" rx="1.5" />
      </svg>
    ),
  },
  {
    key: "dots",
    label: "Dots",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        {[6, 12, 18].flatMap((y) => [6, 12, 18].map((x) => (
          <circle key={`${x}-${y}`} cx={x} cy={y} r="1.4" />
        )))}
      </svg>
    ),
  },
  {
    key: "grid",
    label: "Grid",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
        <path d="M4 10h16M4 15h16M10 4v16M15 4v16" />
      </svg>
    ),
  },
  {
    key: "coordinate",
    label: "Coordinate plane",
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true">
        <path d="M12 3v18M3 12h18" />
      </svg>
    ),
  },
];

let uidCounter = 0;
function uid(): string {
  uidCounter += 1;
  return `m${Date.now().toString(36)}${uidCounter.toString(36)}`;
}

export default function CanvasEngine({
  docKey,
  trayDefaultOpen = false,
}: {
  /** localStorage key for the board document. */
  docKey: string;
  /** Whether the manipulatives tray starts open or collapsed to a tab. */
  trayDefaultOpen?: boolean;
}) {
  const cv = useInfiniteCanvas(true);
  const { svgRef, cameraRef, tick, bump, screenToWorld, toWorldScale, localPoint } = cv;

  const [items, setItems] = useState<Item[]>([]);
  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [pages, setPages] = useState<BackgroundImage[]>([]);
  const [background, setBackground] = useState<CanvasBackground>("dots");
  const [selection, setSelection] = useState<Set<string>>(new Set());
  const [gridSnap, setGridSnap] = useState(true);
  const [marquee, setMarquee] = useState<BBox | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [tool, setTool] = useState<CanvasTool>("select");
  const [color, setColor] = useState(PEN_COLORS[0]);
  const [menu, setMenu] = useState<{ x: number; y: number; itemId: string } | null>(null);
  // Right-click menu for a placed text label: colour swatches + size slider.
  const [textMenu, setTextMenu] = useState<{ x: number; y: number; strokeId: string } | null>(null);
  // pushHistory once per menu-open, on the first actual change — so the
  // whole colour+size tweak session undoes in one step.
  const textMenuMutatedRef = useRef(false);
  const [trayOpen, setTrayOpen] = useState(trayDefaultOpen);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  // One-shot piece animation (colour sweep / coin flip); cleared on a timer
  // so the extra underlay/wrapper doesn't linger after the animation ends.
  const [fx, setFx] = useState<(ItemFx & { itemId: string }) | null>(null);
  const fxCounter = useRef(0);
  const fxTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const playFx = useCallback((itemId: string, type: ItemFx["type"], prev: Item) => {
    fxCounter.current += 1;
    setFx({ itemId, type, n: fxCounter.current, prev });
    if (fxTimer.current) clearTimeout(fxTimer.current);
    fxTimer.current = setTimeout(() => setFx(null), 420);
  }, []);
  // Bumped whenever the history stacks change so button disabled-states update.
  const [historyTick, setHistoryTick] = useState(0);

  // Text tool editing state. Plain text renders as an inline caret on the
  // canvas (contentEditable in a foreignObject); math is typed in the dock.
  const [editing, setEditing] = useState<EditingText | null>(null);
  const inlineRef = useRef<HTMLDivElement | null>(null);
  // Remembers whether the last text box was plain or math, so placing several
  // labels in a row doesn't require re-toggling the mode each time.
  const lastMathModeRef = useRef(false);
  // A placed label clicked with the select tool: boxed with a resize handle;
  // clicking it again enters edit mode.
  const [selectedTextId, setSelectedTextId] = useState<string | null>(null);
  const selectedTextIdRef = useRef(selectedTextId);
  selectedTextIdRef.current = selectedTextId;
  // Live font-size scale drag from the selection box's corner circle.
  const textScaleRef = useRef<{ id: string; startDist: number; startFs: number; fs: number } | null>(null);

  // KaTeX is lazy-loaded (≈280KB) the first time math text is needed —
  // either the text tool goes into math mode or a saved math item renders.
  const [katex, setKatex] = useState<typeof import("katex").default | null>(null);
  const katexLoadingRef = useRef(false);
  const ensureKatex = useCallback(() => {
    if (katexLoadingRef.current) return;
    katexLoadingRef.current = true;
    import("katex").then(
      (m) => setKatex(() => m.default),
      () => {
        katexLoadingRef.current = false; // allow a retry on next trigger
      }
    );
  }, []);
  const renderMath = useCallback(
    (latex: string): string | null => {
      if (!katex) return null;
      try {
        return katex.renderToString(latex, { throwOnError: false, displayMode: false });
      } catch {
        return null;
      }
    },
    [katex]
  );
  useEffect(() => {
    if (katex) return;
    if (editing?.isMath || strokes.some((s) => s.isMath)) ensureKatex();
  }, [katex, editing?.isMath, strokes, ensureKatex]);

  // Live-drag / rotate / ink refs — mutated during a gesture, read on render
  // (we bump the camera tick to re-render) and committed on pointer-up.
  const modeRef = useRef<Mode>("idle");
  // snapDx/snapDy: live vertex-lock adjustment (pattern blocks clicking
  // together mid-drag) — rendered on top of dx/dy and kept on release.
  const dragRef = useRef<{
    startSx: number;
    startSy: number;
    dx: number;
    dy: number;
    snapDx: number;
    snapDy: number;
    snapped: boolean;
  } | null>(null);
  const rotateRef = useRef<{ center: { x: number; y: number }; startAngle: number; delta: number } | null>(null);
  const marqueeStartRef = useRef<{ x: number; y: number; shift: boolean } | null>(null);
  // Right-button drag pans; a right-click that never moved opens the
  // context menu on the item under the cursor instead.
  const rightPanRef = useRef<{ startSx: number; startSy: number; moved: boolean } | null>(null);
  // Live drag of a placed text label (select tool). World-unit offset is
  // applied as a transform while dragging and committed on pointer-up.
  const textDragRef = useRef<{ id: string; startSx: number; startSy: number; dx: number; dy: number; wasSelected: boolean } | null>(null);
  const inkRef = useRef<{ id: string; pts: string } | null>(null);
  const addOffsetRef = useRef(0);
  const itemsRef = useRef(items);
  itemsRef.current = items;
  const strokesRef = useRef(strokes);
  strokesRef.current = strokes;
  const pagesRef = useRef(pages);
  pagesRef.current = pages;
  const selectionRef = useRef(selection);
  selectionRef.current = selection;
  const backgroundRef = useRef(background);
  backgroundRef.current = background;
  const gridSnapRef = useRef(gridSnap);
  gridSnapRef.current = gridSnap;

  // ── Undo / redo ──────────────────────────────────────────────────────
  const pastRef = useRef<Snapshot[]>([]);
  const futureRef = useRef<Snapshot[]>([]);

  /** Call BEFORE any committed mutation of items/strokes/pages. */
  const pushHistory = useCallback(() => {
    pastRef.current.push({
      items: itemsRef.current,
      strokes: strokesRef.current,
      pages: pagesRef.current,
    });
    if (pastRef.current.length > 100) pastRef.current.shift();
    futureRef.current = [];
    setHistoryTick((t) => t + 1);
  }, []);

  const undo = useCallback(() => {
    const prev = pastRef.current.pop();
    if (!prev) return;
    futureRef.current.push({
      items: itemsRef.current,
      strokes: strokesRef.current,
      pages: pagesRef.current,
    });
    setItems(prev.items);
    setStrokes(prev.strokes);
    setPages(prev.pages);
    setSelection(new Set());
    setHistoryTick((t) => t + 1);
  }, []);

  const redo = useCallback(() => {
    const next = futureRef.current.pop();
    if (!next) return;
    pastRef.current.push({
      items: itemsRef.current,
      strokes: strokesRef.current,
      pages: pagesRef.current,
    });
    setItems(next.items);
    setStrokes(next.strokes);
    setPages(next.pages);
    setSelection(new Set());
    setHistoryTick((t) => t + 1);
  }, []);

  // ── Load once on mount (migrating legacy keys if needed) ─────────────
  useEffect(() => {
    const saved = loadBoard(docKey);
    if (saved.items.length) {
      setItems(saved.items);
      uidCounter = saved.items.length; // keep fresh ids clear of restored ones
    }
    if (saved.strokes.length) setStrokes(saved.strokes);
    if (saved.pages.length) setPages(saved.pages);
    setBackground(saved.background);
    setGridSnap(saved.gridSnap);
    if (saved.camera) {
      cameraRef.current = saved.camera;
      bump();
    }
    setLoaded(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Debounced auto-save on board/camera change ───────────────────────
  useEffect(() => {
    if (!loaded) return;
    const t = setTimeout(
      () =>
        saveBoard(
          docKey,
          {
            items: itemsRef.current,
            strokes: strokesRef.current,
            pages: pagesRef.current,
            background: backgroundRef.current,
            gridSnap: gridSnapRef.current,
            camera: cameraRef.current,
          },
          Date.now()
        ),
      400
    );
    return () => clearTimeout(t);
  }, [items, strokes, pages, background, gridSnap, tick, loaded, docKey, cameraRef]);

  const maxZ = useCallback(() => itemsRef.current.reduce((m, i) => Math.max(m, i.z), 0), []);

  // ── Save as PDF (print pipeline) ─────────────────────────────────────
  // The world scene <g>; cloned into hidden print pages on export.
  const sceneRef = useRef<SVGGElement | null>(null);
  const savePdf = useCallback(() => {
    // Deselect first so no selection chrome (outlines, resize dots) is
    // cloned into the printout, then wait two frames for the re-render.
    setSelection(new Set());
    setSelectedTextId(null);
    setMenu(null);
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        const scene = sceneRef.current;
        if (!scene) return;
        const rects = exportRects(itemsRef.current, strokesRef.current, pagesRef.current);
        printBoardToPdf(scene, rects);
      })
    );
  }, []);

  // ── Add from tray: drop at viewport centre, offset-stacked ───────────
  const addFromTray = useCallback(
    (sample: Sample) => {
      const rect = svgRef.current?.getBoundingClientRect();
      const cxScreen = (rect?.width ?? 800) / 2;
      const cyScreen = (rect?.height ?? 600) / 2;
      const off = (addOffsetRef.current % 6) * 14;
      addOffsetRef.current += 1;
      const w = screenToWorld(cxScreen + off, cyScreen + off);
      const at = gridSnap ? { x: snapToGrid(w.x), y: snapToGrid(w.y) } : w;
      const id = uid();
      const item = makeItem(sample, at, id, maxZ() + 1);
      pushHistory();
      setItems((prev) => [...prev, item]);
      setSelection(new Set([id]));
      setTool("select");
    },
    [svgRef, screenToWorld, gridSnap, maxZ, pushHistory]
  );

  // ── Selection bounding box (union of rotated AABBs) ──────────────────
  const selBBox = useMemo<BBox | null>(() => {
    const sel = items.filter((i) => selection.has(i.id));
    if (sel.length === 0) return null;
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    for (const it of sel) {
      const he = rotatedHalfExtent(itemSize(it), it.rot);
      x1 = Math.min(x1, it.x - he.w);
      y1 = Math.min(y1, it.y - he.h);
      x2 = Math.max(x2, it.x + he.w);
      y2 = Math.max(y2, it.y + he.h);
    }
    return { x1, y1, x2, y2 };
  }, [items, selection]);

  // ── Mutations ────────────────────────────────────────────────────────
  const deleteSelected = useCallback(() => {
    pushHistory();
    setItems((prev) => prev.filter((i) => !selectionRef.current.has(i.id)));
    setSelection(new Set());
  }, [pushHistory]);

  const duplicateSelected = useCallback(() => {
    const sel = itemsRef.current.filter((i) => selectionRef.current.has(i.id));
    if (!sel.length) return;
    pushHistory();
    let z = itemsRef.current.reduce((m, i) => Math.max(m, i.z), 0);
    const clones: Item[] = sel.map((i) => ({ ...i, id: uid(), x: i.x + GRID, y: i.y + GRID, z: ++z }));
    setItems((prev) => [...prev, ...clones]);
    setSelection(new Set(clones.map((c) => c.id)));
  }, [pushHistory]);

  /** Flip a counter's colour or an algebra tile's sign. */
  const flipItem = useCallback(
    (id: string) => {
      const target = itemsRef.current.find((i) => i.id === id);
      if (!target || (target.kind !== "counter" && target.kind !== "algebra")) return;
      pushHistory();
      setItems((prev) =>
        prev.map((i) => {
          if (i.id !== id) return i;
          if (i.kind === "counter") return { ...i, color: i.color === "yellow" ? "red" : "yellow" };
          if (i.kind === "algebra") return { ...i, sign: (i.sign * -1) as 1 | -1 };
          return i;
        })
      );
      playFx(id, "flip", target);
    },
    [pushHistory, playFx]
  );

  const tintItem = useCallback(
    (id: string, tint: string | undefined) => {
      const target = itemsRef.current.find((i) => i.id === id);
      if (!target || target.tint === tint) return;
      pushHistory();
      setItems((prev) => prev.map((i) => (i.id === id ? { ...i, tint } : i)));
      playFx(id, "sweep", target);
    },
    [pushHistory, playFx]
  );

  const bringToFront = useCallback(
    (id: string) => {
      pushHistory();
      const top = maxZ() + 1;
      setItems((prev) => prev.map((i) => (i.id === id ? { ...i, z: top } : i)));
    },
    [pushHistory, maxZ]
  );

  const duplicateOne = useCallback(
    (id: string) => {
      const src = itemsRef.current.find((i) => i.id === id);
      if (!src) return;
      pushHistory();
      const clone: Item = { ...src, id: uid(), x: src.x + GRID, y: src.y + GRID, z: maxZ() + 1 };
      setItems((prev) => [...prev, clone]);
      setSelection(new Set([clone.id]));
    },
    [pushHistory, maxZ]
  );

  const deleteOne = useCallback(
    (id: string) => {
      pushHistory();
      setItems((prev) => prev.filter((i) => i.id !== id));
      setSelection((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    },
    [pushHistory]
  );

  const clearInk = useCallback(() => {
    if (!strokesRef.current.length) return;
    pushHistory();
    setStrokes([]);
  }, [pushHistory]);

  const clearAll = useCallback(() => {
    pushHistory();
    setItems([]);
    setStrokes([]);
    setSelection(new Set());
    clearBoard(docKey);
  }, [pushHistory, docKey]);

  const removeImport = useCallback(() => {
    if (!pagesRef.current.length) return;
    pushHistory();
    setPages([]);
    setImportError(null);
  }, [pushHistory]);

  // ── Text tool ────────────────────────────────────────────────────────
  const editingRef = useRef(editing);
  useEffect(() => {
    editingRef.current = editing;
  }, [editing]);
  /** Commit the label being written/edited. Plain text is read from the
   *  inline caret's DOM; math from the dock's controlled value. Emptying an
   *  existing label deletes it. Idempotent — safe to call from both the
   *  inline editor's blur and the canvas pointerdown that caused it. */
  const commitText = useCallback(() => {
    const ed = editingRef.current;
    if (!ed) return;
    editingRef.current = null;
    setEditing(null);
    const value = ed.isMath ? ed.value : (inlineRef.current?.textContent ?? "");
    if (ed.existing) {
      const prev = strokesRef.current.find((s) => s.id === ed.id);
      if (!prev || (prev.text === value && !!prev.isMath === ed.isMath)) return;
      pushHistory();
      if (!value.trim()) {
        setStrokes((s) => s.filter((st) => st.id !== ed.id));
        setSelectedTextId(null);
      } else {
        setStrokes((s) => s.map((st) => (st.id === ed.id ? { ...st, text: value, isMath: ed.isMath } : st)));
      }
      return;
    }
    if (!value.trim()) return;
    pushHistory();
    setStrokes((s) => [
      ...s,
      {
        id: ed.id,
        kind: "text" as StrokeKind,
        points: `${ed.wx},${ed.wy}`,
        color: ed.color,
        width: 0,
        opacity: 1,
        tool: "text" as Tool,
        text: value,
        fontSize: ed.fontSize,
        isMath: ed.isMath,
      },
    ]);
  }, [pushHistory]);

  const cancelEdit = useCallback(() => {
    editingRef.current = null;
    setEditing(null);
  }, []);

  /** Re-open a placed label for typing (select tool: click it while it's
   *  already selected). */
  const openEditFor = useCallback(
    (strokeId: string) => {
      const s = strokesRef.current.find((st) => st.id === strokeId);
      if (!s || s.kind !== "text") return;
      const [pt] = pointsToList(s.points);
      if (!pt) return;
      if (s.isMath) ensureKatex();
      setEditing({
        id: s.id,
        wx: pt[0],
        wy: pt[1],
        value: s.text ?? "",
        isMath: !!s.isMath,
        existing: true,
        fontSize: s.fontSize ?? TEXT_FONT_WORLD,
        color: s.color,
      });
    },
    [ensureKatex]
  );

  /** Insert a unicode chip at the inline canvas caret (plain-text mode). */
  const insertPlain = useCallback((snippet: string) => {
    const el = inlineRef.current;
    if (!el) return;
    el.focus();
    document.execCommand("insertText", false, snippet);
  }, []);

  // Seed the inline caret whenever a plain-text edit begins (or the mode
  // flips back to text): set its content, focus it, caret at the end.
  useEffect(() => {
    if (!editing || editing.isMath) return;
    const el = inlineRef.current;
    if (!el) return;
    el.textContent = editing.value;
    const focusCaret = () => {
      el.focus();
      const sel = window.getSelection();
      if (sel) {
        const range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        sel.removeAllRanges();
        sel.addRange(range);
      }
    };
    focusCaret();
    // The placing click's pointerup can wrestle focus back to the canvas in
    // some browsers — re-assert on the next frame.
    const raf = requestAnimationFrame(focusCaret);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editing?.id, editing?.isMath]);

  /** Recolour / resize a placed text label from its right-click menu.
   *  History is pushed once per menu-open so the tweak undoes in one step. */
  const mutateTextStroke = useCallback(
    (id: string, patch: Partial<Pick<Stroke, "color" | "fontSize">>) => {
      if (!textMenuMutatedRef.current) {
        textMenuMutatedRef.current = true;
        pushHistory();
      }
      setStrokes((prev) => prev.map((s) => (s.id === id ? { ...s, ...patch } : s)));
    },
    [pushHistory]
  );

  const deleteTextStroke = useCallback(
    (id: string) => {
      pushHistory();
      setStrokes((prev) => prev.filter((s) => s.id !== id));
      setTextMenu(null);
    },
    [pushHistory]
  );

  const setTextMode = useCallback(
    (math: boolean) => {
      lastMathModeRef.current = math;
      if (math) ensureKatex();
      setEditing((prev) => {
        if (!prev) return prev;
        // Carry what's been typed across the mode switch: the inline
        // caret's DOM text feeds the LaTeX input and vice versa.
        const carried = prev.isMath ? prev.value : (inlineRef.current?.textContent ?? prev.value);
        return { ...prev, isMath: math, value: carried };
      });
    },
    [ensureKatex]
  );

  // ── PDF / image import ───────────────────────────────────────────────
  const onImportClick = useCallback(() => {
    setImportError(null);
    fileInputRef.current?.click();
  }, []);

  const onFilesChosen = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files ?? []);
      // Reset the input so choosing the same file again re-fires onChange.
      e.target.value = "";
      if (files.length === 0) return;

      setImporting(true);
      setImportError(null);
      try {
        // New pages stack below whatever is already on the board.
        const existing = pagesRef.current;
        let nextY =
          existing.length === 0
            ? 0
            : Math.max(...existing.map((p) => p.y + p.height)) + WORLD_PAGE_GAP;
        const added: BackgroundImage[] = [];

        for (const file of files) {
          const rasters =
            file.type === "application/pdf"
              ? await renderPdf(file)
              : file.type.startsWith("image/")
                ? [await renderImage(file)]
                : [];
          for (const r of rasters) {
            const worldHeight = (WORLD_PAGE_WIDTH * r.px.h) / r.px.w;
            added.push({
              id: `bg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
              href: r.href,
              x: 0,
              y: nextY,
              width: WORLD_PAGE_WIDTH,
              height: worldHeight,
            });
            nextY += worldHeight + WORLD_PAGE_GAP;
          }
        }

        if (added.length === 0) {
          setImportError("Unsupported file — pick a PDF or an image.");
          return;
        }

        pushHistory();
        setPages((prev) => [...prev, ...added]);
        // Frame the first newly-added page.
        cv.fitToBounds(added[0]);
      } catch (err) {
        console.error("Canvas import failed", err);
        setImportError("Could not read that file. Try another PDF or image.");
      } finally {
        setImporting(false);
      }
    },
    [pushHistory, cv]
  );

  // ── Keyboard shortcuts ───────────────────────────────────────────────
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      const mod = e.ctrlKey || e.metaKey;
      if (mod && (e.key === "z" || e.key === "Z") && !e.shiftKey) {
        e.preventDefault();
        undo();
      } else if ((mod && (e.key === "y" || e.key === "Y")) || (mod && e.shiftKey && (e.key === "z" || e.key === "Z"))) {
        e.preventDefault();
        redo();
      } else if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedTextIdRef.current) {
          e.preventDefault();
          deleteTextStroke(selectedTextIdRef.current);
          setSelectedTextId(null);
        } else if (selectionRef.current.size) {
          e.preventDefault();
          deleteSelected();
        }
      } else if (mod && (e.key === "d" || e.key === "D")) {
        if (selectionRef.current.size) {
          e.preventDefault();
          duplicateSelected();
        }
      } else if (e.key === "Escape") {
        setSelection(new Set());
        setMenu(null);
        setTextMenu(null);
        setSelectedTextId(null);
        setEditing(null);
        editingRef.current = null;
        setTool("select");
      } else if (e.key.startsWith("Arrow") && selectionRef.current.size) {
        e.preventDefault();
        const d = e.shiftKey ? GRID : GRID / 4;
        const dx = e.key === "ArrowLeft" ? -d : e.key === "ArrowRight" ? d : 0;
        const dy = e.key === "ArrowUp" ? -d : e.key === "ArrowDown" ? d : 0;
        pushHistory();
        setItems((prev) => prev.map((i) => (selectionRef.current.has(i.id) ? { ...i, x: i.x + dx, y: i.y + dy } : i)));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [deleteSelected, duplicateSelected, undo, redo, pushHistory]);

  // ── Hide site chrome for the tool's lifetime ─────────────────────────
  useEffect(() => {
    document.body.classList.add("project-mode");
    return () => document.body.classList.remove("project-mode");
  }, []);

  // ── Pointer pipeline ─────────────────────────────────────────────────
  const onPointerDown = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      const svg = svgRef.current;
      if (!svg) return;
      setMenu(null);
      setTextMenu(null);
      // A click on the canvas commits whatever label is being typed (clicks
      // inside the inline editor / dock stopPropagation and never get here).
      commitText();
      const { sx, sy } = localPoint(e);

      // Right button → pan-drag. If the pointer never moves, pointer-up
      // opens the context menu instead (classic right-click).
      if (e.button === 2) {
        svg.setPointerCapture(e.pointerId);
        cv.panDragRef.current = { startX: sx, startY: sy, startCam: { ...cameraRef.current } };
        rightPanRef.current = { startSx: sx, startSy: sy, moved: false };
        modeRef.current = "pan";
        return;
      }
      cv.trackPointer(e.pointerId, sx, sy);

      // Two fingers → pinch/two-finger pan.
      if (cv.pointersRef.current.size >= 2) {
        dragRef.current = null;
        inkRef.current = null;
        cv.beginGesture();
        modeRef.current = "gesture";
        return;
      }
      // Space held → pan.
      if (cv.spaceHeldRef.current) {
        svg.setPointerCapture(e.pointerId);
        cv.panDragRef.current = { startX: sx, startY: sy, startCam: { ...cameraRef.current } };
        modeRef.current = "pan";
        return;
      }
      // Text tool → a tap starts a blinking caret right on the canvas
      // (plain text) or focuses the math dock (math mode). No drag stroke.
      if (tool === "text") {
        // Cancel the compatibility mousedown that follows pointerdown for
        // MOUSE input — its default action moves focus to the body, which
        // blurs the freshly-focused caret and instantly commits/closes the
        // empty editor. (Touch never hit this, hence "works on touch".)
        e.preventDefault();
        // Clicking an existing label with the text tool re-opens it for
        // typing rather than starting a new label on top of it.
        const editHit = (e.target as Element).closest("[data-stroke-id]");
        const editId = editHit?.getAttribute("data-stroke-id") ?? null;
        if (editId) {
          setSelectedTextId(null);
          openEditFor(editId);
          return;
        }
        const w = screenToWorld(sx, sy);
        setSelectedTextId(null);
        setEditing({
          id: uid(),
          wx: w.x,
          wy: w.y,
          value: "",
          isMath: lastMathModeRef.current,
          existing: false,
          fontSize: TEXT_FONT_WORLD,
          color,
        });
        return;
      }
      // Any other ink tool → start a stroke (takes precedence over items).
      if (tool !== "select") {
        svg.setPointerCapture(e.pointerId);
        const w = screenToWorld(sx, sy);
        inkRef.current = { id: uid(), pts: `${w.x},${w.y}` };
        modeRef.current = "draw";
        bump();
        return;
      }
      // The selected text's corner circle → font-size scale drag.
      const scaleHit = (e.target as Element).closest("[data-text-scale]");
      const scaleFor = selectedTextIdRef.current;
      if (scaleHit && scaleFor) {
        const s = strokesRef.current.find((st) => st.id === scaleFor);
        const [pt] = s ? pointsToList(s.points) : [];
        if (s && pt) {
          svg.setPointerCapture(e.pointerId);
          const w = screenToWorld(sx, sy);
          const startFs = s.fontSize ?? TEXT_FONT_WORLD;
          textScaleRef.current = {
            id: s.id,
            startDist: Math.max(8, Math.hypot(w.x - pt[0], w.y - pt[1])),
            startFs,
            fs: startFs,
          };
          modeRef.current = "textscale";
          return;
        }
      }
      // Hit a placed text label? (Text renders above items, so it wins.)
      // First click selects (boxes) it; clicking it while selected opens it
      // for typing; dragging moves it either way.
      const strokeHit = (e.target as Element).closest("[data-stroke-id]");
      const strokeId = strokeHit?.getAttribute("data-stroke-id") ?? null;
      if (strokeId) {
        svg.setPointerCapture(e.pointerId);
        setSelection(new Set());
        textDragRef.current = {
          id: strokeId,
          startSx: sx,
          startSy: sy,
          dx: 0,
          dy: 0,
          wasSelected: selectedTextIdRef.current === strokeId,
        };
        setSelectedTextId(strokeId);
        modeRef.current = "textdrag";
        return;
      }
      setSelectedTextId(null);
      // Hit an item?
      const hit = (e.target as Element).closest("[data-item-id]");
      const id = hit?.getAttribute("data-item-id") ?? null;
      if (id) {
        svg.setPointerCapture(e.pointerId);
        setSelection((prev) => {
          if (e.shiftKey) {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
          }
          return prev.has(id) ? prev : new Set([id]);
        });
        dragRef.current = { startSx: sx, startSy: sy, dx: 0, dy: 0, snapDx: 0, snapDy: 0, snapped: false };
        modeRef.current = "drag";
        return;
      }
      // Empty canvas → marquee select.
      svg.setPointerCapture(e.pointerId);
      if (!e.shiftKey) setSelection(new Set());
      const w = screenToWorld(sx, sy);
      marqueeStartRef.current = { x: w.x, y: w.y, shift: e.shiftKey };
      setMarquee({ x1: w.x, y1: w.y, x2: w.x, y2: w.y });
      modeRef.current = "marquee";
    },
    [svgRef, localPoint, cv, cameraRef, screenToWorld, tool, bump, commitText, color, openEditFor]
  );

  const onPointerMove = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      const { sx, sy } = localPoint(e);
      if (cv.pointersRef.current.has(e.pointerId)) cv.trackPointer(e.pointerId, sx, sy);
      const mode = modeRef.current;

      if (mode === "gesture" || cv.pointersRef.current.size >= 2) {
        cv.updateGesture();
        return;
      }
      if (mode === "pan" && cv.panDragRef.current) {
        const p = cv.panDragRef.current;
        if (rightPanRef.current && Math.hypot(sx - rightPanRef.current.startSx, sy - rightPanRef.current.startSy) > 4) {
          rightPanRef.current.moved = true;
        }
        cameraRef.current = { ...p.startCam, tx: p.startCam.tx + (sx - p.startX), ty: p.startCam.ty + (sy - p.startY) };
        bump();
        return;
      }
      if (mode === "draw" && inkRef.current) {
        const w = screenToWorld(sx, sy);
        if (tool !== "select" && isShapeTool(tool)) {
          // Shapes keep only start + current end. Shift constrains: lines
          // snap to 0/45/90°, rect/ellipse become square/circle.
          const start = inkRef.current.pts.split(" ")[0];
          const [ex, ey] = e.shiftKey ? constrainShape(tool, start, w.x, w.y) : [w.x, w.y];
          inkRef.current.pts = `${start} ${ex},${ey}`;
        } else {
          inkRef.current.pts += ` ${w.x},${w.y}`;
        }
        bump();
        return;
      }
      if (mode === "drag" && dragRef.current) {
        const d = dragRef.current;
        d.dx = toWorldScale(sx - d.startSx);
        d.dy = toWorldScale(sy - d.startSy);
        // Live vertex lock: pattern blocks magnetically click onto a
        // neighbour's vertex while dragging. Recomputed from the raw
        // pointer delta each move, so dragging past the threshold
        // releases the lock naturally.
        d.snapDx = 0;
        d.snapDy = 0;
        d.snapped = false;
        const sel = selectionRef.current;
        const primary = itemsRef.current.find((i) => sel.has(i.id) && i.kind === "patternblock");
        if (primary) {
          const others = itemsRef.current.filter((i) => !sel.has(i.id));
          const snap = snapToVertices(
            { ...primary, x: primary.x + d.dx, y: primary.y + d.dy },
            others,
            toWorldScale(16)
          );
          if (snap.snapped) {
            d.snapDx = snap.dx;
            d.snapDy = snap.dy;
            d.snapped = true;
          }
        }
        bump();
        return;
      }
      if (mode === "textdrag" && textDragRef.current) {
        textDragRef.current.dx = toWorldScale(sx - textDragRef.current.startSx);
        textDragRef.current.dy = toWorldScale(sy - textDragRef.current.startSy);
        bump();
        return;
      }
      if (mode === "textscale" && textScaleRef.current) {
        const ts = textScaleRef.current;
        const s = strokesRef.current.find((st) => st.id === ts.id);
        const [pt] = s ? pointsToList(s.points) : [];
        if (pt) {
          const w = screenToWorld(sx, sy);
          const dist = Math.max(8, Math.hypot(w.x - pt[0], w.y - pt[1]));
          ts.fs = Math.max(10, Math.min(200, (ts.startFs * dist) / ts.startDist));
          bump();
        }
        return;
      }
      if (mode === "rotate" && rotateRef.current) {
        const w = screenToWorld(sx, sy);
        const r = rotateRef.current;
        const angle = (Math.atan2(w.y - r.center.y, w.x - r.center.x) * 180) / Math.PI;
        r.delta = angle - r.startAngle;
        bump();
        return;
      }
      if (mode === "marquee" && marqueeStartRef.current) {
        const w = screenToWorld(sx, sy);
        const s = marqueeStartRef.current;
        setMarquee({ x1: s.x, y1: s.y, x2: w.x, y2: w.y });
      }
    },
    [localPoint, cv, cameraRef, bump, toWorldScale, screenToWorld, tool]
  );

  /** Commit the in-progress ink stroke (or apply the eraser pass). */
  const finishInk = useCallback(() => {
    const ink = inkRef.current;
    if (!ink || tool === "select") return;
    inkRef.current = null;
    if (tool === "eraser") {
      // Eraser hit-test in world coords: an 18px screen radius becomes
      // 18 / zoom world units, so the eraser "feels" the same size at any
      // zoom level. Hits at end-of-stroke for predictability — and since
      // history is snapshot-based, erasing is undoable.
      const eraserPts = pointsToList(ink.pts);
      if (eraserPts.length === 0) return;
      const worldRadius = 18 / cameraRef.current.zoom;
      const survivors = strokesRef.current.filter((s) => !eraserHits(s, eraserPts, worldRadius));
      if (survivors.length !== strokesRef.current.length) {
        pushHistory();
        setStrokes(survivors);
      }
      bump();
      return;
    }
    // Shapes need a real drag — a click that never moved is discarded.
    if (isShapeTool(tool) && pointsToList(ink.pts).length < 2) return;
    const kind: StrokeKind = isShapeTool(tool) ? (tool as StrokeKind) : "path";
    pushHistory();
    setStrokes((prev) => [
      ...prev,
      {
        id: ink.id,
        kind,
        points: ink.pts,
        color: tool === "highlighter" ? HIGHLIGHTER_COLOR : color,
        width: tool === "highlighter" ? 18 : 3,
        opacity: tool === "highlighter" ? 0.4 : 1,
        tool,
      },
    ]);
  }, [tool, color, cameraRef, pushHistory, bump]);

  const onPointerUp = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      cv.dropPointer(e.pointerId);
      const mode = modeRef.current;

      if (mode === "draw") {
        modeRef.current = "idle";
        finishInk();
      } else if (mode === "textdrag" && textDragRef.current) {
        const { id, dx, dy, wasSelected } = textDragRef.current;
        textDragRef.current = null;
        modeRef.current = "idle";
        const moved = Math.hypot(dx, dy) * cameraRef.current.zoom > 3;
        if (moved) {
          pushHistory();
          setStrokes((prev) =>
            prev.map((s) => {
              if (s.id !== id) return s;
              const [pt] = pointsToList(s.points);
              return pt ? { ...s, points: `${pt[0] + dx},${pt[1] + dy}` } : s;
            })
          );
        } else if (wasSelected) {
          // Second click on an already-selected label → start typing in it.
          openEditFor(id);
        }
      } else if (mode === "textscale" && textScaleRef.current) {
        const ts = textScaleRef.current;
        textScaleRef.current = null;
        modeRef.current = "idle";
        if (Math.round(ts.fs) !== Math.round(ts.startFs)) {
          pushHistory();
          setStrokes((prev) =>
            prev.map((s) => (s.id === ts.id ? { ...s, fontSize: Math.round(ts.fs) } : s))
          );
        }
      } else if (mode === "drag" && dragRef.current) {
        // Fold the live vertex lock into the committed delta so pieces stay
        // exactly where they visually clicked together.
        const { snapDx, snapDy, snapped } = dragRef.current;
        const dx = dragRef.current.dx + snapDx;
        const dy = dragRef.current.dy + snapDy;
        dragRef.current = null;
        modeRef.current = "idle";
        if (dx !== 0 || dy !== 0) {
          const sel = selectionRef.current;
          const moved = itemsRef.current.map((i) => (sel.has(i.id) ? { ...i, x: i.x + dx, y: i.y + dy } : i));
          // Snap the group by the first selected item, preserving offsets.
          // A vertex lock between shapes is exact and beats everything —
          // never let the grid pull a locked piece off its neighbour.
          // Otherwise neighbour edges win over the grid on each axis
          // independently — so a 1/4 tile sits flush against a 1/2 tile
          // even though their edge positions don't share a grid line
          // (centre-snapping alone can never make 2×(1/4) meet a 1/2).
          const primary = moved.find((i) => sel.has(i.id));
          let adjX = 0, adjY = 0;
          if (primary && !snapped) {
            const others = moved.filter((i) => !sel.has(i.id));
            const near = snapToNeighbors(primary, others, toWorldScale(12));
            adjX = near.snappedX ? near.x - primary.x : gridSnap ? snapToGrid(primary.x) - primary.x : 0;
            adjY = near.snappedY ? near.y - primary.y : gridSnap ? snapToGrid(primary.y) - primary.y : 0;
          }
          pushHistory();
          setItems(moved.map((i) => (sel.has(i.id) ? { ...i, x: i.x + adjX, y: i.y + adjY } : i)));
        }
      } else if (mode === "rotate" && rotateRef.current) {
        const delta = rotateRef.current.delta;
        rotateRef.current = null;
        modeRef.current = "idle";
        const sel = selectionRef.current;
        pushHistory();
        setItems((prev) => prev.map((i) => (sel.has(i.id) ? { ...i, rot: snapRotation(i.rot + delta, rotationStep(i, e.shiftKey)) } : i)));
      } else if (mode === "marquee" && marqueeStartRef.current) {
        const m = marquee;
        const start = marqueeStartRef.current;
        marqueeStartRef.current = null;
        modeRef.current = "idle";
        setMarquee(null);
        if (m) {
          const rect = { x1: m.x1, y1: m.y1, x2: m.x2, y2: m.y2 };
          const hits = itemsRef.current.filter((i) => intersectsRect(i, rect)).map((i) => i.id);
          setSelection((prev) => {
            const next = start.shift ? new Set(prev) : new Set<string>();
            hits.forEach((h) => next.add(h));
            return next;
          });
        }
      } else {
        modeRef.current = "idle";
        cv.panDragRef.current = null;
        // Stationary right-click → context menu on the item under the cursor.
        const rp = rightPanRef.current;
        rightPanRef.current = null;
        if (rp && !rp.moved && tool === "select") {
          const el = document.elementFromPoint(e.clientX, e.clientY);
          const strokeId = el?.closest("[data-stroke-id]")?.getAttribute("data-stroke-id") ?? null;
          const id = el?.closest("[data-item-id]")?.getAttribute("data-item-id") ?? null;
          const { sx, sy } = localPoint(e);
          if (strokeId) {
            textMenuMutatedRef.current = false;
            setTextMenu({ x: sx, y: sy, strokeId });
          } else if (id) {
            setSelection(new Set([id]));
            setMenu({ x: sx, y: sy, itemId: id });
          }
        }
      }
      try {
        svgRef.current?.releasePointerCapture(e.pointerId);
      } catch {
        /* pointer already released */
      }
    },
    [cv, gridSnap, toWorldScale, marquee, svgRef, pushHistory, finishInk, tool, localPoint, openEditFor, cameraRef]
  );

  // Suppress the native context menu — right-button drag pans the board,
  // and a stationary right-click opens the item menu from onPointerUp.
  const onContextMenu = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    e.preventDefault();
  }, []);

  // Double-click flips counters / algebra signs without opening the menu.
  const onDoubleClick = useCallback(
    (e: React.MouseEvent<SVGSVGElement>) => {
      if (tool !== "select") return;
      const hit = (e.target as Element).closest("[data-item-id]");
      const id = hit?.getAttribute("data-item-id");
      if (id) flipItem(id);
    },
    [tool, flipItem]
  );

  const onRotateStart = useCallback(
    (e: React.PointerEvent) => {
      const svg = svgRef.current;
      if (!svg || !selBBox) return;
      const { sx, sy } = localPoint(e);
      const w = screenToWorld(sx, sy);
      const center = { x: (selBBox.x1 + selBBox.x2) / 2, y: (selBBox.y1 + selBBox.y2) / 2 };
      const startAngle = (Math.atan2(w.y - center.y, w.x - center.x) * 180) / Math.PI;
      rotateRef.current = { center, startAngle, delta: 0 };
      modeRef.current = "rotate";
      svg.setPointerCapture(e.pointerId);
    },
    [svgRef, selBBox, localPoint, screenToWorld]
  );

  // ── Render ───────────────────────────────────────────────────────────
  const cam = cameraRef.current;
  const scale = 1 / cam.zoom; // world units per screen px
  const dragging = modeRef.current === "drag" && dragRef.current;
  const rotating = modeRef.current === "rotate" && rotateRef.current;
  const cursor = dragging
    ? "grabbing"
    : cv.spaceHeldRef.current
      ? "grab"
      : tool === "eraser"
        ? "cell"
        : tool === "text"
          ? "text"
          : tool !== "select"
            ? "crosshair"
            : "default";
  const menuItem = menu ? items.find((i) => i.id === menu.itemId) : null;
  const textMenuStroke = textMenu ? strokes.find((s) => s.id === textMenu.strokeId) ?? null : null;
  // historyTick keeps these fresh; refs don't trigger renders on their own.
  void historyTick;
  const canUndo = pastRef.current.length > 0;
  const canRedo = futureRef.current.length > 0;

  // Build the in-progress ink preview from the ref's current state.
  const previewStroke =
    inkRef.current && tool !== "select"
      ? {
          kind: (isShapeTool(tool) ? tool : "path") as StrokeKind,
          points: inkRef.current.pts,
          color: tool === "highlighter" ? HIGHLIGHTER_COLOR : tool === "eraser" ? "#9ca3af" : color,
          width: tool === "highlighter" ? 18 : tool === "eraser" ? 18 : 3,
          opacity: tool === "highlighter" ? 0.4 : tool === "eraser" ? 0.3 : 1,
          dashed: tool === "eraser",
        }
      : null;

  const mathPreview =
    editing?.isMath && editing.value.trim() ? renderMath(editing.value) : null;

  const toolBtn =
    "rounded-md px-2 py-1.5 text-xs font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-40";

  return (
    <div className="fixed inset-0 flex h-screen w-screen flex-col bg-pnp-gray-50 text-pnp-gray-900">
      {/* Top bar */}
      <div className="relative z-10 flex shrink-0 items-center justify-between border-b-2 border-pnp-navy bg-pnp-yellow px-4 py-2">
        <Link
          href="/math"
          className="inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-sm font-semibold text-pnp-navy transition-colors hover:bg-pnp-yellow-dark"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to Math
        </Link>

        <div className="flex items-center gap-2 text-sm">
          <span className="hidden text-pnp-navy/70 2xl:inline">
            Right-click a piece for options &middot; scroll or right-click+drag moves the board &middot; pinch or Ctrl+scroll zooms
          </span>

          {importError && (
            <span className="hidden text-xs font-medium text-pnp-orange sm:inline">{importError}</span>
          )}

          {/* Undo / redo */}
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={undo}
              disabled={!canUndo}
              title="Undo (Ctrl+Z)"
              aria-label="Undo"
              className={`${toolBtn} text-pnp-navy hover:bg-pnp-yellow-dark`}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M3 7v6h6" />
                <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13" />
              </svg>
            </button>
            <button
              type="button"
              onClick={redo}
              disabled={!canRedo}
              title="Redo (Ctrl+Shift+Z)"
              aria-label="Redo"
              className={`${toolBtn} text-pnp-navy hover:bg-pnp-yellow-dark`}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M21 7v6h-6" />
                <path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7" />
              </svg>
            </button>
          </div>

          {/* Canvas background switcher */}
          <div
            className="hidden items-center gap-0.5 rounded-md border-2 border-pnp-navy bg-white p-0.5 shadow-[2px_2px_0_var(--pnp-navy)] sm:flex"
            role="group"
            aria-label="Canvas background"
          >
            {BG_OPTIONS.map((o) => (
              <button
                key={o.key}
                type="button"
                onClick={() => setBackground(o.key)}
                title={o.label}
                aria-label={o.label}
                aria-pressed={background === o.key}
                className={`flex h-8 w-8 items-center justify-center rounded transition-colors ${
                  background === o.key
                    ? "bg-pnp-navy text-white"
                    : "text-pnp-gray-600 hover:bg-pnp-gray-100 hover:text-pnp-navy"
                }`}
              >
                {o.icon}
              </button>
            ))}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,image/*"
            multiple
            className="hidden"
            onChange={onFilesChosen}
          />

          {pages.length > 0 && (
            <button
              type="button"
              onClick={removeImport}
              title="Remove imported pages"
              className={`${toolBtn} text-pnp-navy hover:bg-pnp-yellow-dark`}
            >
              Remove import
            </button>
          )}

          <Button
            tier="secondary"
            size="small"
            onClick={onImportClick}
            disabled={importing}
            title="Draw on a PDF or image"
          >
            {importing ? "Importing…" : "Import PDF / image"}
          </Button>

          <Button
            tier="secondary"
            size="small"
            onClick={savePdf}
            disabled={items.length === 0 && strokes.length === 0 && pages.length === 0}
            title="Save the board as a PDF (choose “Save as PDF” in the print dialog)"
          >
            Save PDF
          </Button>

          <Button
            tier="secondary"
            size="small"
            onClick={() => setGridSnap((g) => !g)}
            aria-pressed={gridSnap}
            title="Toggle snap-to-grid"
          >
            {gridSnap ? "Snap: on" : "Snap: off"}
          </Button>
          <Button tier="secondary" size="small" onClick={cv.resetView} title="Reset the view">
            Reset view
          </Button>
          <Button tier="secondary" size="small" onClick={clearAll} title="Remove every piece and stroke">
            Clear board
          </Button>
        </div>
      </div>

      {/* Tray + canvas */}
      <div className="flex min-h-0 flex-1">
        <Tray onAdd={addFromTray} open={trayOpen} onToggle={() => setTrayOpen((o) => !o)} />
        <div className="relative min-w-0 flex-1">
          <svg
            ref={svgRef}
            className="absolute inset-0 h-full w-full touch-none select-none"
            style={{ cursor }}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={onPointerUp}
            onContextMenu={onContextMenu}
            onDoubleClick={onDoubleClick}
          >
            {/* Backdrop pattern, world-anchored via patternTransform so it
                scrolls and scales with the camera. */}
            {background !== "blank" && (
              <defs>
                <pattern
                  id="pnp-canvas-bg"
                  width={GRID}
                  height={GRID}
                  patternUnits="userSpaceOnUse"
                  patternTransform={`translate(${cam.tx} ${cam.ty}) scale(${cam.zoom})`}
                >
                  {background === "dots" ? (
                    <circle cx={0} cy={0} r={1} fill="var(--pnp-gray-300)" />
                  ) : (
                    // Top + left edge of each cell = a continuous square grid.
                    <path d={`M ${GRID} 0 L 0 0 0 ${GRID}`} fill="none" stroke="var(--pnp-gray-200)" strokeWidth={1} />
                  )}
                </pattern>
              </defs>
            )}
            {background !== "blank" && (
              <rect x={0} y={0} width="100%" height="100%" fill="url(#pnp-canvas-bg)" pointerEvents="none" />
            )}
            {/* Bold axes through the world origin for coordinate mode. Screen
                position of world (0,0) is exactly the camera translation. */}
            {background === "coordinate" && (
              <g stroke="var(--pnp-gray-400)" strokeWidth={1.5} pointerEvents="none">
                <line x1={cam.tx} y1={-100000} x2={cam.tx} y2={100000} />
                <line x1={-100000} y1={cam.ty} x2={100000} y2={cam.ty} />
              </g>
            )}

            <g ref={sceneRef} transform={`translate(${cam.tx} ${cam.ty}) scale(${cam.zoom})`}>
              {/* Imported PDF pages / images sit behind everything in world
                  space, so they pan and zoom locked to the board. */}
              {pages.map((img) => (
                <image
                  key={img.id}
                  href={img.href}
                  x={img.x}
                  y={img.y}
                  width={img.width}
                  height={img.height}
                  preserveAspectRatio="none"
                />
              ))}

              {[...items]
                .sort((a, b) => a.z - b.z)
                .map((it) => {
                  const isSel = selection.has(it.id);
                  const dx = isSel && dragging ? dragRef.current!.dx + dragRef.current!.snapDx : 0;
                  const dy = isSel && dragging ? dragRef.current!.dy + dragRef.current!.snapDy : 0;
                  const rotItem = isSel && rotating ? { ...it, rot: it.rot + rotateRef.current!.delta } : it;
                  return (
                    <ItemView
                      key={it.id}
                      item={rotItem}
                      selected={isSel}
                      dx={dx}
                      dy={dy}
                      outline={1.5 * scale}
                      fx={fx && fx.itemId === it.id ? fx : null}
                    />
                  );
                })}

              {/* Ink renders above the pieces so annotations always show;
                  pointerEvents none so strokes never block item hits. */}
              <g pointerEvents="none">
                {strokes.filter((s) => s.kind !== "text").map((s) => (
                  <StrokeShape key={s.id} item={s} nonScaling />
                ))}
                {previewStroke && <StrokeShape item={previewStroke} nonScaling />}
              </g>

              {/* Text labels ARE interactive in select mode: click to box
                  them, click again to type, drag to move, corner circle to
                  resize. A transparent rect sized from the font metrics
                  gives each label a generous hit area. */}
              {strokes.filter((s) => s.kind === "text").map((s) => {
                // The label being re-typed is hidden — the inline caret /
                // dock preview stands in for it until commit.
                if (editing?.existing && editing.id === s.id) return null;
                const [pt] = pointsToList(s.points);
                if (!pt) return null;
                const ts = textScaleRef.current;
                const scaling = modeRef.current === "textscale" && ts && ts.id === s.id;
                const fs = scaling ? ts.fs : (s.fontSize ?? TEXT_FONT_WORLD);
                const hitW = Math.max(fs, (s.text?.length ?? 1) * fs * 0.6);
                const hitH = fs * 1.3;
                const td = textDragRef.current;
                const dragging = modeRef.current === "textdrag" && td && td.id === s.id;
                const isSelected = selectedTextId === s.id && tool === "select";
                return (
                  <g
                    key={s.id}
                    data-stroke-id={s.id}
                    transform={dragging ? `translate(${td.dx} ${td.dy})` : undefined}
                    pointerEvents={tool === "select" || tool === "text" ? "auto" : "none"}
                    style={{ cursor: tool === "select" ? "move" : tool === "text" ? "text" : undefined }}
                  >
                    <rect x={pt[0] - 4} y={pt[1] - 4} width={hitW + 8} height={hitH + 8} fill="transparent" />
                    <StrokeShape
                      item={scaling ? { ...s, fontSize: fs } : s}
                      nonScaling
                      mathHtml={s.isMath ? renderMath(s.text ?? "") : null}
                    />
                    {isSelected && (
                      <>
                        <rect
                          x={pt[0] - 4}
                          y={pt[1] - 4}
                          width={hitW + 8}
                          height={hitH + 8}
                          fill="none"
                          stroke="var(--pnp-accent)"
                          strokeWidth={1.5 * scale}
                          strokeDasharray={`${5 * scale} ${4 * scale}`}
                        />
                        {/* Corner circle — drag to grow/shrink the font.
                            The visible dot rides on a much larger invisible
                            hit circle so it's easy to grab with a mouse. */}
                        <circle
                          cx={pt[0] + hitW + 4}
                          cy={pt[1] + hitH + 4}
                          r={9 * scale}
                          fill="var(--pnp-accent)"
                          stroke="white"
                          strokeWidth={2 * scale}
                          pointerEvents="none"
                        />
                        <circle
                          data-text-scale="true"
                          cx={pt[0] + hitW + 4}
                          cy={pt[1] + hitH + 4}
                          r={22 * scale}
                          fill="transparent"
                          style={{ cursor: "nwse-resize" }}
                        />
                      </>
                    )}
                  </g>
                );
              })}

              {/* Inline caret for a plain-text label being typed: a real
                  contentEditable in world space, so the cursor blinks right
                  on the board and the text scales with zoom. */}
              {editing && !editing.isMath && (
                <foreignObject
                  x={editing.wx - 4}
                  y={editing.wy - 4}
                  width={2400}
                  height={editing.fontSize * 2 + 8}
                  style={{ overflow: "visible" }}
                >
                  <div
                    ref={inlineRef}
                    contentEditable
                    suppressContentEditableWarning
                    role="textbox"
                    aria-label="Type a label"
                    style={{
                      display: "inline-block",
                      minWidth: "10px",
                      padding: "4px",
                      fontSize: editing.fontSize,
                      lineHeight: 1.2,
                      color: editing.color,
                      caretColor: editing.color,
                      outline: "none",
                      whiteSpace: "pre",
                      fontFamily: "var(--font-sans, system-ui, sans-serif)",
                      border: "1.5px dashed var(--pnp-accent)",
                      borderRadius: "4px",
                      background: "transparent",
                      // The SVG canvas is `select-none`; a contentEditable
                      // that inherits user-select:none can't take a caret,
                      // so re-enable selection explicitly.
                      userSelect: "text",
                      WebkitUserSelect: "text",
                      // And make sure the browser routes pointer/keyboard
                      // to the editor rather than the canvas gestures.
                      touchAction: "auto",
                    }}
                    onPointerDown={(e) => e.stopPropagation()}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        commitText();
                      } else if (e.key === "Escape") {
                        e.preventDefault();
                        cancelEdit();
                      }
                      e.stopPropagation();
                    }}
                    onBlur={commitText}
                  />
                </foreignObject>
              )}

              {/* Live in-place preview while a math label is being typed in
                  the dock. */}
              {editing && editing.isMath && (
                <foreignObject
                  x={editing.wx - 4}
                  y={editing.wy - 4}
                  width={2400}
                  height={600}
                  style={{ overflow: "visible", pointerEvents: "none" }}
                >
                  <div
                    style={{
                      display: "inline-block",
                      minWidth: "10px",
                      minHeight: `${editing.fontSize}px`,
                      padding: "4px",
                      fontSize: editing.fontSize,
                      lineHeight: 1.2,
                      color: editing.color,
                      whiteSpace: "nowrap",
                      border: "1.5px dashed var(--pnp-accent)",
                      borderRadius: "4px",
                    }}
                    dangerouslySetInnerHTML={{
                      __html:
                        (editing.value.trim() && renderMath(editing.value)) ||
                        `<span style="opacity:.4">${editing.value.trim() ? "…" : "math"}</span>`,
                    }}
                  />
                </foreignObject>
              )}

              {selBBox && !marquee && tool === "select" && (
                <SelectionOverlay
                  bbox={selBBox}
                  scale={scale}
                  onDelete={deleteSelected}
                  onDuplicate={duplicateSelected}
                  onRotateStart={onRotateStart}
                />
              )}

              {marquee && (
                <rect
                  x={Math.min(marquee.x1, marquee.x2)}
                  y={Math.min(marquee.y1, marquee.y2)}
                  width={Math.abs(marquee.x2 - marquee.x1)}
                  height={Math.abs(marquee.y2 - marquee.y1)}
                  fill="var(--pnp-accent)"
                  fillOpacity={0.08}
                  stroke="var(--pnp-accent)"
                  strokeWidth={scale}
                  pointerEvents="none"
                />
              )}
            </g>
          </svg>

          {menu && menuItem && (
            <ContextMenu
              x={menu.x}
              y={menu.y}
              item={menuItem}
              onFlip={() => {
                flipItem(menu.itemId);
                setMenu(null);
              }}
              onTint={(t) => {
                tintItem(menu.itemId, t);
                setMenu(null);
              }}
              onDuplicate={() => {
                duplicateOne(menu.itemId);
                setMenu(null);
              }}
              onBringToFront={() => {
                bringToFront(menu.itemId);
                setMenu(null);
              }}
              onDelete={() => {
                deleteOne(menu.itemId);
                setMenu(null);
              }}
              onClose={() => setMenu(null)}
            />
          )}

          {/* Right-click menu for a text label: colour + font size. */}
          {textMenu && textMenuStroke && (
            <div
              className="absolute z-40 flex w-56 flex-col gap-2 rounded-lg border-2 border-pnp-navy bg-white p-2.5 shadow-[3px_3px_0_var(--pnp-navy)]"
              style={{
                left: Math.min(textMenu.x, (svgRef.current?.clientWidth ?? 600) - 240),
                top: Math.min(textMenu.y, (svgRef.current?.clientHeight ?? 400) - 140),
              }}
              onPointerDown={(e) => e.stopPropagation()}
              onContextMenu={(e) => e.preventDefault()}
            >
              {/* Colour swatches */}
              <div className="flex items-center gap-1.5">
                {PEN_COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => mutateTextStroke(textMenuStroke.id, { color: c })}
                    title="Colour"
                    aria-label={`Text colour ${c}`}
                    className={`h-6 w-6 rounded-full border-2 transition-all ${
                      textMenuStroke.color === c ? "border-pnp-navy scale-110" : "border-pnp-gray-200 hover:scale-105"
                    }`}
                    style={{ backgroundColor: c }}
                  />
                ))}
                <button
                  type="button"
                  onClick={() => deleteTextStroke(textMenuStroke.id)}
                  title="Delete text"
                  className="ml-auto rounded-md px-2 py-1 text-xs font-semibold text-pnp-gray-600 hover:bg-pnp-gray-100 hover:text-pnp-navy"
                >
                  Delete
                </button>
              </div>
              {/* Font size slider */}
              <div className="flex items-center gap-2">
                <span className="text-[0.65rem] font-bold text-pnp-gray-500">A</span>
                <input
                  type="range"
                  min={14}
                  max={96}
                  step={2}
                  value={textMenuStroke.fontSize ?? TEXT_FONT_WORLD}
                  onChange={(e) => mutateTextStroke(textMenuStroke.id, { fontSize: Number(e.target.value) })}
                  aria-label="Font size"
                  className="w-full accent-[var(--pnp-accent)]"
                />
                <span className="text-base font-bold text-pnp-gray-500">A</span>
                <span className="w-7 text-right text-xs tabular-nums text-pnp-gray-600">
                  {textMenuStroke.fontSize ?? TEXT_FONT_WORLD}
                </span>
              </div>
            </div>
          )}

          {loaded && items.length === 0 && strokes.length === 0 && pages.length === 0 && (
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <p className="font-heading text-lg font-bold text-pnp-gray-300">
                {trayOpen
                  ? "Click a manipulative on the left to place it here"
                  : "Pick a pen below, or open the manipulatives tray on the left"}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Floating tool palette — bottom centre, above the canvas. */}
      <div
        className="fixed bottom-6 left-1/2 z-[230] flex -translate-x-1/2 items-center gap-1.5 rounded-full border-2 border-pnp-navy bg-white/95 px-2.5 py-2 shadow-[3px_3px_0_var(--pnp-navy)] backdrop-blur-md"
        onPointerDown={(e) => e.stopPropagation()}
      >
        <PaletteButton label="Select & move" active={tool === "select"} onClick={() => setTool("select")}>
          <SelectIcon />
        </PaletteButton>
        <PaletteButton label="Pen" active={tool === "pen"} onClick={() => setTool("pen")}>
          <PenIcon />
        </PaletteButton>
        <PaletteButton label="Highlighter" active={tool === "highlighter"} onClick={() => setTool("highlighter")}>
          <HighlighterIcon />
        </PaletteButton>
        <PaletteButton label="Eraser (ink only)" active={tool === "eraser"} onClick={() => setTool("eraser")}>
          <EraserIcon />
        </PaletteButton>

        <div className="mx-1 h-7 w-px bg-pnp-gray-200" />

        <PaletteButton label="Line (hold Shift to snap)" active={tool === "line"} onClick={() => setTool("line")}>
          <LineIcon />
        </PaletteButton>
        <PaletteButton label="Rectangle (hold Shift for square)" active={tool === "rect"} onClick={() => setTool("rect")}>
          <RectIcon />
        </PaletteButton>
        <PaletteButton label="Ellipse (hold Shift for circle)" active={tool === "ellipse"} onClick={() => setTool("ellipse")}>
          <EllipseIcon />
        </PaletteButton>
        <PaletteButton label="Text" active={tool === "text"} onClick={() => setTool("text")}>
          <TextIcon />
        </PaletteButton>

        <div className="mx-1 h-7 w-px bg-pnp-gray-200" />

        {PEN_COLORS.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => {
              setColor(c);
              // Colour applies to pen / shapes / text — the eraser and select
              // tool have no colour, so picking one switches to the pen.
              if (tool === "eraser" || tool === "select") setTool("pen");
            }}
            title="Colour"
            aria-label={`Pen colour ${c}`}
            className={`h-7 w-7 rounded-full border-2 transition-all ${
              color === c && tool !== "eraser" && tool !== "select"
                ? "border-pnp-navy scale-110"
                : "border-pnp-gray-200 hover:scale-105"
            }`}
            style={{ backgroundColor: c }}
          />
        ))}

        <div className="mx-1 h-7 w-px bg-pnp-gray-200" />

        <button
          type="button"
          onClick={clearInk}
          disabled={strokes.length === 0}
          title="Erase all ink (pieces stay)"
          className={`${toolBtn} text-pnp-gray-700 hover:bg-pnp-gray-100 hover:text-pnp-navy`}
        >
          Clear ink
        </button>
      </div>

      {/* Docked text controls while a label is being written: Text/Math
          toggle + symbol chips; in math mode it grows into the LaTeX
          editor, floating up above the tool palette. */}
      {editing && (
        <TextDock
          isMath={editing.isMath}
          value={editing.value}
          onChange={(v) => setEditing((prev) => (prev ? { ...prev, value: v } : prev))}
          onSetMath={setTextMode}
          onCommit={commitText}
          onCancel={cancelEdit}
          onInsertPlain={insertPlain}
          mathPreview={mathPreview}
          katexReady={!!katex}
        />
      )}
    </div>
  );
}

function PaletteButton({
  active,
  onClick,
  label,
  children,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={label}
      aria-label={label}
      aria-pressed={active}
      className={`flex h-9 w-9 items-center justify-center rounded-md border-2 transition-colors ${
        active
          ? "border-pnp-navy bg-pnp-navy/5 text-pnp-navy"
          : "border-transparent text-pnp-gray-500 hover:bg-pnp-gray-100 hover:text-pnp-navy"
      }`}
    >
      {children}
    </button>
  );
}

// ────────── icons ──────────

function SelectIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 3l7 18 2.5-7.5L21 11 4 3z" />
    </svg>
  );
}
function PenIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 19l7-7 3 3-7 7-3-3z" />
      <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" />
      <path d="M2 2l7.586 7.586" />
      <circle cx="11" cy="11" r="2" />
    </svg>
  );
}
function HighlighterIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 11l-6 6v3h3l6-6" />
      <path d="M22 12l-9 9" />
      <path d="M11 13l9-9 4 4-9 9-4-4z" fill="currentColor" fillOpacity="0.3" />
    </svg>
  );
}
function EraserIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 20H7L3 16a2 2 0 010-2.8L13 3.5a2 2 0 012.8 0L21 9a2 2 0 010 2.8L13 20" />
      <line x1="18" y1="13" x2="9" y2="22" />
    </svg>
  );
}
function LineIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <line x1="5" y1="19" x2="19" y2="5" />
    </svg>
  );
}
function RectIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round">
      <rect x="4" y="6" width="16" height="12" rx="1" />
    </svg>
  );
}
function EllipseIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <ellipse cx="12" cy="12" rx="9" ry="7" />
    </svg>
  );
}
function TextIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 6V5h14v1M12 5v14M9 19h6" />
    </svg>
  );
}
