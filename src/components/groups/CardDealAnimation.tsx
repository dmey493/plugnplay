"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { Student } from "@/lib/classes";

/**
 * Card-deal randomization animation — 3D version.
 *
 * What changed vs the prior 2D pass:
 *   - Real perspective camera looking down at a tabletop. The shuffle
 *     reads as cards on a real surface, not divs in a viewport.
 *   - Each card is a 3D group with a front plane and a back plane;
 *     rotating the group on Y reveals the face (no CSS flip hack).
 *   - Card textures are generated on a 2D canvas at mount and uploaded
 *     to the GPU as THREE.CanvasTextures — gives crisp text at any
 *     projection size with no SVG fonts to worry about.
 *   - All motion is per-frame lerping (useFrame). Each card carries its
 *     own "start position / target position / start time / delay" and
 *     interpolates with an eased curve, so the simultaneous riffle drop
 *     becomes a clean L/R/L/R cascade once delays are applied.
 *
 * What's the same:
 *   - The student → group assignment is decided upstream by the parent
 *     and passed in as `groups`. We never re-randomize here.
 *   - The orchestration is still the two-pass bridge shuffle:
 *     stack → split → arch → riffle → settle → split → arch → riffle
 *     → settle → deal → flip → group.
 *   - The Skip button at top-right jumps straight to onFinish.
 *
 * Coordinate system:
 *   - X right (+), Y up (+), Z out toward camera (+).
 *   - The tabletop is at y = 0. The camera looks slightly down from
 *     (0, 4, 7). Cards sit roughly at y = 0..1 during the shuffle and
 *     dip back to the table for the deal.
 *   - One world unit ≈ "one card width." Cards are 1.0 × 1.4 units.
 */

interface Props {
  groups: Student[][];
  onFinish: () => void;
  onSkip: () => void;
}

type CardPhase =
  | "stacked"
  | "split-1"
  | "bridge-1"
  | "riffle-1"
  | "between"
  | "split-2"
  | "bridge-2"
  | "riffle-2"
  | "dealing"
  | "dealt"
  | "flipped"
  | "grouped";

interface Card {
  id: string;
  name: string;
  groupIdx: number;
  posInGroup: number;
  deckIndex: number;
  half1: "L" | "R";
  rankInHalf1: number;
  half2: "L" | "R";
  rankInHalf2: number;
  riffleOrder1: number;
  riffleOrder2: number;
  dealOrder: number;
}

const GROUP_COLORS = [
  "#0d9488", // teal-600 (pnp-accent)
  "#f97316",
  "#0ea5e9",
  "#16a34a",
  "#dc2626",
  "#475569",
  "#facc15",
  "#3f42d9",
  "#ec4899",
];
const COL_FOR = (i: number) => GROUP_COLORS[i % GROUP_COLORS.length];

// Card dimensions (world units) — 5:7 ratio matches a real playing card.
const CARD_W = 1.0;
const CARD_H = 1.4;
// Two planes back-to-back, separated by this much on Z to prevent
// z-fighting. Small enough that the card still reads as thin.
const FACE_OFFSET = 0.003;

/** Fisher–Yates in-place. Cosmetic ordering only. */
function shuffleInPlace<T>(arr: T[]): void {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
}

// ─────────────────────────────────────────────────────────────────────
// Card texture generation
//
// Each card's front gets a unique canvas (group color band + student
// name). All cards share ONE back canvas — the back never changes
// between cards. Generating once at component mount + uploading as
// CanvasTextures keeps the per-frame cost effectively zero.
// ─────────────────────────────────────────────────────────────────────

const TEX_W = 256;
const TEX_H = 358; // matches CARD_W : CARD_H ratio

/** Build the shared "deck back" texture — deep teal field with a
 *  diamond lattice and a centre medallion. */
function makeBackTexture(): THREE.Texture {
  const c = document.createElement("canvas");
  c.width = TEX_W;
  c.height = TEX_H;
  const g = c.getContext("2d");
  if (!g) return new THREE.Texture();

  // Outer field
  g.fillStyle = "#0a3d4a";
  g.fillRect(0, 0, TEX_W, TEX_H);

  // White rim — drawn as a thin outline inset 5% from each edge.
  const inset = 14;
  g.strokeStyle = "rgba(255,255,255,0.85)";
  g.lineWidth = 2;
  g.strokeRect(inset, inset, TEX_W - inset * 2, TEX_H - inset * 2);

  // Inner field (slightly darker for contrast against rim)
  const ix = inset + 6;
  const iy = inset + 6;
  const iw = TEX_W - (inset + 6) * 2;
  const ih = TEX_H - (inset + 6) * 2;
  g.fillStyle = "#08323d";
  g.fillRect(ix, iy, iw, ih);

  // Diamond lattice — two crosshatched line sets at 45/-45 deg.
  g.save();
  g.beginPath();
  g.rect(ix, iy, iw, ih);
  g.clip();
  g.strokeStyle = "rgba(255,255,255,0.22)";
  g.lineWidth = 1;
  const step = 14;
  // forward slashes
  for (let x = ix - ih; x < ix + iw + ih; x += step) {
    g.beginPath();
    g.moveTo(x, iy);
    g.lineTo(x + ih, iy + ih);
    g.stroke();
  }
  // back slashes
  for (let x = ix - ih; x < ix + iw + ih; x += step) {
    g.beginPath();
    g.moveTo(x + ih, iy);
    g.lineTo(x, iy + ih);
    g.stroke();
  }
  g.restore();

  // Inner border around lattice
  g.strokeStyle = "rgba(255,255,255,0.45)";
  g.lineWidth = 1.5;
  g.strokeRect(ix, iy, iw, ih);

  // Centre medallion — teal radial gradient circle with PnP mark.
  const cx = TEX_W / 2;
  const cy = TEX_H / 2;
  const r = TEX_W * 0.17;
  const grad = g.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r);
  grad.addColorStop(0, "#14b8a6");
  grad.addColorStop(0.5, "#0d9488");
  grad.addColorStop(1, "#115e59");
  g.fillStyle = grad;
  g.beginPath();
  g.arc(cx, cy, r, 0, Math.PI * 2);
  g.fill();
  // medallion ring
  g.strokeStyle = "rgba(255,255,255,0.7)";
  g.lineWidth = 2;
  g.stroke();
  // text
  g.fillStyle = "#ffffff";
  g.font = `700 ${Math.round(r * 0.55)}px "Inter", system-ui, sans-serif`;
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillText("PnP", cx, cy + 2);

  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

/** Build a single card's front face: group-color band at top with the
 *  group number, student name below. */
function makeFrontTexture(name: string, groupIdx: number): THREE.Texture {
  const c = document.createElement("canvas");
  c.width = TEX_W;
  c.height = TEX_H;
  const g = c.getContext("2d");
  if (!g) return new THREE.Texture();

  // Card body
  g.fillStyle = "#ffffff";
  g.fillRect(0, 0, TEX_W, TEX_H);
  // Subtle border for definition
  g.strokeStyle = "rgba(15,23,42,0.15)";
  g.lineWidth = 2;
  g.strokeRect(1, 1, TEX_W - 2, TEX_H - 2);

  // Coloured band — top 40% of card.
  const bandH = TEX_H * 0.4;
  g.fillStyle = COL_FOR(groupIdx);
  g.fillRect(0, 0, TEX_W, bandH);

  // Group number in band
  g.fillStyle = "#ffffff";
  g.font = `800 ${Math.round(bandH * 0.6)}px "Inter", system-ui, sans-serif`;
  g.textAlign = "center";
  g.textBaseline = "middle";
  g.fillText(String(groupIdx + 1), TEX_W / 2, bandH / 2);

  // Student name — wrap on first space if needed so long names don't
  // overflow the bottom region.
  const nameRegionY = bandH;
  const nameRegionH = TEX_H - bandH;
  g.fillStyle = "#0f172a"; // pnp-navy
  const baseFontPx = Math.round(nameRegionH * 0.18);
  g.font = `700 ${baseFontPx}px "Inter", system-ui, sans-serif`;
  drawWrappedText(g, name, TEX_W / 2, nameRegionY + nameRegionH / 2, TEX_W - 28, baseFontPx * 1.1);

  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}

function drawWrappedText(
  g: CanvasRenderingContext2D,
  text: string,
  cx: number,
  cy: number,
  maxWidth: number,
  lineHeight: number
) {
  // Word-wrap by spaces, then centre the resulting lines vertically.
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let current = "";
  for (const w of words) {
    const next = current ? `${current} ${w}` : w;
    if (g.measureText(next).width <= maxWidth) current = next;
    else {
      if (current) lines.push(current);
      current = w;
    }
  }
  if (current) lines.push(current);
  const totalH = lines.length * lineHeight;
  let y = cy - totalH / 2 + lineHeight / 2;
  for (const line of lines) {
    g.fillText(line, cx, y);
    y += lineHeight;
  }
}

// ─────────────────────────────────────────────────────────────────────
// Phase → 3D target position/rotation math
//
// Returns a card's target in the scene given its current phase and
// shuffle-pass state. Position units are world-space; rotation is
// (x, y, z) Euler in radians.
// ─────────────────────────────────────────────────────────────────────

interface Target {
  pos: [number, number, number];
  rot: [number, number, number];
  /** Per-card transition delay (ms) layered on top of the global
   *  duration. Used to interleave the riffle drop. 0 for most phases. */
  delay: number;
  /** Total time (ms) this transition should take. */
  duration: number;
}

function computeTarget(args: {
  card: Card;
  phase: CardPhase;
  halfSize1: number;
  halfSize2: number;
  cards: Card[];
  groupCount: number;
}): Target {
  const { card, phase, halfSize1, halfSize2, cards, groupCount } = args;
  // Stack jitter — deterministic per-card tilt so the resting deck
  // doesn't look like a flat rectangle.
  const hash = stringHash(card.id);
  const jitterX = ((hash & 0xff) / 255 - 0.5) * 0.04;
  const jitterZRot = (((hash >> 8) & 0xff) / 255 - 0.5) * 0.06;
  // Each card sits slightly higher in the stack so the deck has depth.
  // Bottom of deck = lowest y; top = highest y.
  const stackY = 0.015 * card.deckIndex;

  switch (phase) {
    case "stacked":
    case "between":
      return {
        pos: [jitterX, stackY, 0],
        rot: [0, 0, jitterZRot],
        delay: 0,
        duration: 360,
      };
    case "split-1":
      return splitTarget(card, halfSize1, "first");
    case "bridge-1":
      return bridgeTarget(card, halfSize1, "first");
    case "riffle-1":
      return {
        pos: [jitterX, stackY, 0],
        rot: [0, 0, jitterZRot],
        delay: card.riffleOrder1 * 28,
        duration: 240,
      };
    case "split-2":
      return splitTarget(card, halfSize2, "second");
    case "bridge-2":
      return bridgeTarget(card, halfSize2, "second");
    case "riffle-2":
      return {
        pos: [jitterX, stackY, 0],
        rot: [0, 0, jitterZRot],
        delay: card.riffleOrder2 * 28,
        duration: 240,
      };
    case "dealing":
    case "dealt":
    case "flipped":
      return dealTarget(card, cards.length, phase === "flipped");
    case "grouped":
      return groupTarget(card, groupCount);
  }
}

function splitTarget(card: Card, halfSize: number, pass: "first" | "second"): Target {
  const half = pass === "first" ? card.half1 : card.half2;
  const rank = pass === "first" ? card.rankInHalf1 : card.rankInHalf2;
  // Centre each half vertically (in Y, i.e. card stacking dimension) so
  // 8-card and 30-card halves both feel balanced.
  const stackY = 0.015 * rank;
  // Halves sit symmetric about origin on X. A slight Z lean toward the
  // viewer makes them feel held above the table.
  const xCentre = half === "L" ? -1.05 : 1.05;
  // Each half tilts toward the centre of the table — like hands holding
  // two halves of a deck on either side.
  const yawTowardCentre = half === "L" ? 0.15 : -0.15;
  return {
    pos: [xCentre, stackY, 0.2],
    rot: [0, yawTowardCentre, 0],
    delay: 0,
    duration: 460,
  };
}

function bridgeTarget(card: Card, halfSize: number, pass: "first" | "second"): Target {
  const half = pass === "first" ? card.half1 : card.half2;
  const rank = pass === "first" ? card.rankInHalf1 : card.rankInHalf2;
  // t goes 0 (bottom of half) → 1 (top of half)
  const t = halfSize <= 1 ? 0 : rank / (halfSize - 1);
  // The arch lifts the top of each half. We bow the half toward the
  // other half — each card lives along an arc that goes from the base
  // (at split position) up and inward toward the centre.
  const baseX = half === "L" ? -1.05 : 1.05;
  // Inward sweep — top of each half travels toward x=0
  const inward = 0.9 * t;
  const x = half === "L" ? baseX + inward : baseX - inward;
  // Lift cards along the arch
  const lift = 0.45 * t + 0.05 * card.deckIndex * 0.0; // small linear lift
  const y = 0.015 * rank + lift;
  // Pull cards forward (toward camera) along the arch's top
  const z = 0.2 + 0.6 * t;
  // Cards tilt to follow the tangent of the arch — top cards lean
  // toward the opposite side.
  const tilt = (half === "L" ? -1 : 1) * 0.6 * t;
  // Pitch forward slightly so the face peeks downward (like a
  // bridge-shuffle bow).
  const pitch = 0.5 * t;
  return {
    pos: [x, y, z],
    rot: [pitch, half === "L" ? 0.15 + 0.1 * t : -0.15 - 0.1 * t, tilt],
    delay: 0,
    duration: 480,
  };
}

function dealTarget(card: Card, n: number, faceUp: boolean): Target {
  // With Euler order YXZ (set in CardMesh), yaw is applied around world
  // Y BEFORE pitch — so it spins the upright card on the spot without
  // affecting up/down, and pitch alone determines which face points up.
  //   pitch = −π/2  → body +Z (back texture) faces +Y (up)  ⇒ back up
  //   pitch = +π/2  → body −Z (front texture) faces +Y (up) ⇒ face up
  // The flip from dealt → flipped lerps pitch from −π/2 to +π/2, taking
  // the short way through 0 — the card visibly stands up momentarily
  // and then lays back down face-up, which reads as a real card flip.
  const angle = -Math.PI / 2 + (card.dealOrder / Math.max(n, 1)) * Math.PI * 2;
  const r = 2.4 + Math.min(0.8, n * 0.025);
  const x = Math.cos(angle) * r;
  const z = Math.sin(angle) * r * 0.7; // slight ellipse so the ring reads in perspective
  const y = 0.02; // just above the tabletop
  const pitch = faceUp ? Math.PI / 2 : -Math.PI / 2;
  // orientYaw spins the card on its centre so its top edge points
  // outward from the ring centre — purely cosmetic, like cards dealt
  // to seats around a table.
  const orientYaw = angle + Math.PI / 2;
  return {
    pos: [x, y, z],
    rot: [pitch, orientYaw, 0],
    delay: 0,
    duration: 380,
  };
}

function groupTarget(card: Card, groupCount: number): Target {
  // Lay out group clusters along the front of the table (small +Z) in
  // a single row, or two rows if there are too many groups.
  const perRow = Math.min(5, groupCount);
  const rows = Math.ceil(groupCount / perRow);
  const row = Math.floor(card.groupIdx / perRow);
  const col = card.groupIdx % perRow;
  const xSpan = 5.5;
  const xBase =
    perRow === 1
      ? 0
      : -xSpan / 2 + (col * xSpan) / (perRow - 1);
  const zBase = rows === 1 ? 1.6 : 1.0 + row * 1.6;
  // Within a group, fan the 3 (or 2) cards horizontally a touch so
  // each name stays readable.
  const slotDx = (card.posInGroup - 1) * 0.45;
  const slotRot = (card.posInGroup - 1) * 0.18;
  // pitch = +π/2 → face up (under YXZ order). yaw = 0 → top edge
  // points toward camera so the teacher reads the name upright.
  return {
    pos: [xBase + slotDx, 0.02 + card.posInGroup * 0.005, zBase],
    rot: [Math.PI / 2, 0, slotRot],
    delay: 0,
    duration: 700,
  };
}

function stringHash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return h;
}

// ─────────────────────────────────────────────────────────────────────
// Card component — one 3D group per student. Lerps from its previous
// position toward its current target each frame.
// ─────────────────────────────────────────────────────────────────────

function CardMesh({
  card,
  target,
  frontTexture,
  backTexture,
  phaseStartMs,
}: {
  card: Card;
  target: Target;
  frontTexture: THREE.Texture;
  backTexture: THREE.Texture;
  // Wall-clock ms when the current target became active. We use this to
  // compute elapsed time vs delay/duration each frame.
  phaseStartMs: number;
}) {
  const groupRef = useRef<THREE.Group>(null);
  // Snapshot of where the card was when the target last changed.
  // Updated only on target change so the lerp interpolates from a
  // stable origin instead of chasing the previous frame's value.
  const startPos = useRef<[number, number, number]>([0, 0, 0]);
  const startRot = useRef<[number, number, number]>([0, 0, 0]);
  const lastTargetRef = useRef<Target>(target);
  // Once-on-mount: switch the group's Euler order to YXZ so the yaw
  // around world Y is applied BEFORE the pitch. With the default XYZ
  // order the pitch comes first and the yaw is then interpreted in
  // the card's body frame — which (after pitch −π/2) turned out to be
  // a horizontal axis through the card, so half the dealt cards
  // ended up showing face and half showing back. YXZ keeps yaw as
  // "spin the upright card on its centre," which is what we want for
  // orienting the card around its ring seat. The Euler set() method
  // preserves whatever order is on the object, so subsequent rotation
  // updates via g.rotation.set(x, y, z) honour YXZ.
  useEffect(() => {
    if (groupRef.current) groupRef.current.rotation.order = "YXZ";
  }, []);

  // When the target changes, snapshot the current pose. The first time
  // (no group yet) we use the target itself as the start.
  if (lastTargetRef.current !== target) {
    const g = groupRef.current;
    if (g) {
      startPos.current = [g.position.x, g.position.y, g.position.z];
      startRot.current = [g.rotation.x, g.rotation.y, g.rotation.z];
    } else {
      startPos.current = target.pos;
      startRot.current = target.rot;
    }
    lastTargetRef.current = target;
  }

  useFrame(() => {
    const g = groupRef.current;
    if (!g) return;
    const now = performance.now();
    const elapsed = now - phaseStartMs - target.delay;
    const t = Math.max(0, Math.min(1, elapsed / target.duration));
    const eased = easeInOutCubic(t);
    g.position.set(
      lerp(startPos.current[0], target.pos[0], eased),
      lerp(startPos.current[1], target.pos[1], eased),
      lerp(startPos.current[2], target.pos[2], eased)
    );
    g.rotation.set(
      lerp(startRot.current[0], target.rot[0], eased),
      lerp(startRot.current[1], target.rot[1], eased),
      lerp(startRot.current[2], target.rot[2], eased)
    );
  });

  return (
    <group ref={groupRef} position={target.pos} rotation={target.rot}>
      {/* Plane at body +Z normal — visible to the camera at rest, so
          this is where the BACK texture goes. The deck reads as
          face-down at the start, just like a real deck of cards. */}
      <mesh position={[0, 0, FACE_OFFSET]} castShadow>
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshStandardMaterial
          map={backTexture}
          side={THREE.FrontSide}
          roughness={0.55}
          metalness={0.0}
        />
      </mesh>
      {/* Plane at body −Z normal — visible only when the card is
          flipped so its body −Z faces up. This is where the FRONT
          texture (group color band + student name) goes. */}
      <mesh
        position={[0, 0, -FACE_OFFSET]}
        rotation={[0, Math.PI, 0]}
        castShadow
      >
        <planeGeometry args={[CARD_W, CARD_H]} />
        <meshStandardMaterial
          map={frontTexture}
          side={THREE.FrontSide}
          roughness={0.65}
          metalness={0.0}
        />
      </mesh>
    </group>
  );
}

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}
function easeInOutCubic(t: number) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// ─────────────────────────────────────────────────────────────────────
// Top-level component
// ─────────────────────────────────────────────────────────────────────

export default function CardDealAnimation({ groups, onFinish, onSkip }: Props) {
  // Build the flat card list with all the shuffle-pass metadata.
  const cards = useMemo<Card[]>(() => {
    const flat: Omit<
      Card,
      | "deckIndex"
      | "half1"
      | "rankInHalf1"
      | "half2"
      | "rankInHalf2"
      | "riffleOrder1"
      | "riffleOrder2"
      | "dealOrder"
    >[] = [];
    groups.forEach((g, gi) => {
      g.forEach((s, si) => {
        flat.push({
          id: s.id,
          name: s.name,
          groupIdx: gi,
          posInGroup: si,
        });
      });
    });

    const deckOrder = flat.map((_, i) => i);
    shuffleInPlace(deckOrder);
    const splitAt = Math.ceil(deckOrder.length / 2);
    const splitFor = (deckPos: number): { half: "L" | "R"; rank: number } =>
      deckPos < splitAt
        ? { half: "L", rank: deckPos }
        : { half: "R", rank: deckPos - splitAt };
    const riffleOrderFor = (half: "L" | "R", rank: number) =>
      rank * 2 + (half === "R" ? 1 : 0);

    // Post-pass-1 order, derived analytically by walking the riffle.
    const postPass1: number[] = new Array(deckOrder.length);
    deckOrder.forEach((srcI, deckPos) => {
      const { half, rank } = splitFor(deckPos);
      postPass1[riffleOrderFor(half, rank)] = srcI;
    });

    const result: Card[] = flat.map((c, srcI) => {
      const deckPos1 = deckOrder.indexOf(srcI);
      const { half: half1, rank: rankInHalf1 } = splitFor(deckPos1);
      const deckPos2 = postPass1.indexOf(srcI);
      const { half: half2, rank: rankInHalf2 } = splitFor(deckPos2);
      return {
        ...c,
        deckIndex: deckPos1,
        half1,
        rankInHalf1,
        half2,
        rankInHalf2,
        riffleOrder1: riffleOrderFor(half1, rankInHalf1),
        riffleOrder2: riffleOrderFor(half2, rankInHalf2),
        dealOrder: 0,
      };
    });

    const idxs = result.map((_, i) => i);
    shuffleInPlace(idxs);
    idxs.forEach((srcI, dealI) => {
      result[srcI].dealOrder = dealI;
    });
    return result;
  }, [groups]);

  const halfSize1 = useMemo(() => {
    const ls = cards.filter((c) => c.half1 === "L").length;
    return Math.max(ls, cards.length - ls);
  }, [cards]);
  const halfSize2 = useMemo(() => {
    const ls = cards.filter((c) => c.half2 === "L").length;
    return Math.max(ls, cards.length - ls);
  }, [cards]);

  // Per-card phase. Most phase changes set every card; the deal phase
  // changes them one by one so the dealer reveal is staggered.
  const [phase, setPhase] = useState<Record<string, CardPhase>>(() =>
    Object.fromEntries(cards.map((c) => [c.id, "stacked" as CardPhase]))
  );
  // Wall-clock timestamp of when each card's current phase began.
  // Updated atomically with the phase change. Used to drive
  // useFrame's elapsed-vs-duration math.
  const [phaseStart, setPhaseStart] = useState<Record<string, number>>(() =>
    Object.fromEntries(cards.map((c) => [c.id, performance.now()]))
  );
  const [stage, setStage] = useState<
    "idle" | "shuffle" | "deal" | "reveal" | "group" | "done"
  >("idle");

  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);
  const cancelled = useRef(false);
  const after = (ms: number, fn: () => void) => {
    if (cancelled.current) return;
    timersRef.current.push(setTimeout(fn, ms));
  };

  const setPhaseAll = (p: CardPhase) => {
    const now = performance.now();
    setPhase((prev) => {
      const next: Record<string, CardPhase> = {};
      for (const id of Object.keys(prev)) next[id] = p;
      return next;
    });
    setPhaseStart((prev) => {
      const next: Record<string, number> = {};
      for (const id of Object.keys(prev)) next[id] = now;
      return next;
    });
  };

  const setOneCardPhase = (id: string, p: CardPhase) => {
    const now = performance.now();
    setPhase((prev) => ({ ...prev, [id]: p }));
    setPhaseStart((prev) => ({ ...prev, [id]: now }));
  };

  useEffect(() => {
    cancelled.current = false;
    setStage("shuffle");

    // Bridge x2 — same timing as the 2D version.
    after(200, () => setPhaseAll("split-1"));
    after(650, () => setPhaseAll("bridge-1"));
    after(1100, () => setPhaseAll("riffle-1"));
    after(2100, () => setPhaseAll("between"));
    after(2400, () => setPhaseAll("split-2"));
    after(2850, () => setPhaseAll("bridge-2"));
    after(3300, () => setPhaseAll("riffle-2"));
    after(4300, () => setPhaseAll("between"));

    const dealStart = 4500;
    const dealInterval = Math.max(60, Math.min(140, 2400 / Math.max(cards.length, 1)));
    after(dealStart, () => setStage("deal"));
    cards
      .slice()
      .sort((a, b) => a.dealOrder - b.dealOrder)
      .forEach((card, i) => {
        after(dealStart + i * dealInterval, () => setOneCardPhase(card.id, "dealing"));
        after(dealStart + i * dealInterval + 380, () => setOneCardPhase(card.id, "dealt"));
      });

    const dealEnd = dealStart + cards.length * dealInterval + 380;
    const flipStart = dealEnd + 350;
    after(flipStart, () => {
      setStage("reveal");
      setPhaseAll("flipped");
    });

    const groupStart = flipStart + 1000;
    after(groupStart, () => {
      setStage("group");
      setPhaseAll("grouped");
    });

    const doneAt = groupStart + 1400;
    after(doneAt, () => {
      setStage("done");
      onFinish();
    });

    return () => {
      cancelled.current = true;
      timersRef.current.forEach((t) => clearTimeout(t));
      timersRef.current = [];
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSkip = () => {
    cancelled.current = true;
    timersRef.current.forEach((t) => clearTimeout(t));
    timersRef.current = [];
    onSkip();
  };

  // Build textures once, memoized. One shared back, one front per card.
  const backTexture = useMemo(() => makeBackTexture(), []);
  const frontTextures = useMemo(() => {
    const map: Record<string, THREE.Texture> = {};
    for (const c of cards) {
      map[c.id] = makeFrontTexture(c.name, c.groupIdx);
    }
    return map;
  }, [cards]);

  // Dispose textures on unmount to keep the GPU clean across multiple
  // re-randomizations.
  useEffect(() => {
    return () => {
      backTexture.dispose();
      for (const t of Object.values(frontTextures)) t.dispose();
    };
  }, [backTexture, frontTextures]);

  // Compute current target per card on render. Cheap — pure math.
  const targets = useMemo(() => {
    const map: Record<string, Target> = {};
    for (const c of cards) {
      map[c.id] = computeTarget({
        card: c,
        phase: phase[c.id],
        halfSize1,
        halfSize2,
        cards,
        groupCount: groups.length,
      });
    }
    return map;
  }, [cards, phase, halfSize1, halfSize2, groups.length]);

  return (
    <section
      className="relative overflow-hidden bg-pnp-navy"
      style={{ minHeight: "calc(100vh - var(--header-h, 0px))" }}
    >
      <div className="relative h-[80vh] w-full">
        {/* Stage label */}
        <div className="pointer-events-none absolute left-1/2 top-6 z-20 -translate-x-1/2 text-center">
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-white/50">
            {stage === "shuffle" && "Shuffling…"}
            {stage === "deal" && "Dealing…"}
            {stage === "reveal" && "Reveal"}
            {stage === "group" && "Forming groups"}
            {stage === "done" && "Done"}
            {stage === "idle" && " "}
          </p>
        </div>

        <Canvas
          shadows
          camera={{ position: [0, 4.5, 6], fov: 38 }}
          gl={{ antialias: true }}
          style={{ background: "transparent" }}
        >
          {/* Lighting — ambient base + key directional from above-right
              + a softer fill on the opposite side. The key light
              casts the card shadows on the tabletop. */}
          <ambientLight intensity={0.55} />
          <directionalLight
            position={[4, 8, 4]}
            intensity={1.0}
            castShadow
            shadow-mapSize-width={1024}
            shadow-mapSize-height={1024}
            shadow-camera-left={-6}
            shadow-camera-right={6}
            shadow-camera-top={6}
            shadow-camera-bottom={-6}
          />
          <directionalLight position={[-3, 4, -2]} intensity={0.25} />

          {/* Tabletop — large plane that receives the cards' shadows.
              Slight dark navy felt to match the projection chrome
              without competing with the cards' colour bands. */}
          <mesh position={[0, -0.01, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
            <planeGeometry args={[24, 16]} />
            <meshStandardMaterial color="#0b1a3a" roughness={0.9} />
          </mesh>

          {/* Group target halos — soft coloured rings at each group's
              cluster position. Render only during/after the group
              phase so they appear as cards arrive. */}
          {(stage === "group" || stage === "done") &&
            groups.map((_, gi) => {
              const t = groupTarget(
                { ...({} as Card), groupIdx: gi, posInGroup: 0 } as Card,
                groups.length
              );
              return (
                <mesh
                  key={`halo-${gi}`}
                  position={[t.pos[0], 0.005, t.pos[2]]}
                  rotation={[-Math.PI / 2, 0, 0]}
                >
                  <ringGeometry args={[0.7, 0.78, 64]} />
                  <meshBasicMaterial color={COL_FOR(gi)} transparent opacity={0.55} />
                </mesh>
              );
            })}

          {cards.map((c) => (
            <CardMesh
              key={c.id}
              card={c}
              target={targets[c.id]}
              frontTexture={frontTextures[c.id]}
              backTexture={backTexture}
              phaseStartMs={phaseStart[c.id]}
            />
          ))}
        </Canvas>

        <button
          type="button"
          onClick={handleSkip}
          className="absolute right-6 top-6 z-30 rounded-md border border-white/20 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white/80 backdrop-blur transition-colors hover:bg-white/10 hover:text-white"
        >
          Skip animation
        </button>
      </div>
    </section>
  );
}
