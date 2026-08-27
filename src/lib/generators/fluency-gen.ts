/**
 * Fluency-practice problem generator: fractions (add/subtract) and decimals
 * (add/subtract). Pure functions — no DOM, no React. The UI is just a
 * client component that calls `generateProblems()` and renders the result.
 *
 * Difficulty bands for FRACTION problems are defined by how the denominators
 * relate:
 *   easy   — same denominator (no LCD needed)
 *   medium — one denominator divides the other (LCD = larger denom)
 *   hard   — coprime denominators (full LCD computation required)
 *
 * Difficulty bands for DECIMAL problems are defined by decimal places:
 *   easy   — 1 decimal place
 *   medium — 2 decimal places
 *   hard   — 3 decimal places (mixed lengths allowed)
 */

export type Difficulty = "easy" | "medium" | "hard";

export type FluencyTopic =
  | "add-fractions"
  | "subtract-fractions"
  | "multiply-fractions"
  | "divide-fractions"
  | "add-decimals"
  | "subtract-decimals"
  | "multiply-decimals"
  | "divide-decimals"
  // ----- Converting (rational number form conversions) -----
  | "frac-to-dec-term"      // proper/mixed fraction → terminating decimal
  | "frac-to-dec-rep"       // fraction → repeating decimal (bar notation)
  | "dec-to-frac-term"      // terminating decimal → simplified fraction
  | "dec-to-frac-rep"       // repeating decimal → fraction
  | "frac-to-percent"
  | "percent-to-frac"
  | "dec-to-percent"
  | "percent-to-dec"
  | "mixed-to-improper"
  | "improper-to-mixed"
  | "compare-rationals"     // compare two rationals in mixed forms
  | "order-rationals"       // order 4 rationals from least to greatest
  | "equivalent-forms"      // fill in the missing forms of a rational
  // ----- Equations: Tier 1 — One-Step (6.AF.3) -----
  | "eq-one-add"            // x + a = b
  | "eq-one-sub"            // x − a = b
  | "eq-one-mul"            // ax = b
  | "eq-one-div"            // x/a = b
  | "eq-one-mixed"          // random mix of the four
  // ----- Equations: Tier 2 — Two-Step (7.AF.3) -----
  | "eq-two-pos"            // ax + b = c (positive coefficients)
  | "eq-two-neg"            // ax + b = c with negatives
  | "eq-two-rational"       // ax + b = c with fractional/decimal coefficients
  | "eq-two-dist"           // p(x + q) = r
  // ----- Equations: Tier 3 — Multi-Step (8.AF.1) -----
  | "eq-multi-combine"      // combine like terms first
  | "eq-multi-dist"         // distributive then solve
  | "eq-multi-both"         // variables on both sides
  | "eq-multi-full"         // distributive + variables on both sides + combine
  | "eq-multi-special"      // no solution / infinitely many
  // ----- Equations: Tier 4 — Literal -----
  | "eq-literal"            // solve a formula for a specified variable
  // ----- Equations: Tier 5 — Proportions -----
  | "eq-prop"               // a/b = c/x
  | "eq-prop-word"          // proportional word problem
  // ----- Equations: Tier 6 — Absolute Value -----
  | "eq-abs-simple"         // |x + a| = b
  | "eq-abs-coef"           // |ax + b| = c
  | "eq-abs-isolate"        // c|ax + b| + d = e
  // ----- Equations: Tier 7 — Systems -----
  | "eq-sys-sub"            // solve by substitution
  | "eq-sys-elim"           // solve by elimination
  | "eq-sys-special"        // no solution / infinitely many
  | "eq-sys-word"           // system-style word problem
  // ----- Equations: Tier 8 — Quadratics -----
  | "eq-quad-sqrt"          // x² = c
  | "eq-quad-trans"         // (x − h)² = k
  | "eq-quad-fac-a1"        // x² + bx + c = 0 (factor)
  | "eq-quad-fac-an"        // ax² + bx + c = 0 (factor, a > 1)
  | "eq-quad-diff"          // a²x² − b² = 0
  | "eq-quad-formula"       // quadratic formula
  | "eq-quad-complete"      // completing the square
  // ----- Equations: Tier 9 — Radicals -----
  | "eq-rad-single"         // √(ax + b) = c
  | "eq-rad-double"         // √(ax + b) = √(cx + d)
  | "eq-rad-linear"         // √(x + a) = x − b (check extraneous)
  // ----- Equations: Tier 10 — Rationals -----
  | "eq-rat-simple"         // a/x = b
  | "eq-rat-linear"         // (ax + b)/c = d
  | "eq-rat-lcd"            // 1/x + p/q = r style
  // ----- Equations: Tier 11 — Exponential -----
  | "eq-exp-bases"          // solve via matching bases
  // ----- Inequalities: Tier 1 — One-Step (6.AF.4) -----
  | "ineq-one-add"          // x + a (op) b
  | "ineq-one-sub"          // x − a (op) b
  | "ineq-one-mul"          // ax (op) b  (negative a forces flip)
  | "ineq-one-div"          // x/a (op) b
  | "ineq-one-mixed"        // mixed one-step
  // ----- Inequalities: Tier 2 — Two-Step (7.AF.4) -----
  | "ineq-two-pos"          // ax + b (op) c, positive a
  | "ineq-two-neg"          // ax + b (op) c with negative a (flip required)
  | "ineq-two-rational"     // rational coefficients
  | "ineq-two-dist"         // p(x + q) (op) r
  // ----- Inequalities: Tier 3 — Multi-Step (8.AF.1) -----
  | "ineq-multi-combine"    // combine like terms first
  | "ineq-multi-dist"       // distributive then solve
  | "ineq-multi-both"       // variables on both sides
  | "ineq-multi-full"       // distributive + both sides + combine
  | "ineq-multi-special"    // no solution / all real numbers
  // ----- Inequalities: Tier 4 — Compound (Algebra 1) -----
  | "ineq-compound-and"     // a < x + b < c
  | "ineq-compound-or"      // x + a < b OR x + a > c
  | "ineq-compound-translate" // translate a verbal phrase to a compound inequality
  // ----- Inequalities: Tier 5 — Absolute Value (Algebra 1) -----
  | "ineq-abs-less"         // |x + a| < b (AND form)
  | "ineq-abs-greater"      // |x + a| > b (OR form)
  | "ineq-abs-isolate"      // c|ax + b| + d (op) e (isolate first)
  // ----- Geometry: Tier 1 — Area & Perimeter (forward) -----
  | "geo-rect-area"
  | "geo-rect-perim"
  | "geo-square"            // randomly area or perimeter
  | "geo-tri-area"
  | "geo-parallelogram-area"
  | "geo-trap-area"
  | "geo-circle-area"
  | "geo-circle-circumference"
  // ----- Geometry: Tier 2 — Find Missing Dimension (reverse) -----
  | "geo-rect-find-area"    // given area + one side → find other side
  | "geo-rect-find-perim"   // given perimeter + one side → find other side
  | "geo-square-find"       // given area or perimeter → find side
  | "geo-tri-find-base"     // given area + height → find base
  | "geo-tri-find-height"   // given area + base → find height
  | "geo-circle-find-r-area"  // given area → find radius
  | "geo-circle-find-r-circ" // given circumference → find radius
  // ----- Geometry: Tier 3 — Volume & Surface Area (forward) -----
  | "geo-rect-prism-v"
  | "geo-rect-prism-sa"
  | "geo-cube"               // randomly volume or surface area
  | "geo-tri-prism-v"
  | "geo-tri-prism-sa"
  | "geo-cylinder-v"
  | "geo-cylinder-sa"
  | "geo-cone-v"
  | "geo-sphere-v"
  | "geo-pyramid-v"
  // ----- Geometry: Tier 4 — Find Missing Dim from Volume / SA -----
  | "geo-rect-prism-find-h"  // given V + l + w → find h
  | "geo-cube-find-s"        // given V or SA → find side
  | "geo-cylinder-find-h"    // given V + r → find h
  | "geo-cylinder-find-r"    // given V + h → find r
  | "geo-cone-find-h"        // given V + r → find h
  | "geo-sphere-find-r"      // given V → find r
  // ----- Geometry: Tier 5 — Pythagorean Theorem -----
  | "geo-pyth-hyp"           // given legs a, b → find c
  | "geo-pyth-leg"           // given hypotenuse + one leg → find other leg
  | "geo-pyth-check"         // is the triangle right? (check a² + b² ?= c²)
  | "geo-pyth-word"          // real-world Pythagorean (ladder, distance, screen)
  // ----- Geometry: Tier 6 — Coordinate Geometry -----
  | "geo-coord-distance"     // distance between two points
  | "geo-coord-midpoint"     // midpoint of a segment
  | "geo-coord-slope"        // slope through two points (moved to Graphing & Rates)
  // ----- Graphing & Rates: Tier 1 — Rates & Unit Rates -----
  | "gr-unit-rate"           // find a unit rate from a ratio
  | "gr-rate-table"          // complete a table keeping rate constant
  | "gr-rate-convert"        // convert rate units (mph ↔ ft/sec, etc.)
  // ----- Graphing & Rates: Tier 2 — Proportional Relationships -----
  | "gr-prop-k-table"        // find constant of proportionality from a table
  | "gr-prop-k-graph"        // find k from a graph
  | "gr-prop-equation"       // write y = kx from a table
  | "gr-prop-table-yn"       // is this table proportional? yes/no
  | "gr-prop-graph-yn"       // is this graph proportional? yes/no
  // ----- Graphing & Rates: Tier 3 — Slope from Two Points -----
  | "gr-slope-points"        // slope from two points (replaces geo-coord-slope)
  | "gr-slope-graph"         // slope from a graph
  | "gr-slope-table"         // slope from a table
  | "gr-slope-verbal"        // slope from a verbal description
  | "gr-slope-classify"      // classify pos / neg / zero / undefined
  // ----- Graphing & Rates: Tier 4 — Slope-Intercept Form -----
  | "gr-si-identify"         // identify m and b from y = mx + b
  | "gr-si-mb"               // write y = mx + b given slope and intercept
  | "gr-si-mp"               // write y = mx + b given slope and a point
  | "gr-si-pp"               // write y = mx + b given two points
  | "gr-si-graph"            // write y = mx + b from a graph
  // ----- Graphing & Rates: Tier 5 — Point-Slope & Standard Forms -----
  | "gr-std-to-si"           // standard → slope-intercept
  | "gr-si-to-std"           // slope-intercept → standard
  | "gr-ps-write"            // write in point-slope form
  | "gr-ps-to-si"            // point-slope → slope-intercept
  // ----- Graphing & Rates: Tier 6 — Graphing Lines -----
  | "gr-graph-si"            // plot from y = mx + b
  | "gr-graph-table"         // plot from a table
  | "gr-graph-std"           // plot from standard form
  | "gr-graph-points"        // plot from two points
  // ----- Graphing & Rates: Tier 9 — Functions on the Coordinate Plane -----
  | "gr-fn-vlt-graph"        // vertical line test from a graph
  | "gr-fn-table"            // function from a table / mapping
  | "gr-fn-eval"             // evaluate f(x) for a given x
  | "gr-fn-reverse"          // find x given f(x)
  | "gr-fn-domain-range"     // domain & range from a graph
  // ----- Graphing & Rates: Tier 10 — Non-Linear & Comparison -----
  | "gr-nonlinear-classify"  // linear vs nonlinear from a table
  | "gr-rate-compare"        // compare two rates
  | "gr-linear-compare"      // compare two linear models
  // ----- Integer Operations (7.NS.1-4) -----
  // Signed-integer drill across the four operations. Difficulty bands:
  //   easy   : single-digit operands, |x| ≤ 9
  //   medium : |x| ≤ 20, both signed
  //   hard   : |x| ≤ 99, both signed, includes division with non-trivial
  //            quotients
  | "add-integers"
  | "subtract-integers"
  | "multiply-integers"
  | "divide-integers"
  | "integer-mixed"          // random mix of the four operations
  // ----- Rational Operations (7.NS.7) -----
  // Signed fraction drill across +, −, ×, ÷. Uses the existing fraction
  // generators internally with `allowNegatives` forced on, so all of the
  // fraction format toggles (proper / mixed / improper / whole) still
  // apply. Distinct from plain fraction topics because the negative is
  // baked in — no toggle, parentheses on every negative operand.
  | "add-rationals"
  | "subtract-rationals"
  | "multiply-rationals"
  | "divide-rationals"
  | "rational-mixed"          // random mix of the four operations
  // ----- Number Theory (Indiana 7.NS.5 / 7.NS.6) -----
  | "prime-factorization"     // factor a whole number into primes with exponents
  | "perfect-square-roots"    // √n for perfect-square n
  // ----- Percent Applications (7.RP.2) -----
  | "percent-of-change"       // % change from old → new value
  | "percent-application"     // tax / tip / markup / discount as final price
  | "simple-interest"         // I = Prt
  // ----- Algebraic Expressions (7.AF.1) -----
  | "combine-like-terms"      // simplify an expression to ax + b form
  | "distribute-expand"       // apply distributive property: a(bx ± c) → abx ± ac
  | "distribute-combine";     // distribute and combine like terms across multiple groups

export interface FractionFormatToggles {
  /** Proper fractions: numerator < denominator (e.g., 3/4). */
  proper: boolean;
  /** Whole numbers (e.g., 3, 7). Stored internally as num/1. */
  whole: boolean;
  /** Mixed numbers (e.g., 2 1/4). Stored internally as improper, displayed as mixed. */
  mixed: boolean;
  /** Improper fractions (e.g., 7/4). */
  improper: boolean;
}

export interface FluencyOptions {
  topic: FluencyTopic;
  difficulty: Difficulty;
  /** Only meaningful when topic is a fraction topic. */
  formats: FractionFormatToggles;
  /** Cap on denominators used for fraction problems (e.g., 12). */
  maxDenominator: number;
  /** Whether negatives are allowed in either operand. */
  allowNegatives: boolean;
  /** When true, answers display in simplest form. (We always simplify; this
   *  toggle currently signals "force problems that *need* simplifying", but
   *  v1 just always renders the simplified answer.) */
  requireSimplification: boolean;
  /** How many problems to generate (1–60 sensible). */
  count: number;
  /** Distribute topics only — mix unit-fraction outside coefficients
   *  (1/2, 1/3, 1/4, 1/5, 1/6) in alongside integers. Inside terms are
   *  forced to be divisible by the denominator so answers stay clean
   *  integers (e.g. (1/2)(4x + 6) = 2x + 3). */
  distributeIncludeFractions?: boolean;
  /** Distribute topics only — mix friendly-decimal outside coefficients
   *  (0.1, 0.2, 0.25, 0.5) in alongside integers. Inside terms are
   *  picked so answers come out to one decimal place at most. */
  distributeIncludeDecimals?: boolean;
  /** Rational-number topics only — mix in problems that pair a fraction
   *  with a decimal (e.g. 3/4 + 0.5, 1/2 × 0.6) using the topic's
   *  operation. Roughly a third of the worksheet when on. */
  rationalIncludeFracDec?: boolean;
}

/** Inline labeled-shape diagram for geometry problems. The worksheet
 *  renderer draws a small SVG for each shape kind with the supplied label
 *  positions. Labels are strings so an unknown side can be rendered as "x"
 *  or "?". */
export interface ShapeSpec {
  kind:
    | "rectangle"
    | "square"
    | "triangle"
    | "right-triangle"
    | "parallelogram"
    | "trapezoid"
    | "circle"
    | "rect-prism"
    | "cube"
    | "tri-prism"
    | "cylinder"
    | "cone"
    | "sphere"
    | "pyramid"
    | "grid"
    | "numberline";
  /** For kind === "numberline" — a horizontal number line. Inequality
   *  worksheets show a blank line for the student to graph on; the
   *  answer key fills in the boundary point(s) and shaded ray(s). */
  numberline?: {
    min: number;
    max: number;
    /** Label every `step` ticks (default 1; use 2 on wide ranges). */
    step?: number;
    /** Boundary circles: open (< / >) or closed (≤ / ≥). */
    points?: { x: number; open: boolean }[];
    /** Shaded pieces; "-inf" / "+inf" extend to the arrow ends. */
    segments?: { from: number | "-inf"; to: number | "+inf" }[];
  };
  /** For kind === "grid", carries the data needed to draw a coordinate
   *  grid with points, lines, or a curve. */
  grid?: {
    /** Axis range — defaults to 10 (covers −10 to +10). */
    range?: number;
    /** Points to mark on the grid. */
    points?: { x: number; y: number; label?: string }[];
    /** Straight lines, each from one point to another. */
    lines?: { x1: number; y1: number; x2: number; y2: number }[];
    /** A polyline curve drawn through these points (for non-linear fns). */
    curve?: [number, number][];
    /** Vertical lines at x = c for vertical-line-test demos. */
    verticals?: number[];
  };
  /** Map of label slot → text. Slot names depend on the shape:
   *    rectangle    → { length, width }
   *    square       → { side }
   *    triangle     → { base, height }     (height drawn as dashed)
   *    right-triangle → { a, b, c }        (a, b legs; c hypotenuse)
   *    parallelogram→ { base, height, side? }
   *    trapezoid    → { base1, base2, height }
   *    circle       → { radius?, diameter? }
   */
  labels: Record<string, string>;
}

export interface Problem {
  num: number;       // 1-based problem number
  display: string;   // e.g., "3/4 + 1/2" — what shows on the worksheet
  answer: string;    // e.g., "5/4" or "1 1/4" — what shows on the answer key
  /** Optional data table (x/y table). Rendered by the UI as a real
   *  bordered table instead of the old monospaced text approximation. */
  table?: { headers: string[]; rows: (string | number)[][] };
  /** Optional labeled-shape diagram drawn beside the problem text. */
  shape?: ShapeSpec;
  /** Optional shape variant for the answer key. Used when the worksheet
   *  should show a blank diagram (e.g., empty coordinate grid for graphing
   *  problems) but the answer key should show the solution drawn on it. */
  answerShape?: ShapeSpec;
  /** Optional shared instruction (e.g., "Find the area.") used by topics
   *  where every problem shares the same prompt. When every problem in a
   *  worksheet carries the same `instruction`, the worksheet renders it
   *  once between the header and the grid instead of next to every shape. */
  instruction?: string;
}

// ───────────────────── helpers ─────────────────────

function gcd(a: number, b: number): number {
  a = Math.abs(a);
  b = Math.abs(b);
  while (b) {
    [a, b] = [b, a % b];
  }
  return a || 1;
}

function lcm(a: number, b: number): number {
  return Math.abs(a * b) / gcd(a, b);
}

function simplify(num: number, den: number): [number, number] {
  if (den === 0) return [num, 0];
  const g = gcd(num, den);
  let n = num / g;
  let d = den / g;
  if (d < 0) {
    n = -n;
    d = -d;
  }
  return [n, d];
}

function rnd(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/** Render a signed (num/den) as a string. When `useMixed` and the value is
 *  improper, format as "W A/B" (with a single space). */
function fmtFraction(num: number, den: number, useMixed: boolean): string {
  if (den === 1 || den === 0) return String(num);
  if (useMixed && Math.abs(num) >= den) {
    const sign = num < 0 ? -1 : 1;
    const a = Math.abs(num);
    const whole = Math.floor(a / den);
    const remainder = a % den;
    const signedWhole = whole * sign;
    if (remainder === 0) return String(signedWhole);
    return `${signedWhole} ${remainder}/${den}`;
  }
  return `${num}/${den}`;
}

// ───────────────────── denominator pairing ─────────────────────

/** Pick two denominators matching the requested difficulty band. */
function denomPair(difficulty: Difficulty, max: number): [number, number] {
  if (difficulty === "easy") {
    const d = rnd(2, Math.max(2, max));
    return [d, d];
  }
  if (difficulty === "medium") {
    // One denom is a multiple of the other.
    for (let t = 0; t < 30; t++) {
      const d1 = rnd(2, Math.max(2, Math.floor(max / 2)));
      const k = rnd(2, Math.max(2, Math.floor(max / d1)));
      const d2 = d1 * k;
      if (d2 <= max && d1 !== d2) {
        return Math.random() < 0.5 ? [d1, d2] : [d2, d1];
      }
    }
    return [2, 4];
  }
  // hard: coprime small denominators
  for (let t = 0; t < 60; t++) {
    const d1 = rnd(2, max);
    const d2 = rnd(2, max);
    if (d1 !== d2 && gcd(d1, d2) === 1) return [d1, d2];
  }
  return [3, 4];
}

// ───────────────────── operand generation ─────────────────────

interface Operand {
  /** Signed numerator. For improper / mixed values, |num| can exceed den. */
  num: number;
  /** Positive denominator (1 for whole numbers). */
  den: number;
  /** Was this operand picked as a "mixed number" — affects display. */
  asMixed: boolean;
}

function makeOperand(den: number, opts: FluencyOptions): Operand {
  // Build the list of allowed formats. If nothing is on, fall back to
  // proper so we always produce *something*.
  const allowed = (["proper", "whole", "mixed", "improper"] as const).filter(
    (f) => opts.formats[f]
  );
  const choice =
    allowed.length === 0
      ? "proper"
      : allowed[Math.floor(Math.random() * allowed.length)];
  const sign = opts.allowNegatives && Math.random() < 0.5 ? -1 : 1;

  switch (choice) {
    case "whole":
      return { num: rnd(1, 9) * sign, den: 1, asMixed: false };
    case "proper":
      return { num: rnd(1, Math.max(1, den - 1)) * sign, den, asMixed: false };
    case "improper":
      return {
        num: rnd(den + 1, den * 4) * sign,
        den,
        asMixed: false,
      };
    case "mixed": {
      const whole = rnd(1, 9);
      const numer = rnd(1, Math.max(1, den - 1));
      return { num: (whole * den + numer) * sign, den, asMixed: true };
    }
  }
}

// ───────────────────── problem generators ─────────────────────

/** Wrap a rendered operand string in parens when its leading sign makes
 *  the math ambiguous (used for any negative). The "-" → "−" swap keeps
 *  the minus visually consistent with what we render elsewhere. */
function wrapNegative(s: string): string {
  return `(${s.replace("-", "−")})`;
}

function generateFractionAddSubProblem(opts: FluencyOptions, idx: number): Problem {
  const [d1, d2] = denomPair(opts.difficulty, opts.maxDenominator);
  const a = makeOperand(d1, opts);
  const b = makeOperand(d2, opts);

  const op = opts.topic === "add-fractions" ? 1 : -1;
  const commonDen = lcm(a.den, b.den);
  const aN = a.num * (commonDen / a.den);
  const bN = b.num * (commonDen / b.den) * op;
  let rNum = aN + bN;
  let rDen = commonDen;
  [rNum, rDen] = simplify(rNum, rDen);

  const aStr = fmtFraction(a.num, a.den, a.asMixed);
  const bStr = fmtFraction(b.num, b.den, b.asMixed);
  const opSym = opts.topic === "add-fractions" ? "+" : "−";
  const aDisplay = a.num < 0 ? wrapNegative(aStr) : aStr;
  const bDisplay = b.num < 0 ? wrapNegative(bStr) : bStr;
  const display = `${aDisplay} ${opSym} ${bDisplay}`;

  const wantsMixed = opts.formats.mixed;
  const answer = fmtFraction(rNum, rDen, wantsMixed);

  return { num: idx, display, answer };
}

/** Pick a denominator (1 for whole numbers) appropriate to difficulty. */
function denomSingle(difficulty: Difficulty, max: number): number {
  const lo = 2;
  const hi = difficulty === "easy" ? Math.min(6, max) : difficulty === "medium" ? Math.min(10, max) : max;
  return rnd(lo, Math.max(lo, hi));
}

function generateFractionMulDivProblem(opts: FluencyOptions, idx: number): Problem {
  // Multiply / divide don't need a common denominator, so we pick each
  // operand's denominator independently from the difficulty's range.
  const a = makeOperand(denomSingle(opts.difficulty, opts.maxDenominator), opts);
  let b = makeOperand(denomSingle(opts.difficulty, opts.maxDenominator), opts);
  // Avoid dividing by zero. makeOperand never returns 0 numerator, but
  // belt-and-suspenders.
  if (b.num === 0) b = { num: 1, den: b.den, asMixed: false };

  let rNum: number;
  let rDen: number;
  let opSym: string;
  if (opts.topic === "multiply-fractions") {
    rNum = a.num * b.num;
    rDen = a.den * b.den;
    opSym = "×";
  } else {
    // Divide: a / b = (a.num * b.den) / (a.den * b.num)
    rNum = a.num * b.den;
    rDen = a.den * b.num;
    opSym = "÷";
  }
  [rNum, rDen] = simplify(rNum, rDen);

  const aStr = fmtFraction(a.num, a.den, a.asMixed);
  const bStr = fmtFraction(b.num, b.den, b.asMixed);
  const aDisplay = a.num < 0 ? wrapNegative(aStr) : aStr;
  const bDisplay = b.num < 0 ? wrapNegative(bStr) : bStr;
  const display = `${aDisplay} ${opSym} ${bDisplay}`;

  const wantsMixed = opts.formats.mixed;
  const answer = fmtFraction(rNum, rDen, wantsMixed);

  return { num: idx, display, answer };
}

function generateDecimalProblem(opts: FluencyOptions, idx: number): Problem {
  // Pick decimal-place count per operand. Hard mixes 1-3 places.
  const placesFor = (): number => {
    if (opts.difficulty === "easy") return 1;
    if (opts.difficulty === "medium") return 2;
    return rnd(1, 3);
  };

  const sign = () => (opts.allowNegatives && Math.random() < 0.5 ? -1 : 1);
  const wholeMax = opts.difficulty === "easy" ? 10 : 99;
  const isMul = opts.topic === "multiply-decimals";
  const isDiv = opts.topic === "divide-decimals";

  let a: number;
  let b: number;
  let display: string;
  let answer: string;

  if (isDiv) {
    // Build a clean divide problem by picking the QUOTIENT first, then b,
    // and computing a = quotient * b. Guarantees the answer terminates.
    const qPlaces = opts.difficulty === "easy" ? 1 : opts.difficulty === "medium" ? 2 : rnd(1, 3);
    const bPlaces = opts.difficulty === "easy" ? 0 : rnd(0, 2);
    const sQ = sign();
    const sB = sign();
    const q = (sQ * rnd(1, 50 * 10 ** qPlaces)) / 10 ** qPlaces;
    let bVal = (sB * rnd(1, 20 * 10 ** bPlaces)) / 10 ** bPlaces;
    if (bVal === 0) bVal = 1;
    a = q * bVal;
    b = bVal;

    const aStr = a.toFixed(qPlaces + bPlaces);
    const bStr = bPlaces === 0 ? String(b) : b.toFixed(bPlaces);
    const aDisplay = a < 0 ? wrapNegative(aStr) : aStr;
    const bDisplay = b < 0 ? wrapNegative(bStr) : bStr;
    display = `${aDisplay} ÷ ${bDisplay}`;
    answer = trimDecimal(q, qPlaces);
  } else if (isMul) {
    const p1 = placesFor();
    const p2 = placesFor();
    a = (sign() * rnd(1, wholeMax * 10 ** p1)) / 10 ** p1;
    b = (sign() * rnd(1, wholeMax * 10 ** p2)) / 10 ** p2;
    const result = a * b;
    const aStr = a.toFixed(p1);
    const bStr = b.toFixed(p2);
    const aDisplay = a < 0 ? wrapNegative(aStr) : aStr;
    const bDisplay = b < 0 ? wrapNegative(bStr) : bStr;
    display = `${aDisplay} × ${bDisplay}`;
    // Multiplication result places = sum of operand places.
    answer = trimDecimal(result, p1 + p2);
  } else {
    // Add / subtract.
    const p1 = placesFor();
    const p2 = placesFor();
    a = (sign() * rnd(1, wholeMax * 10 ** p1)) / 10 ** p1;
    b = (sign() * rnd(1, wholeMax * 10 ** p2)) / 10 ** p2;
    const op = opts.topic === "add-decimals" ? 1 : -1;
    const result = a + b * op;
    const aStr = a.toFixed(p1);
    const bStr = b.toFixed(p2);
    const opSym = opts.topic === "add-decimals" ? "+" : "−";
    const aDisplay = a < 0 ? wrapNegative(aStr) : aStr;
    const bDisplay = b < 0 ? wrapNegative(bStr) : bStr;
    display = `${aDisplay} ${opSym} ${bDisplay}`;
    const maxP = Math.max(p1, p2);
    answer = trimDecimal(result, maxP);
  }

  return { num: idx, display, answer };
}

/** Round to `places` decimals and drop trailing zeros so the answer reads
 *  naturally: 3.5 instead of 3.500, 7 instead of 7.00. */
function trimDecimal(n: number, places: number): string {
  const factor = 10 ** places;
  const rounded = Math.round(n * factor) / factor;
  // toFixed → strip trailing zeros → strip trailing dot.
  return rounded
    .toFixed(places)
    .replace(/0+$/, "")
    .replace(/\.$/, "");
}

// ───────────────────────────────────────────────────────────
//                 CONVERTING RATIONAL NUMBERS
// ───────────────────────────────────────────────────────────
//
// Display convention for repeating decimals: we wrap the repeating digit
// group in pipes, e.g. "0.|3|" or "0.16|6|". The MathExpr renderer in the
// UI recognizes |...| and draws an overline over those digits.

/** Denominators that produce terminating decimals (prime factors 2 and 5 only). */
function pickTerminatingDenom(difficulty: Difficulty): number {
  const easy = [2, 4, 5, 10];
  const med = [2, 4, 5, 8, 10, 20, 25];
  const hard = [4, 5, 8, 16, 20, 25, 50, 100];
  const pool = difficulty === "easy" ? easy : difficulty === "medium" ? med : hard;
  return pool[Math.floor(Math.random() * pool.length)];
}

/** Denominators whose decimal expansion repeats. */
function pickRepeatingDenom(difficulty: Difficulty): number {
  const easy = [3, 9];
  const med = [3, 6, 9, 11];
  const hard = [3, 6, 7, 9, 11, 12, 13];
  const pool = difficulty === "easy" ? easy : difficulty === "medium" ? med : hard;
  return pool[Math.floor(Math.random() * pool.length)];
}

/**
 * Convert a fraction num/den to its decimal expansion. If repeating, the
 * repeating block is wrapped in pipes for the renderer to overline.
 * Examples: 1/3 → "0.|3|"  · 1/6 → "0.1|6|"  · 3/4 → "0.75"
 */
function fractionToDecimalString(num: number, den: number): string {
  if (den === 0) return "0";
  const sign = num < 0 ? "-" : "";
  const N = Math.abs(num);
  const intPart = Math.floor(N / den);
  let rem = N % den;
  if (rem === 0) return `${sign}${intPart}`;

  // Long division: track each remainder so we can detect a repeat.
  const seen = new Map<number, number>(); // remainder → position in digits
  let digits = "";
  while (rem !== 0 && !seen.has(rem)) {
    seen.set(rem, digits.length);
    rem *= 10;
    digits += Math.floor(rem / den);
    rem = rem % den;
  }
  if (rem === 0) return `${sign}${intPart}.${digits}`;
  const start = seen.get(rem)!;
  const non = digits.slice(0, start);
  const rep = digits.slice(start);
  return non
    ? `${sign}${intPart}.${non}|${rep}|`
    : `${sign}${intPart}.|${rep}|`;
}

function randomBool(): boolean {
  return Math.random() < 0.5;
}

function makeFractionToDec(opts: FluencyOptions, idx: number, repeating: boolean): Problem {
  const den = repeating
    ? pickRepeatingDenom(opts.difficulty)
    : pickTerminatingDenom(opts.difficulty);
  const num = rnd(1, den - 1);
  // Hard mode occasionally throws in mixed/improper.
  let whole = 0;
  if (opts.difficulty === "hard" && randomBool()) {
    whole = rnd(1, 9);
  }
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const totalNum = (whole * den + num) * sign;
  const display = whole > 0
    ? `${sign === -1 ? "-" : ""}${whole} ${num}/${den}`
    : `${sign === -1 ? "-" : ""}${num}/${den}`;
  const answer = fractionToDecimalString(totalNum, den);
  return { num: idx, display, answer };
}

function makeDecToFrac(opts: FluencyOptions, idx: number, repeating: boolean): Problem {
  // Generate from the answer (a fraction) and produce the decimal.
  const den = repeating
    ? pickRepeatingDenom(opts.difficulty)
    : pickTerminatingDenom(opts.difficulty);
  let num = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  num *= sign;
  const dec = fractionToDecimalString(num, den);
  // Display IS the decimal; the answer is the simplified fraction.
  const [sn, sd] = simplify(num, den);
  const answer = sd === 1 ? String(sn) : `${sn}/${sd}`;
  return { num: idx, display: dec, answer };
}

function makeFracToPercent(opts: FluencyOptions, idx: number): Problem {
  const den = pickTerminatingDenom(opts.difficulty);
  const num = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const signed = num * sign;
  const display = `${sign === -1 ? "-" : ""}${num}/${den}`;
  // num/den × 100
  const pct = (signed * 100) / den;
  const pctStr = Number.isInteger(pct) ? String(pct) : trimDecimal(pct, 4);
  return { num: idx, display, answer: `${pctStr}%` };
}

function makePercentToFrac(opts: FluencyOptions, idx: number): Problem {
  // Pick a percent that maps to a clean fraction with a friendly denom.
  const den = pickTerminatingDenom(opts.difficulty);
  const k = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const pct = (k * 100) / den;
  const pctStr = Number.isInteger(pct) ? String(pct) : trimDecimal(pct, 4);
  const [sn, sd] = simplify(k * sign, den);
  const fracStr = sd === 1 ? String(sn) : `${sn}/${sd}`;
  return { num: idx, display: `${sign === -1 ? "-" : ""}${pctStr}%`, answer: fracStr };
}

function makeDecToPercent(opts: FluencyOptions, idx: number): Problem {
  const den = pickTerminatingDenom(opts.difficulty);
  const k = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const signedNum = k * sign;
  const dec = fractionToDecimalString(signedNum, den);
  const pct = (signedNum * 100) / den;
  const pctStr = Number.isInteger(pct) ? String(pct) : trimDecimal(pct, 4);
  return { num: idx, display: dec, answer: `${pctStr}%` };
}

function makePercentToDec(opts: FluencyOptions, idx: number): Problem {
  const den = pickTerminatingDenom(opts.difficulty);
  const k = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const signedNum = k * sign;
  const pct = (signedNum * 100) / den;
  const pctStr = Number.isInteger(pct) ? String(pct) : trimDecimal(pct, 4);
  const dec = fractionToDecimalString(signedNum, den);
  return { num: idx, display: `${sign === -1 ? "-" : ""}${Math.abs(parseFloat(pctStr))}%`, answer: dec };
}

function makeMixedToImproper(opts: FluencyOptions, idx: number): Problem {
  const den = rnd(2, Math.min(12, opts.maxDenominator));
  const whole = rnd(1, opts.difficulty === "easy" ? 5 : opts.difficulty === "medium" ? 9 : 15);
  const num = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const display = `${sign === -1 ? "-" : ""}${whole} ${num}/${den}`;
  const improperNum = (whole * den + num) * sign;
  return { num: idx, display, answer: `${improperNum}/${den}` };
}

function makeImproperToMixed(opts: FluencyOptions, idx: number): Problem {
  const den = rnd(2, Math.min(12, opts.maxDenominator));
  const whole = rnd(1, opts.difficulty === "easy" ? 5 : opts.difficulty === "medium" ? 9 : 15);
  const numRem = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const improperNum = (whole * den + numRem) * sign;
  const display = `${improperNum}/${den}`;
  const answer = `${sign === -1 ? "-" : ""}${whole} ${numRem}/${den}`;
  return { num: idx, display, answer };
}

// Render a rational as one of {fraction, decimal, percent} chosen at random.
// Returns { display, value } so we can compare numerically.
function randomMixedForm(opts: FluencyOptions): { display: string; value: number } {
  const den = pickTerminatingDenom(opts.difficulty);
  const num = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const value = (num * sign) / den;
  const form = ["frac", "dec", "pct"][Math.floor(Math.random() * 3)];
  if (form === "frac") {
    return { display: `${sign === -1 ? "-" : ""}${num}/${den}`, value };
  }
  if (form === "dec") {
    return { display: fractionToDecimalString(num * sign, den), value };
  }
  // percent
  const pct = (num * sign * 100) / den;
  const pctStr = Number.isInteger(pct) ? String(pct) : trimDecimal(pct, 4);
  return { display: `${pctStr}%`, value };
}

function makeCompareRationals(opts: FluencyOptions, idx: number): Problem {
  const a = randomMixedForm(opts);
  let b = randomMixedForm(opts);
  // Avoid trivially-equal pairs unless we explicitly want them.
  let attempts = 0;
  while (attempts < 10 && a.value === b.value) {
    b = randomMixedForm(opts);
    attempts++;
  }
  const sym = a.value < b.value ? "<" : a.value > b.value ? ">" : "=";
  return {
    num: idx,
    display: `${a.display}  ___  ${b.display}`,
    answer: sym,
  };
}

function makeOrderRationals(opts: FluencyOptions, idx: number): Problem {
  const k = opts.difficulty === "easy" ? 3 : 4;
  const items: { display: string; value: number }[] = [];
  const seen = new Set<number>();
  while (items.length < k) {
    const v = randomMixedForm(opts);
    if (seen.has(v.value)) continue;
    seen.add(v.value);
    items.push(v);
  }
  const shuffled = [...items].sort(() => Math.random() - 0.5);
  const ordered = [...items].sort((x, y) => x.value - y.value);
  return {
    num: idx,
    display: `Least → greatest: ${shuffled.map((v) => v.display).join(", ")}`,
    answer: ordered.map((v) => v.display).join(", "),
  };
}

// ───────────────────────────────────────────────────────────
//                       EQUATIONS
// ───────────────────────────────────────────────────────────
//
// Display strings use plain text + "x" for the variable. The MathExpr
// tokenizer in the UI already renders + / − operators with extra margin
// and any "a/b" digit fractions as stacked, so most equations render
// nicely without further work.

/** Render a leading coefficient term: 1→"x", -1→"−x", 5→"5x", -5→"−5x". */
function fmtCoefTerm(coef: number, v = "x"): string {
  if (coef === 1) return v;
  if (coef === -1) return `−${v}`;
  return coef < 0 ? `−${Math.abs(coef)}${v}` : `${coef}${v}`;
}

/** Render an additive term after the first: "+ 5" or "− 5". */
function fmtAddConst(value: number): string {
  return value < 0 ? `− ${Math.abs(value)}` : `+ ${value}`;
}

/** Render an additive coefficient term after the first: "+ 5x" or "− 5x". */
function fmtAddCoef(coef: number, v = "x"): string {
  const sign = coef < 0 ? "− " : "+ ";
  const abs = Math.abs(coef);
  if (abs === 1) return `${sign}${v}`;
  return `${sign}${abs}${v}`;
}

/** Format the answer "x = …". Uses a fraction when the solution isn't an
 *  integer. */
function fmtSolution(num: number, den: number): string {
  const [sn, sd] = simplify(num, den);
  if (sd === 1) return `x = ${sn}`;
  // Mixed-number rendering when the absolute value > 1.
  if (Math.abs(sn) >= sd) {
    const sign = sn < 0 ? "−" : "";
    const whole = Math.floor(Math.abs(sn) / sd);
    const rem = Math.abs(sn) % sd;
    if (rem === 0) return `x = ${sign}${whole}`;
    return `x = ${sign}${whole} ${rem}/${sd}`;
  }
  return `x = ${sn}/${sd}`;
}

/** Difficulty-aware sign rule for equation/inequality/graphing topics:
 *  Easy stays positive, Medium and Hard mix negatives in — and the
 *  teacher's "Allow negatives" toggle can force them on at any level. */
function negsFor(opts: FluencyOptions): boolean {
  return opts.allowNegatives || opts.difficulty !== "easy";
}

/** Simplified signed fraction for display: "5/4", "−3/2"; integers plain. */
function fmtSimpleFrac(n: number, d: number): string {
  const [sn, sd] = simplify(n, d);
  if (sd === 1) return sn < 0 ? `−${Math.abs(sn)}` : `${sn}`;
  return sn < 0 ? `−${Math.abs(sn)}/${sd}` : `${sn}/${sd}`;
}

/** Format a tenths-int as a decimal string ("−4.8", "12", "0.5"). Doing
 *  decimal arithmetic in integer tenths keeps every hard-tier decimal
 *  problem exact — no floating-point fuzz on a worksheet. */
function fmtTenths(t: number): string {
  const v = Math.abs(t) / 10;
  const s = Number.isInteger(v) ? `${v}` : v.toFixed(1);
  return t < 0 ? `−${s}` : s;
}

/** Pick a non-zero coefficient appropriate to difficulty. */
function rndCoef(opts: FluencyOptions, allowNegative: boolean): number {
  const max = opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 9 : 12;
  let v = rnd(1, max);
  if (allowNegative && randomBool()) v = -v;
  return v;
}

/** Pick a constant appropriate to difficulty. */
function rndConst(opts: FluencyOptions, allowNegative: boolean): number {
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 18 : 25;
  let v = rnd(1, max);
  if (allowNegative && randomBool()) v = -v;
  return v;
}

/** Pick the SOLUTION first, then back-solve to a clean equation. */
function rndSolution(opts: FluencyOptions, allowNegative: boolean): number {
  const range = opts.difficulty === "easy" ? 9 : opts.difficulty === "medium" ? 12 : 18;
  let v = rnd(1, range);
  if (allowNegative && randomBool()) v = -v;
  return v;
}

// ----- Tier 1: One-Step -----

function makeOneStepAdd(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the problems use one-place decimals or same-denominator
  // fractions (exact arithmetic in tenths / numerators).
  if (opts.difficulty === "hard" && randomBool()) {
    if (randomBool()) {
      const a10 = rnd(11, 99);
      const x10 = rnd(11, 99) * (randomBool() ? 1 : -1);
      return {
        num: idx,
        display: `x + ${fmtTenths(a10)} = ${fmtTenths(x10 + a10)}`,
        answer: `x = ${fmtTenths(x10)}`,
      };
    }
    const d = rnd(2, 6);
    const an = rnd(1, d - 1);
    const xn = rnd(1, 2 * d) * (randomBool() ? 1 : -1);
    return {
      num: idx,
      display: `x + ${an}/${d} = ${fmtSimpleFrac(xn + an, d)}`,
      answer: `x = ${fmtSimpleFrac(xn, d)}`,
    };
  }
  const a = rndCoef(opts, false);
  const x = rndSolution(opts, negsFor(opts));
  const b = x + a;
  return { num: idx, display: `x + ${a} = ${b}`, answer: `x = ${x}` };
}

function makeOneStepSub(opts: FluencyOptions, idx: number): Problem {
  if (opts.difficulty === "hard" && randomBool()) {
    if (randomBool()) {
      const a10 = rnd(11, 99);
      const x10 = rnd(11, 99) * (randomBool() ? 1 : -1);
      return {
        num: idx,
        display: `x − ${fmtTenths(a10)} = ${fmtTenths(x10 - a10)}`,
        answer: `x = ${fmtTenths(x10)}`,
      };
    }
    const d = rnd(2, 6);
    const an = rnd(1, d - 1);
    const xn = rnd(1, 2 * d) * (randomBool() ? 1 : -1);
    return {
      num: idx,
      display: `x − ${an}/${d} = ${fmtSimpleFrac(xn - an, d)}`,
      answer: `x = ${fmtSimpleFrac(xn, d)}`,
    };
  }
  const a = rndCoef(opts, false);
  const x = rndSolution(opts, negsFor(opts));
  const b = x - a;
  return { num: idx, display: `x − ${a} = ${b}`, answer: `x = ${x}` };
}

function makeOneStepMul(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the problems get a decimal or fraction coefficient.
  if (opts.difficulty === "hard" && randomBool()) {
    if (randomBool()) {
      const a10 = [5, 15, 25, 4, 6, 12][rnd(0, 5)] * (randomBool() ? 1 : -1);
      const x = rnd(1, 9) * (randomBool() ? 1 : -1);
      return {
        num: idx,
        display: `${fmtTenths(a10)}x = ${fmtTenths(a10 * x)}`,
        answer: `x = ${x}`,
      };
    }
    const d = rnd(2, 6);
    let n = rnd(1, d - 1);
    while (gcd(n, d) !== 1) n += 1;
    if (randomBool()) n = -n;
    const m = rnd(1, 6) * (randomBool() ? 1 : -1);
    const x = m * d;
    const coefStr = n < 0 ? `−${Math.abs(n)}/${d}` : `${n}/${d}`;
    return {
      num: idx,
      display: `${coefStr}x = ${n * m}`,
      answer: `x = ${x}`,
    };
  }
  const a = rndCoef(opts, negsFor(opts));
  const x = rndSolution(opts, negsFor(opts));
  const b = a * x;
  return { num: idx, display: `${fmtCoefTerm(a)} = ${b}`, answer: `x = ${x}` };
}

function makeOneStepDiv(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the problems put a fraction on the right (x/a = n/d).
  if (opts.difficulty === "hard" && randomBool()) {
    const d = rnd(2, 4);
    const m = rnd(2, 5);
    const a = d * m;
    let n = rnd(1, 2 * d - 1);
    while (gcd(n, d) !== 1) n += 1;
    if (randomBool()) n = -n;
    return {
      num: idx,
      display: `x/${a} = ${fmtSimpleFrac(n, d)}`,
      answer: `x = ${m * n}`,
    };
  }
  const a = rndCoef(opts, negsFor(opts));
  // Solution can be anything; we still display as x/a = b. Solution = a*b.
  const b = rndConst(opts, negsFor(opts));
  const x = a * b;
  return { num: idx, display: `x/${a < 0 ? `(${a})` : a} = ${b}`, answer: `x = ${x}` };
}

function makeOneStepMixed(opts: FluencyOptions, idx: number): Problem {
  const which = rnd(0, 3);
  if (which === 0) return makeOneStepAdd(opts, idx);
  if (which === 1) return makeOneStepSub(opts, idx);
  if (which === 2) return makeOneStepMul(opts, idx);
  return makeOneStepDiv(opts, idx);
}

// ----- Tier 2: Two-Step -----

function makeTwoStepPos(opts: FluencyOptions, idx: number): Problem {
  // Everything stays positive at every level (this topic's contract) —
  // hard raises the numbers and mixes in one-place decimal coefficients.
  if (opts.difficulty === "hard" && randomBool()) {
    const a10 = [5, 15, 25, 12, 24][rnd(0, 4)];
    const x = rnd(1, 9);
    const b = rnd(1, 15);
    return {
      num: idx,
      display: `${fmtTenths(a10)}x ${fmtAddConst(b)} = ${fmtTenths(a10 * x + b * 10)}`,
      answer: `x = ${x}`,
    };
  }
  const a = Math.abs(rndCoef(opts, false));
  const b = Math.abs(rndConst(opts, false));
  const x = Math.abs(rndSolution(opts, false));
  const c = a * x + b;
  return { num: idx, display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${c}`, answer: `x = ${x}` };
}

function makeTwoStepNeg(opts: FluencyOptions, idx: number): Problem {
  // Same shape but with negatives forced on. Hard mixes in decimal
  // coefficients (still exact — tenths arithmetic).
  if (opts.difficulty === "hard" && randomBool()) {
    const a10 = [5, 15, 25, 12][rnd(0, 3)] * (randomBool() ? 1 : -1);
    const x = rnd(1, 9) * (randomBool() ? 1 : -1);
    const b = rnd(1, 15) * (randomBool() ? 1 : -1);
    return {
      num: idx,
      display: `${fmtTenths(a10)}x ${fmtAddConst(b)} = ${fmtTenths(a10 * x + b * 10)}`,
      answer: `x = ${x}`,
    };
  }
  const a = rndCoef(opts, true);
  const b = rndConst(opts, true);
  const x = rndSolution(opts, true);
  const c = a * x + b;
  return { num: idx, display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${c}`, answer: `x = ${x}` };
}

function makeTwoStepRational(opts: FluencyOptions, idx: number): Problem {
  // Easy: unit-fraction coefficient, everything positive.
  // Medium: any proper-fraction coefficient, signs mixed.
  // Hard: adds one-place decimal coefficients to the rotation.
  // (No "·" between fraction and variable — multiplication is implied.)
  if (opts.difficulty === "easy") {
    const d = [2, 3, 4, 5, 6][rnd(0, 4)];
    const b = rnd(1, 9);
    const x = rnd(1, 8) * d; // ensure (1/d)x is whole
    const c = x / d + b;
    return {
      num: idx,
      display: `1/${d}x ${fmtAddConst(b)} = ${c}`,
      answer: `x = ${x}`,
    };
  }
  if (opts.difficulty === "medium" || randomBool()) {
    const d = rnd(2, 6);
    let n = rnd(1, d - 1);
    while (gcd(n, d) !== 1) n += 1;
    if (randomBool()) n = -n;
    const b = rnd(1, 12) * (randomBool() ? 1 : -1);
    const m = rnd(1, 6) * (randomBool() ? 1 : -1);
    const x = m * d;
    const c = n * m + b;
    const coefStr = n < 0 ? `−${Math.abs(n)}/${d}` : `${n}/${d}`;
    return {
      num: idx,
      display: `${coefStr}x ${fmtAddConst(b)} = ${c}`,
      answer: `x = ${x}`,
    };
  }
  const a10 = [5, 15, 25, 4, 6, 8, 12][rnd(0, 6)] * (randomBool() ? 1 : -1);
  const x = rnd(1, 9) * (randomBool() ? 1 : -1);
  const b = rnd(1, 12) * (randomBool() ? 1 : -1);
  return {
    num: idx,
    display: `${fmtTenths(a10)}x ${fmtAddConst(b)} = ${fmtTenths(a10 * x + b * 10)}`,
    answer: `x = ${x}`,
  };
}

function makeTwoStepDist(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the problems distribute a unit fraction — 1/d(x + q) = r.
  if (opts.difficulty === "hard" && randomBool()) {
    const d = [2, 3, 4][rnd(0, 2)];
    const sign = randomBool() ? 1 : -1;
    const x = rnd(1, 9) * (randomBool() ? 1 : -1);
    let q = rnd(1, 8) * (randomBool() ? 1 : -1);
    q += (d - ((((x + q) % d) + d) % d)) % d; // make x + q divisible by d
    const r = (sign * (x + q)) / d;
    const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
    return {
      num: idx,
      display: `${sign === -1 ? "−" : ""}1/${d}(x ${qStr}) = ${r}`,
      answer: `x = ${x}`,
    };
  }
  // p(x + q) = r — pick x, p, q; compute r.
  const p = rndCoef(opts, negsFor(opts));
  const q = rndConst(opts, negsFor(opts));
  const x = rndSolution(opts, negsFor(opts));
  const r = p * (x + q);
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) = ${r}`,
    answer: `x = ${x}`,
  };
}

// ----- Tier 3: Multi-Step -----

function makeMultiCombine(opts: FluencyOptions, idx: number): Problem {
  // Hard: ~40% of problems combine DECIMAL like terms whose sum is a
  // whole coefficient (0.7x + 2.3x − 4 = 8) — exact tenths arithmetic.
  if (opts.difficulty === "hard" && Math.random() < 0.4) {
    let a10 = rnd(1, 29);
    if (a10 % 10 === 0) a10 += 1;
    const sum10 = (Math.ceil(a10 / 10) + rnd(1, 2)) * 10;
    const b10 = sum10 - a10;
    const c = rnd(1, 12) * (randomBool() ? 1 : -1);
    const x = rnd(1, 9) * (randomBool() ? 1 : -1);
    const d = (sum10 / 10) * x + c;
    return {
      num: idx,
      display: `${fmtTenths(a10)}x + ${fmtTenths(b10)}x ${fmtAddConst(c)} = ${d}`,
      answer: `x = ${x}`,
    };
  }
  // ax + bx + c = d → (a+b)x + c = d → x = (d−c)/(a+b)
  const a = rndCoef(opts, negsFor(opts));
  let b = rndCoef(opts, negsFor(opts));
  // Avoid a + b = 0 (would erase the variable).
  if (a + b === 0) b += 1;
  const c = rndConst(opts, negsFor(opts));
  const x = rndSolution(opts, negsFor(opts));
  const d = (a + b) * x + c;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddCoef(b)} ${fmtAddConst(c)} = ${d}`,
    answer: `x = ${x}`,
  };
}

function makeMultiDist(opts: FluencyOptions, idx: number): Problem {
  // Hard: ~40% of problems distribute a unit fraction —
  // 1/d(x + q) + r = s with (x + q) divisible by d.
  if (opts.difficulty === "hard" && Math.random() < 0.4) {
    const den = [2, 3, 4][rnd(0, 2)];
    const x = rnd(1, 9) * (randomBool() ? 1 : -1);
    let q = rnd(1, 8) * (randomBool() ? 1 : -1);
    q += (den - ((((x + q) % den) + den) % den)) % den;
    const r = rnd(1, 9) * (randomBool() ? 1 : -1);
    const s = (x + q) / den + r;
    const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
    return {
      num: idx,
      display: `1/${den}(x ${qStr}) ${fmtAddConst(r)} = ${s}`,
      answer: `x = ${x}`,
    };
  }
  // p(x + q) + r = s
  const p = rndCoef(opts, negsFor(opts));
  const q = rndConst(opts, negsFor(opts));
  const r = rndConst(opts, negsFor(opts));
  const x = rndSolution(opts, negsFor(opts));
  const s = p * (x + q) + r;
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)} = ${s}`,
    answer: `x = ${x}`,
  };
}

function makeMultiBoth(opts: FluencyOptions, idx: number): Problem {
  // Hard: ~40% of problems use decimal coefficients on both sides whose
  // difference is a whole number (1.5x + 4 = 0.5x − 2).
  if (opts.difficulty === "hard" && Math.random() < 0.4) {
    let c10 = rnd(1, 19);
    if (c10 % 10 === 0) c10 += 1;
    const a10 = c10 + 10 * rnd(1, 2);
    const x = rnd(1, 9) * (randomBool() ? 1 : -1);
    const b = rnd(1, 12) * (randomBool() ? 1 : -1);
    const d = ((a10 - c10) / 10) * x + b;
    return {
      num: idx,
      display: `${fmtTenths(a10)}x ${fmtAddConst(b)} = ${fmtTenths(c10)}x ${fmtAddConst(d)}`,
      answer: `x = ${x}`,
    };
  }
  // ax + b = cx + d → (a−c)x = d − b
  const a = rndCoef(opts, negsFor(opts));
  let c = rndCoef(opts, negsFor(opts));
  if (a === c) c += 1; // ensure (a-c) != 0
  const x = rndSolution(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  const d = (a - c) * x + b;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${fmtCoefTerm(c)} ${fmtAddConst(d)}`,
    answer: `x = ${x}`,
  };
}

function makeMultiFull(opts: FluencyOptions, idx: number): Problem {
  // p(x + q) + r = sx + t
  const p = rndCoef(opts, negsFor(opts));
  const q = rndConst(opts, negsFor(opts));
  const r = rndConst(opts, negsFor(opts));
  let s = rndCoef(opts, negsFor(opts));
  if (p === s) s += 1;
  const x = rndSolution(opts, negsFor(opts));
  const t = p * (x + q) + r - s * x;
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)} = ${fmtCoefTerm(s)} ${fmtAddConst(t)}`,
    answer: `x = ${x}`,
  };
}

function makeMultiSpecial(opts: FluencyOptions, idx: number): Problem {
  // A third each: no solution, infinitely many, exactly ONE solution —
  // and every equation must be simplified (combine like terms and/or
  // distribute) before the outcome is visible. The old version wrote
  // identical sides verbatim, so students could answer at a glance
  // without doing any algebra.
  const outcome = rnd(0, 2); // 0 = no solution, 1 = infinite, 2 = one solution
  const sgn = () => (randomBool() ? 1 : -1);

  if (opts.difficulty === "easy") {
    // ax + bx + c = sx + e — combine the left side first.
    const a = rnd(2, 6);
    let b = rnd(1, 5) * sgn();
    if (a + b === 0 || a + b === 1) b += 1;
    const c = rnd(1, 12);
    const s = a + b;
    const lhs = `${fmtCoefTerm(a)} ${fmtAddCoef(b)} ${fmtAddConst(c)}`;
    if (outcome === 1) {
      return { num: idx, display: `${lhs} = ${fmtCoefTerm(s)} ${fmtAddConst(c)}`, answer: "all real numbers" };
    }
    if (outcome === 0) {
      const e = c + rnd(1, 6) * sgn();
      return { num: idx, display: `${lhs} = ${fmtCoefTerm(s)} ${fmtAddConst(e)}`, answer: "no solution" };
    }
    let d = rnd(1, 6) * sgn();
    if (d === s) d += 1;
    const x = rnd(1, 9) * sgn();
    const e = (s - d) * x + c;
    return { num: idx, display: `${lhs} = ${fmtCoefTerm(d)} ${fmtAddConst(e)}`, answer: `x = ${x}` };
  }

  if (opts.difficulty === "medium") {
    // p(x + q) + r = ax + c — distribute the left side first.
    const p = rnd(2, 6) * sgn();
    const q = rnd(1, 6) * sgn();
    const r = rnd(1, 9) * sgn();
    const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
    const lhs = `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)}`;
    const flatConst = p * q + r;
    if (outcome === 1) {
      return { num: idx, display: `${lhs} = ${fmtCoefTerm(p)} ${fmtAddConst(flatConst)}`, answer: "all real numbers" };
    }
    if (outcome === 0) {
      const c = flatConst + rnd(1, 6) * sgn();
      return { num: idx, display: `${lhs} = ${fmtCoefTerm(p)} ${fmtAddConst(c)}`, answer: "no solution" };
    }
    let a = rnd(1, 6) * sgn();
    if (a === p) a += 1;
    const x = rnd(1, 9) * sgn();
    const c = (p - a) * x + flatConst;
    return { num: idx, display: `${lhs} = ${fmtCoefTerm(a)} ${fmtAddConst(c)}`, answer: `x = ${x}` };
  }

  // Hard: p(x + q) + r = s(x + t) + u — distribute BOTH sides.
  const p = rnd(2, 7) * sgn();
  const q = rnd(1, 6) * sgn();
  const r = rnd(1, 9) * sgn();
  const t = rnd(1, 6) * sgn();
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  const tStr = t < 0 ? `− ${Math.abs(t)}` : `+ ${t}`;
  const lhs = `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)}`;
  const rhsOf = (s: number, u: number) =>
    `${s < 0 ? `−${Math.abs(s)}` : s}(x ${tStr}) ${fmtAddConst(u)}`;
  const lhsConst = p * q + r;
  if (outcome === 1) {
    const u = lhsConst - p * t;
    return { num: idx, display: `${lhs} = ${rhsOf(p, u)}`, answer: "all real numbers" };
  }
  if (outcome === 0) {
    const u = lhsConst - p * t + rnd(1, 6) * sgn();
    return { num: idx, display: `${lhs} = ${rhsOf(p, u)}`, answer: "no solution" };
  }
  let s = rnd(2, 7) * sgn();
  if (s === p) s += 1;
  const x = rnd(1, 9) * sgn();
  const u = (p - s) * x + lhsConst - s * t;
  return { num: idx, display: `${lhs} = ${rhsOf(s, u)}`, answer: `x = ${x}` };
}

// ----- Tier 4: Literal -----

// Formula pools by how many undo-steps the rearrangement takes:
//   easy   — one inverse operation (divide or subtract once)
//   medium — two steps (subtract then divide)
//   hard   — multi-step, fractions, or factoring involved
const LITERAL_EASY: { display: string; answer: string }[] = [
  { display: "Solve for w:  A = lw", answer: "w = A/l" },
  { display: "Solve for t:  d = rt", answer: "t = d/r" },
  { display: "Solve for r:  d = rt", answer: "r = d/t" },
  { display: "Solve for h:  V = lwh", answer: "h = V/(lw)" },
  { display: "Solve for a:  P = a + b + c", answer: "a = P − b − c" },
  { display: "Solve for r:  C = 2πr", answer: "r = C/(2π)" },
];
const LITERAL_MEDIUM: { display: string; answer: string }[] = [
  { display: "Solve for x:  y = mx + b", answer: "x = (y − b)/m" },
  { display: "Solve for m:  y = mx + b", answer: "m = (y − b)/x" },
  { display: "Solve for b:  y = mx + b", answer: "b = y − mx" },
  { display: "Solve for l:  P = 2l + 2w", answer: "l = (P − 2w)/2" },
  { display: "Solve for h:  A = (1/2)bh", answer: "h = 2A/b" },
  { display: "Solve for t:  I = Prt", answer: "t = I/(Pr)" },
];
const LITERAL_HARD: { display: string; answer: string }[] = [
  { display: "Solve for C:  F = (9/5)C + 32", answer: "C = (5/9)(F − 32)" },
  { display: "Solve for b:  A = (1/2)h(b + c)", answer: "b = (2A/h) − c" },
  { display: "Solve for y:  ax + by = c", answer: "y = (c − ax)/b" },
  { display: "Solve for h:  S = 2πr² + 2πrh", answer: "h = (S − 2πr²)/(2πr)" },
  { display: "Solve for r:  A = P(1 + rt)", answer: "r = (A − P)/(Pt)" },
];

function makeLiteral(opts: FluencyOptions, idx: number): Problem {
  const pool =
    opts.difficulty === "easy" ? LITERAL_EASY
    : opts.difficulty === "medium" ? LITERAL_MEDIUM
    : LITERAL_HARD;
  const pick = pool[rnd(0, pool.length - 1)];
  return { num: idx, display: pick.display, answer: pick.answer };
}

// ----- Tier 5: Proportions -----

function makeProportion(opts: FluencyOptions, idx: number): Problem {
  // Build a true proportion a/b = c/d (i.e., a·d = b·c), then hide one
  // of the four terms behind x.
  //   easy   — x in a numerator, whole-number scale factor
  //   medium — x in any of the four positions
  //   hard   — also mixes proportions whose answer is NOT a whole
  //            number (cross-multiply and divide; fraction answers)
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 12 : 15;
  if (opts.difficulty === "hard" && randomBool()) {
    const a = rnd(2, max);
    let b = rnd(2, max);
    while (b === a) b = rnd(2, max); // avoid the trivial a/a = 1 ratio
    const c = rnd(2, max);
    if (randomBool()) {
      // a/b = c/x → x = b·c/a
      return { num: idx, display: `${a}/${b} = ${c}/x`, answer: fmtSolution(b * c, a) };
    }
    // a/b = x/c → x = a·c/b
    return { num: idx, display: `${a}/${b} = x/${c}`, answer: fmtSolution(a * c, b) };
  }
  const a = rnd(2, max);
  let b = rnd(2, max);
  while (b === a) b = rnd(2, max); // avoid the trivial a/a = 1 ratio
  const k = rnd(2, 6);
  const c = a * k;
  const d = b * k;
  const pos = opts.difficulty === "easy" ? [0, 2][rnd(0, 1)] : rnd(0, 3);
  let display: string;
  let answer: string;
  if (pos === 0) {        display = `x/${b} = ${c}/${d}`; answer = `x = ${a}`; }
  else if (pos === 1) {   display = `${a}/x = ${c}/${d}`; answer = `x = ${b}`; }
  else if (pos === 2) {   display = `${a}/${b} = x/${d}`; answer = `x = ${c}`; }
  else {                  display = `${a}/${b} = ${c}/x`; answer = `x = ${d}`; }
  return { num: idx, display, answer };
}

// Difficulty ladder: easy uses small whole numbers, medium uses larger
// scale factors, hard mixes decimal money / measurement values.
const PROPORTION_WORDS: ((d: Difficulty) => { display: string; answer: string })[] = [
  (dif) => {
    const a = rnd(2, 5);
    const k = rnd(2, dif === "easy" ? 4 : 8);
    if (dif === "hard") {
      const price = rnd(5, 19) / 2; // $2.50 … $9.50
      return {
        display: `If ${a} apples cost $${price.toFixed(2)}, how much do ${a * k} apples cost?`,
        answer: `$${(price * k).toFixed(2)}`,
      };
    }
    const b = rnd(2, dif === "easy" ? 6 : 9);
    return {
      display: `If ${a} apples cost $${b}, how much do ${a * k} apples cost?`,
      answer: `$${b * k}`,
    };
  },
  (dif) => {
    const cm = rnd(2, 5);
    const k = rnd(2, dif === "easy" ? 4 : 8);
    if (dif === "hard") {
      const km = rnd(5, 15) / 2; // 2.5 … 7.5 km per cm-group
      return {
        display: `On a map, ${cm} cm represents ${km % 1 === 0 ? km : km.toFixed(1)} km. How many km does ${cm * k} cm represent?`,
        answer: `${Number.isInteger(km * k) ? km * k : (km * k).toFixed(1)} km`,
      };
    }
    const km = rnd(3, dif === "easy" ? 8 : 12);
    return {
      display: `On a map, ${cm} cm represents ${km} km. How many km does ${cm * k} cm represent?`,
      answer: `${km * k} km`,
    };
  },
  (dif) => {
    const b = rnd(2, 5);
    const k = rnd(2, dif === "easy" ? 4 : 7);
    if (dif === "hard") {
      const cups = rnd(3, 9) / 2; // 1.5 … 4.5 cups
      return {
        display: `A recipe uses ${cups % 1 === 0 ? cups : cups.toFixed(1)} cups of flour per ${b} cups of sugar. How many cups of flour for ${b * k} cups of sugar?`,
        answer: `${Number.isInteger(cups * k) ? cups * k : (cups * k).toFixed(1)} cups`,
      };
    }
    const a = rnd(3, dif === "easy" ? 7 : 9);
    return {
      display: `A recipe uses ${a} cups of flour per ${b} cups of sugar. How many cups of flour for ${b * k} cups of sugar?`,
      answer: `${a * k} cups`,
    };
  },
  (dif) => {
    const a = rnd(2, 4);
    const b = rnd(5, dif === "easy" ? 9 : 14);
    const k = rnd(2, dif === "easy" ? 4 : 6);
    return {
      display: `A car travels ${a * k * b} miles in ${a * k} hours. At the same rate, how many miles in ${a} hours?`,
      answer: `${a * b} miles`,
    };
  },
];

function makePropWord(opts: FluencyOptions, idx: number): Problem {
  const pick = PROPORTION_WORDS[rnd(0, PROPORTION_WORDS.length - 1)];
  const r = pick(opts.difficulty);
  return { num: idx, display: r.display, answer: r.answer };
}

// ----- Tier 6: Absolute Value -----

function makeAbsSimple(opts: FluencyOptions, idx: number): Problem {
  const a = rndCoef(opts, negsFor(opts));
  const b = rnd(1, opts.difficulty === "easy" ? 9 : opts.difficulty === "medium" ? 15 : 24);
  const x1 = b - a;
  const x2 = -b - a;
  return {
    num: idx,
    display: `|x ${fmtAddConst(a)}| = ${b}`,
    answer: `x = ${x1} or x = ${x2}`,
  };
}

function makeAbsCoef(opts: FluencyOptions, idx: number): Problem {
  const a = Math.abs(rndCoef(opts, false)) || 2;
  const b = rndCoef(opts, negsFor(opts));
  const c = rnd(1, opts.difficulty === "easy" ? 9 : opts.difficulty === "medium" ? 15 : 24);
  // |ax + b| = c → ax + b = ±c → x = (±c − b)/a
  const x1Num = c - b;
  const x2Num = -c - b;
  return {
    num: idx,
    display: `|${fmtCoefTerm(a)} ${fmtAddConst(b)}| = ${c}`,
    answer: `${fmtSolution(x1Num, a)} or ${fmtSolution(x2Num, a)}`,
  };
}

function makeAbsIsolate(opts: FluencyOptions, idx: number): Problem {
  const a = Math.abs(rndCoef(opts, false)) || 2;
  const b = rndCoef(opts, negsFor(opts));
  const c = rnd(2, 5); // multiplier outside
  const d = rndConst(opts, negsFor(opts));
  const k = rnd(1, opts.difficulty === "easy" ? 4 : opts.difficulty === "medium" ? 8 : 12); // |…| equals k
  const e = c * k + d;
  // After isolating: |ax + b| = k → ax + b = ±k
  const x1Num = k - b;
  const x2Num = -k - b;
  return {
    num: idx,
    display: `${c}|${fmtCoefTerm(a)} ${fmtAddConst(b)}| ${fmtAddConst(d)} = ${e}`,
    answer: `${fmtSolution(x1Num, a)} or ${fmtSolution(x2Num, a)}`,
  };
}

// ----- Tier 7: Systems of Equations -----

function makeSysSub(opts: FluencyOptions, idx: number): Problem {
  // Build a 2×2 with integer solution (x, y). Display two lines via \n.
  const x = rndSolution(opts, negsFor(opts));
  const y = rndSolution(opts, negsFor(opts));
  const a1 = rndCoef(opts, negsFor(opts));
  const b1 = rndCoef(opts, negsFor(opts));
  const c1 = a1 * x + b1 * y;
  // Second equation: keep it different. Often "y = …" form so substitution
  // is the natural route.
  const m = rndCoef(opts, negsFor(opts));
  const k = y - m * x;
  const eq2 = `y = ${fmtCoefTerm(m)} ${fmtAddConst(k)}`;
  return {
    num: idx,
    display: `${fmtCoefTerm(a1)} ${fmtAddCoef(b1, "y")} = ${c1}\n${eq2}`,
    answer: `(${x}, ${y})`,
  };
}

function makeSysElim(opts: FluencyOptions, idx: number): Problem {
  // Elimination-effort ladder:
  //   easy   — the y-coefficients are already opposites (just add)
  //   medium — one equation must be multiplied first
  //   hard   — both equations usually need multiplying
  const x = rndSolution(opts, negsFor(opts));
  const y = rndSolution(opts, negsFor(opts));
  const a1 = rndCoef(opts, negsFor(opts));
  const b1 = rndCoef(opts, negsFor(opts));
  let a2: number;
  let b2: number;
  if (opts.difficulty === "easy") {
    a2 = rndCoef(opts, false);
    b2 = -b1; // add the equations and y drops out
    if (a1 === -a2) a2 += 1; // keep x from also cancelling
  } else if (opts.difficulty === "medium") {
    // b2 is a small multiple of b1 (opposite sign) → scale one equation.
    b2 = -b1 * rnd(2, 3);
    a2 = rndCoef(opts, true);
  } else {
    a2 = rndCoef(opts, true);
    b2 = rndCoef(opts, true);
    // Avoid accidentally-easy setups where the coefficients already
    // match, and degenerate (parallel) systems.
    if (Math.abs(b2) === Math.abs(b1)) b2 += b2 > 0 ? 1 : -1;
  }
  if (a1 * b2 - a2 * b1 === 0) b2 += 1; // avoid parallel lines
  const c1 = a1 * x + b1 * y;
  const c2 = a2 * x + b2 * y;
  return {
    num: idx,
    display: `${fmtCoefTerm(a1)} ${fmtAddCoef(b1, "y")} = ${c1}\n${fmtCoefTerm(a2)} ${fmtAddCoef(b2, "y")} = ${c2}`,
    answer: `(${x}, ${y})`,
  };
}

function makeSysSpecial(opts: FluencyOptions, idx: number): Problem {
  // A third each: no solution, infinitely many, and exactly one
  // solution. The second equation is always a scaled multiple so the
  // relationship isn't visible until the student compares the ratios —
  // the old version reused the identical left side, which gave the
  // answer away at a glance.
  const outcome = rnd(0, 2); // 0 = none, 1 = infinite, 2 = one
  const a = rndCoef(opts, negsFor(opts));
  const b = rndCoef(opts, negsFor(opts));
  const c = rndConst(opts, negsFor(opts));
  const k = rnd(2, opts.difficulty === "easy" ? 2 : 3) * (opts.difficulty === "hard" && randomBool() ? -1 : 1);
  if (outcome === 0) {
    // Scaled LHS, mismatched RHS → parallel lines.
    return {
      num: idx,
      display: `${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c}\n${fmtCoefTerm(a * k)} ${fmtAddCoef(b * k, "y")} = ${c * k + rnd(1, 4) * (randomBool() ? 1 : -1)}`,
      answer: "no solution",
    };
  }
  if (outcome === 1) {
    // Fully scaled → the same line written two ways.
    return {
      num: idx,
      display: `${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c}\n${fmtCoefTerm(a * k)} ${fmtAddCoef(b * k, "y")} = ${c * k}`,
      answer: "infinitely many solutions",
    };
  }
  // One solution: build a second equation with a different slope and an
  // integer intersection point.
  const x = rndSolution(opts, negsFor(opts));
  const y = rndSolution(opts, negsFor(opts));
  const c1 = a * x + b * y;
  const a2 = rndCoef(opts, negsFor(opts));
  let b2 = rndCoef(opts, negsFor(opts));
  if (a * b2 - a2 * b === 0) b2 += 1; // ensure the lines actually cross
  const c2 = a2 * x + b2 * y;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c1}\n${fmtCoefTerm(a2)} ${fmtAddCoef(b2, "y")} = ${c2}`,
    answer: `(${x}, ${y})`,
  };
}

const SYSTEM_WORDS: ((d: Difficulty) => { display: string; answer: string })[] = [
  (dif) => {
    const cost1 = rnd(2, dif === "easy" ? 4 : 6);
    const cost2 = cost1 + rnd(2, dif === "easy" ? 4 : 6);
    const nMax = dif === "easy" ? 6 : dif === "medium" ? 12 : 20;
    const n1 = rnd(2, nMax);
    const n2 = rnd(2, nMax);
    return {
      display: `Tickets cost $${cost1} for students and $${cost2} for adults. ${n1 + n2} tickets sold for a total of $${cost1 * n1 + cost2 * n2}. How many of each were sold?`,
      answer: `${n1} student, ${n2} adult`,
    };
  },
  (dif) => {
    const a = rnd(2, dif === "easy" ? 5 : 8);
    const b = a + rnd(1, dif === "easy" ? 3 : 6);
    const k = rnd(2, dif === "easy" ? 5 : dif === "medium" ? 8 : 12);
    const total = (a + b) * k;
    return {
      display: `The sum of two numbers is ${total} and one number is ${(b - a) * k} more than the other. Find the numbers.`,
      answer: `${a * k} and ${b * k}`,
    };
  },
];

function makeSysWord(opts: FluencyOptions, idx: number): Problem {
  const pick = SYSTEM_WORDS[rnd(0, SYSTEM_WORDS.length - 1)];
  const r = pick(opts.difficulty);
  return { num: idx, display: r.display, answer: r.answer };
}

// ----- Tier 8: Quadratics -----
// We use Unicode ² for x² in display strings — renders cleanly in any sans
// or serif font without needing a sup tag.

function makeQuadSqrt(opts: FluencyOptions, idx: number): Problem {
  // x² = c → x = ±√c. Hard: half the problems are NOT perfect squares,
  // so the answer is a simplified radical (x² = 18 → x = ±3√2).
  if (opts.difficulty === "hard" && randomBool()) {
    const r = rnd(2, 6);
    const s = [2, 3, 5][rnd(0, 2)];
    return { num: idx, display: `x² = ${r * r * s}`, answer: `x = ±${r}√${s}` };
  }
  const r = rnd(2, opts.difficulty === "easy" ? 9 : opts.difficulty === "medium" ? 13 : 16);
  const c = r * r;
  return { num: idx, display: `x² = ${c}`, answer: `x = ±${r}` };
}

function makeQuadTrans(opts: FluencyOptions, idx: number): Problem {
  // (x − h)² = k where k is a perfect square
  const h = rndConst(opts, negsFor(opts));
  const r = rnd(1, opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 10 : 13);
  const k = r * r;
  const hStr = h < 0 ? `+ ${Math.abs(h)}` : `− ${h}`;
  return {
    num: idx,
    display: `(x ${hStr})² = ${k}`,
    answer: `x = ${h + r} or x = ${h - r}`,
  };
}

function makeQuadFacA1(opts: FluencyOptions, idx: number): Problem {
  // x² + bx + c = 0 with integer roots r1, r2
  const r1 = rndSolution(opts, negsFor(opts));
  let r2 = rndSolution(opts, negsFor(opts));
  if (r2 === r1) r2 += 1;
  const b = -(r1 + r2);
  const c = r1 * r2;
  return {
    num: idx,
    display: `x² ${fmtAddCoef(b)} ${fmtAddConst(c)} = 0`,
    answer: `x = ${r1} or x = ${r2}`,
  };
}

function makeQuadFacAn(opts: FluencyOptions, idx: number): Problem {
  // (ax − p)(x − q) = 0  → ax² − (aq + p)x + pq = 0
  // Roots: x = p/a (rational) and x = q (integer)
  const a = rnd(2, 3);
  const p = rndSolution(opts, negsFor(opts));
  const q = rndSolution(opts, negsFor(opts));
  const bCoef = -(a * q + p);
  const cConst = p * q;
  return {
    num: idx,
    display: `${a}x² ${fmtAddCoef(bCoef)} ${fmtAddConst(cConst)} = 0`,
    answer: `${fmtSolution(p, a)} or x = ${q}`,
  };
}

function makeQuadDiff(opts: FluencyOptions, idx: number): Problem {
  // a²x² − b² = 0 → x = ±b/a
  const a = rnd(2, opts.difficulty === "easy" ? 4 : opts.difficulty === "medium" ? 6 : 8);
  const b = rnd(2, opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 9 : 12);
  return {
    num: idx,
    display: `${a * a}x² − ${b * b} = 0`,
    answer: `${fmtSolution(b, a)} or ${fmtSolution(-b, a)}`,
  };
}

function makeQuadFormula(opts: FluencyOptions, idx: number): Problem {
  // Generate ax² + bx + c with non-perfect-square discriminant so the
  // formula must be used. Answer rendered as x = (−b ± √D) / (2a).
  const a = rnd(1, opts.difficulty === "easy" ? 2 : 3);
  const b = rndCoef(opts, negsFor(opts));
  const c = rndConst(opts, negsFor(opts));
  const D = b * b - 4 * a * c;
  // Ensure D > 0 and not a perfect square.
  if (D <= 0 || Math.sqrt(D) === Math.floor(Math.sqrt(D))) {
    // Fall back to a known irrational example.
    return {
      num: idx,
      display: `x² + 3x + 1 = 0`,
      answer: `x = (−3 ± √5) / 2`,
    };
  }
  return {
    num: idx,
    display: `${a === 1 ? "" : a}x² ${fmtAddCoef(b)} ${fmtAddConst(c)} = 0`,
    answer: `x = (${-b} ± √${D}) / ${2 * a}`,
  };
}

function makeQuadComplete(opts: FluencyOptions, idx: number): Problem {
  // x² + bx + c = 0 with even b so (b/2)² is integer.
  let bHalf = rndCoef(opts, negsFor(opts));
  if (bHalf === 0) bHalf = 1;
  const b = 2 * bHalf;
  // Pick a target k such that (x + bHalf)² = k has integer answers.
  const r = rnd(1, opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 8 : 11);
  const k = r * r;
  // x² + bx + c = 0 → x² + bx = −c → x² + bx + (b/2)² = (b/2)² − c
  // (x + b/2)² = (b/2)² − c = k → c = (b/2)² − k = bHalf² − r²
  const c = bHalf * bHalf - k;
  return {
    num: idx,
    display: `x² ${fmtAddCoef(b)} ${fmtAddConst(c)} = 0`,
    answer: `x = ${-bHalf + r} or x = ${-bHalf - r}`,
  };
}

// ----- Tier 9: Radicals -----

function makeRadSingle(opts: FluencyOptions, idx: number): Problem {
  // √(ax + b) = c → ax + b = c² → x = (c² − b)/a
  const a = Math.abs(rndCoef(opts, false)) || 1;
  const c = rnd(2, opts.difficulty === "easy" ? 7 : opts.difficulty === "medium" ? 10 : 13);
  const x = rndSolution(opts, negsFor(opts));
  const b = c * c - a * x;
  return {
    num: idx,
    display: `√(${fmtCoefTerm(a)} ${fmtAddConst(b)}) = ${c}`,
    answer: `x = ${x}`,
  };
}

function makeRadDouble(opts: FluencyOptions, idx: number): Problem {
  // √(ax + b) = √(cx + d) → ax + b = cx + d → x = (d − b)/(a − c)
  const a = rndCoef(opts, negsFor(opts));
  let c = rndCoef(opts, negsFor(opts));
  if (c === a) c += 1;
  const x = rndSolution(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  const d = (a - c) * x + b;
  return {
    num: idx,
    display: `√(${fmtCoefTerm(a)} ${fmtAddConst(b)}) = √(${fmtCoefTerm(c)} ${fmtAddConst(d)})`,
    answer: `x = ${x}`,
  };
}

function makeRadLinear(opts: FluencyOptions, idx: number): Problem {
  // √(x + a) = x − b. Picking integer a, b with x − b ≥ 0 and x + a = (x − b)²
  // gives a clean quadratic. We pre-pick the "valid" root and verify the
  // extraneous one.
  const x = rnd(opts.difficulty === "easy" ? 3 : 4, 9);
  const b = rnd(1, x - 1);
  const a = (x - b) * (x - b) - x;
  const aStr = a < 0 ? `− ${Math.abs(a)}` : `+ ${a}`;
  const bStr = b < 0 ? `+ ${Math.abs(b)}` : `− ${b}`;
  return {
    num: idx,
    display: `√(x ${aStr}) = x ${bStr}`,
    answer: `x = ${x}  (check for extraneous)`,
  };
}

// ----- Tier 10: Rational Equations -----

function makeRatSimple(opts: FluencyOptions, idx: number): Problem {
  // a/x = b → x = a/b
  const b = Math.abs(rndCoef(opts, false)) || 1;
  const x = rndSolution(opts, negsFor(opts));
  const a = b * x;
  return { num: idx, display: `${a}/x = ${b}`, answer: `x = ${x}` };
}

function makeRatLinear(opts: FluencyOptions, idx: number): Problem {
  // (ax + b)/c = d → ax + b = cd → x = (cd − b)/a
  const a = Math.abs(rndCoef(opts, false)) || 1;
  const c = Math.abs(rndCoef(opts, false)) || 1;
  const x = rndSolution(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  const d = (a * x + b) / c;
  // We need d to be integer for a clean problem — back off and force.
  const dInt = Math.round(d);
  const xCorrected = (c * dInt - b) / a;
  if (!Number.isInteger(xCorrected)) {
    return {
      num: idx,
      display: `(2x + 4)/3 = 6`,
      answer: `x = 7`,
    };
  }
  return {
    num: idx,
    display: `(${fmtCoefTerm(a)} ${fmtAddConst(b)})/${c} = ${dInt}`,
    answer: `x = ${xCorrected}`,
  };
}

function makeRatLCD(opts: FluencyOptions, idx: number): Problem {
  // 1/x + 1/p = 1/q form. Solve: 1/x = 1/q − 1/p = (p − q)/(pq)
  // → x = pq/(p − q). Pick p, q so this is integer.
  const cap = opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 10 : 12;
  const p = rnd(2, cap);
  let q = rnd(2, cap);
  if (p === q) q += 1;
  const diff = p - q;
  if (diff === 0) return { num: idx, display: `1/x + 1/3 = 1/2`, answer: `x = 6` };
  const x = Math.round((p * q) / diff);
  if (!Number.isInteger((p * q) / diff)) {
    return { num: idx, display: `1/x + 1/3 = 1/2`, answer: `x = 6` };
  }
  return {
    num: idx,
    display: `1/x + 1/${p} = 1/${q}`,
    answer: `x = ${x}`,
  };
}

// ----- Tier 11: Exponential (matching bases) -----

function makeExpBases(opts: FluencyOptions, idx: number): Problem {
  // Pick a base b and an exponent answer x. Right side is b^x written as a
  // number ("2^x = 32"). The tokenizer renders ^X as a superscript.
  const base = [2, 3, 5][rnd(0, 2)];
  const xMax = opts.difficulty === "easy" ? 5 : opts.difficulty === "medium" ? 7 : 9;
  const x = rnd(2, xMax);
  const value = Math.pow(base, x);
  return { num: idx, display: `${base}^x = ${value}`, answer: `x = ${x}` };
}

// ───────────────────────────────────────────────────────────
//                       INEQUALITIES
// ───────────────────────────────────────────────────────────

type IneqOp = "<" | ">" | "≤" | "≥";

function pickIneqOp(): IneqOp {
  return (["<", ">", "≤", "≥"] as const)[rnd(0, 3)];
}

function flipOp(op: IneqOp): IneqOp {
  return op === "<" ? ">" : op === ">" ? "<" : op === "≤" ? "≥" : "≤";
}

// ----- Tier 1: One-Step Inequalities -----

function makeIneqOneAdd(opts: FluencyOptions, idx: number): Problem {
  const op = pickIneqOp();
  // Hard: half the problems use one-place decimals (exact tenths math).
  if (opts.difficulty === "hard" && randomBool()) {
    const a10 = rnd(11, 99);
    const x10 = rnd(11, 99) * (randomBool() ? 1 : -1);
    return {
      num: idx,
      display: `x + ${fmtTenths(a10)} ${op} ${fmtTenths(x10 + a10)}`,
      answer: `x ${op} ${fmtTenths(x10)}`,
    };
  }
  const a = rndCoef(opts, false);
  const x = rndSolution(opts, negsFor(opts));
  const b = x + a;
  return {
    num: idx,
    display: `x + ${a} ${op} ${b}`,
    answer: `x ${op} ${x}`,
  };
}

function makeIneqOneSub(opts: FluencyOptions, idx: number): Problem {
  const op = pickIneqOp();
  if (opts.difficulty === "hard" && randomBool()) {
    const a10 = rnd(11, 99);
    const x10 = rnd(11, 99) * (randomBool() ? 1 : -1);
    return {
      num: idx,
      display: `x − ${fmtTenths(a10)} ${op} ${fmtTenths(x10 - a10)}`,
      answer: `x ${op} ${fmtTenths(x10)}`,
    };
  }
  const a = rndCoef(opts, false);
  const x = rndSolution(opts, negsFor(opts));
  const b = x - a;
  return {
    num: idx,
    display: `x − ${a} ${op} ${b}`,
    answer: `x ${op} ${x}`,
  };
}

function makeIneqOneMul(opts: FluencyOptions, idx: number): Problem {
  // ax (op) b → x (op) b/a if a>0; x (flipped) b/a if a<0.
  // Easy keeps a positive (no flip yet); medium mixes negative a in;
  // hard adds decimal / fraction coefficients.
  const op = pickIneqOp();
  if (opts.difficulty === "hard" && randomBool()) {
    if (randomBool()) {
      const a10 = [5, 15, 25][rnd(0, 2)] * (randomBool() ? 1 : -1);
      const x = rnd(1, 9) * (randomBool() ? 1 : -1);
      const outOp = a10 < 0 ? flipOp(op) : op;
      return {
        num: idx,
        display: `${fmtTenths(a10)}x ${op} ${fmtTenths(a10 * x)}`,
        answer: `x ${outOp} ${x}`,
      };
    }
    const d = rnd(2, 5);
    const sign = randomBool() ? 1 : -1;
    const m = rnd(1, 6) * (randomBool() ? 1 : -1);
    const x = m * d;
    const b = sign * m;
    const outOp = sign < 0 ? flipOp(op) : op;
    return {
      num: idx,
      display: `${sign < 0 ? "−" : ""}1/${d}x ${op} ${b}`,
      answer: `x ${outOp} ${x}`,
    };
  }
  const a = rndCoef(opts, negsFor(opts));
  const x = rndSolution(opts, negsFor(opts));
  const b = a * x;
  const outOp = a < 0 ? flipOp(op) : op;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${op} ${b}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqOneDiv(opts: FluencyOptions, idx: number): Problem {
  // x/a (op) b → x (op) ab if a>0; x (flipped) ab if a<0.
  const op = pickIneqOp();
  // Hard: half the problems put a fraction on the right side.
  if (opts.difficulty === "hard" && randomBool()) {
    const d = rnd(2, 4);
    const m = rnd(2, 5);
    const a = d * m;
    let n = rnd(1, 2 * d - 1);
    while (gcd(n, d) !== 1) n += 1;
    if (randomBool()) n = -n;
    return {
      num: idx,
      display: `x/${a} ${op} ${fmtSimpleFrac(n, d)}`,
      answer: `x ${op} ${m * n}`,
    };
  }
  const a = rndCoef(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  const x = a * b;
  const outOp = a < 0 ? flipOp(op) : op;
  return {
    num: idx,
    display: `x/${a < 0 ? `(${a})` : a} ${op} ${b}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqOneMixed(opts: FluencyOptions, idx: number): Problem {
  const which = rnd(0, 3);
  if (which === 0) return makeIneqOneAdd(opts, idx);
  if (which === 1) return makeIneqOneSub(opts, idx);
  if (which === 2) return makeIneqOneMul(opts, idx);
  return makeIneqOneDiv(opts, idx);
}

// ----- Tier 2: Two-Step Inequalities -----

function makeIneqTwoPos(opts: FluencyOptions, idx: number): Problem {
  const op = pickIneqOp();
  // Hard: mixes in one-place decimal coefficients (still all positive).
  if (opts.difficulty === "hard" && randomBool()) {
    const a10 = [5, 15, 25, 12][rnd(0, 3)];
    const x = rnd(1, 9);
    const b = rnd(1, 15);
    return {
      num: idx,
      display: `${fmtTenths(a10)}x ${fmtAddConst(b)} ${op} ${fmtTenths(a10 * x + b * 10)}`,
      answer: `x ${op} ${x}`,
    };
  }
  const a = Math.abs(rndCoef(opts, false)) || 1;
  const b = Math.abs(rndConst(opts, false));
  const x = Math.abs(rndSolution(opts, false));
  const c = a * x + b;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} ${op} ${c}`,
    answer: `x ${op} ${x}`,
  };
}

function makeIneqTwoNeg(opts: FluencyOptions, idx: number): Problem {
  // Force the coefficient to be negative so the sign flip happens.
  const op = pickIneqOp();
  // Hard: mixes in negative decimal coefficients.
  if (opts.difficulty === "hard" && randomBool()) {
    const a10 = -[5, 15, 25, 12][rnd(0, 3)];
    const x = rnd(1, 9) * (randomBool() ? 1 : -1);
    const b = rnd(1, 15) * (randomBool() ? 1 : -1);
    return {
      num: idx,
      display: `${fmtTenths(a10)}x ${fmtAddConst(b)} ${op} ${fmtTenths(a10 * x + b * 10)}`,
      answer: `x ${flipOp(op)} ${x}`,
    };
  }
  let a = rndCoef(opts, true);
  if (a > 0) a = -a;
  const b = rndConst(opts, true);
  const x = rndSolution(opts, true);
  const c = a * x + b;
  const outOp = flipOp(op);
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} ${op} ${c}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqTwoRational(opts: FluencyOptions, idx: number): Problem {
  // Same ladder as the two-step rational equations, with flips:
  //   easy   — unit-fraction coefficient, all positive
  //   medium — proper-fraction coefficient, signs mixed (flips appear)
  //   hard   — adds decimal coefficients to the rotation
  // (Implied multiplication — no "·" between fraction and variable.)
  const op = pickIneqOp();
  if (opts.difficulty === "easy") {
    const d = [2, 3, 4, 5, 6][rnd(0, 4)];
    const b = rnd(1, 9);
    const x = rnd(1, 8) * d;
    const c = x / d + b;
    return {
      num: idx,
      display: `1/${d}x ${fmtAddConst(b)} ${op} ${c}`,
      answer: `x ${op} ${x}`,
    };
  }
  if (opts.difficulty === "medium" || randomBool()) {
    const d = rnd(2, 6);
    let n = rnd(1, d - 1);
    while (gcd(n, d) !== 1) n += 1;
    if (randomBool()) n = -n;
    const b = rnd(1, 12) * (randomBool() ? 1 : -1);
    const m = rnd(1, 6) * (randomBool() ? 1 : -1);
    const x = m * d;
    const c = n * m + b;
    const coefStr = n < 0 ? `−${Math.abs(n)}/${d}` : `${n}/${d}`;
    const outOp = n < 0 ? flipOp(op) : op;
    return {
      num: idx,
      display: `${coefStr}x ${fmtAddConst(b)} ${op} ${c}`,
      answer: `x ${outOp} ${x}`,
    };
  }
  const a10 = [5, 15, 25, 12][rnd(0, 3)] * (randomBool() ? 1 : -1);
  const x = rnd(1, 9) * (randomBool() ? 1 : -1);
  const b = rnd(1, 12) * (randomBool() ? 1 : -1);
  const outOp = a10 < 0 ? flipOp(op) : op;
  return {
    num: idx,
    display: `${fmtTenths(a10)}x ${fmtAddConst(b)} ${op} ${fmtTenths(a10 * x + b * 10)}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqTwoDist(opts: FluencyOptions, idx: number): Problem {
  const op = pickIneqOp();
  // Hard: half the problems distribute a unit fraction.
  if (opts.difficulty === "hard" && randomBool()) {
    const d = [2, 3, 4][rnd(0, 2)];
    const sign = randomBool() ? 1 : -1;
    const x = rnd(1, 9) * (randomBool() ? 1 : -1);
    let q = rnd(1, 8) * (randomBool() ? 1 : -1);
    q += (d - ((((x + q) % d) + d) % d)) % d;
    const r = (sign * (x + q)) / d;
    const outOp = sign < 0 ? flipOp(op) : op;
    const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
    return {
      num: idx,
      display: `${sign === -1 ? "−" : ""}1/${d}(x ${qStr}) ${op} ${r}`,
      answer: `x ${outOp} ${x}`,
    };
  }
  // p(x + q) (op) r
  const p = rndCoef(opts, negsFor(opts));
  const q = rndConst(opts, negsFor(opts));
  const x = rndSolution(opts, negsFor(opts));
  const r = p * (x + q);
  const outOp = p < 0 ? flipOp(op) : op;
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${op} ${r}`,
    answer: `x ${outOp} ${x}`,
  };
}

// ----- Tier 3: Multi-Step Inequalities -----

function makeIneqMultiCombine(opts: FluencyOptions, idx: number): Problem {
  // ax + bx + c (op) d
  const a = rndCoef(opts, negsFor(opts));
  let b = rndCoef(opts, negsFor(opts));
  if (a + b === 0) b += 1;
  const c = rndConst(opts, negsFor(opts));
  const op = pickIneqOp();
  const x = rndSolution(opts, negsFor(opts));
  const d = (a + b) * x + c;
  const outOp = a + b < 0 ? flipOp(op) : op;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddCoef(b)} ${fmtAddConst(c)} ${op} ${d}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqMultiDist(opts: FluencyOptions, idx: number): Problem {
  // p(x + q) + r (op) s
  const p = rndCoef(opts, negsFor(opts));
  const q = rndConst(opts, negsFor(opts));
  const r = rndConst(opts, negsFor(opts));
  const op = pickIneqOp();
  const x = rndSolution(opts, negsFor(opts));
  const s = p * (x + q) + r;
  const outOp = p < 0 ? flipOp(op) : op;
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)} ${op} ${s}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqMultiBoth(opts: FluencyOptions, idx: number): Problem {
  // ax + b (op) cx + d → (a−c)x (op) d − b
  const a = rndCoef(opts, negsFor(opts));
  let c = rndCoef(opts, negsFor(opts));
  if (a === c) c += 1;
  const x = rndSolution(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  const d = (a - c) * x + b;
  const op = pickIneqOp();
  const outOp = a - c < 0 ? flipOp(op) : op;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} ${op} ${fmtCoefTerm(c)} ${fmtAddConst(d)}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqMultiFull(opts: FluencyOptions, idx: number): Problem {
  // p(x + q) + r (op) sx + t
  const p = rndCoef(opts, negsFor(opts));
  const q = rndConst(opts, negsFor(opts));
  const r = rndConst(opts, negsFor(opts));
  let s = rndCoef(opts, negsFor(opts));
  if (p === s) s += 1;
  const x = rndSolution(opts, negsFor(opts));
  const t = p * (x + q) + r - s * x;
  const op = pickIneqOp();
  const outOp = p - s < 0 ? flipOp(op) : op;
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)} ${op} ${fmtCoefTerm(s)} ${fmtAddConst(t)}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqMultiSpecial(opts: FluencyOptions, idx: number): Problem {
  // A third each: no solution, all real numbers, and a regular one-
  // boundary solution — always with like terms to combine or a group
  // to distribute so the outcome isn't visible until after simplifying.
  const outcome = rnd(0, 2); // 0 = no solution, 1 = all real, 2 = solve
  const sgn = () => (randomBool() ? 1 : -1);
  const op = pickIneqOp();

  // Left side: easy combines like terms; medium/hard distribute.
  let lhsSlope: number;
  let lhsConst: number;
  let lhs: string;
  if (opts.difficulty === "easy") {
    const a = rnd(2, 6);
    let b = rnd(1, 5) * sgn();
    if (a + b === 0) b += 1;
    const c = rnd(1, 12);
    lhsSlope = a + b;
    lhsConst = c;
    lhs = `${fmtCoefTerm(a)} ${fmtAddCoef(b)} ${fmtAddConst(c)}`;
  } else {
    const p = rnd(2, opts.difficulty === "hard" ? 7 : 6) * (opts.difficulty === "hard" ? sgn() : 1);
    const q = rnd(1, 6) * sgn();
    const r = rnd(1, 9) * sgn();
    const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
    lhsSlope = p;
    lhsConst = p * q + r;
    lhs = `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)}`;
  }

  if (outcome === 2) {
    // Regular solve: RHS slope differs, so a boundary exists.
    let s = rnd(1, 6) * sgn();
    if (s === lhsSlope) s += 1;
    const x = rnd(1, 9) * sgn();
    const e = (lhsSlope - s) * x + lhsConst;
    const outOp = lhsSlope - s < 0 ? flipOp(op) : op;
    return {
      num: idx,
      display: `${lhs} ${op} ${fmtCoefTerm(s)} ${fmtAddConst(e)}`,
      answer: `x ${outOp} ${x}`,
    };
  }

  // Special outcomes: same slope on both sides; the constants decide.
  // After subtracting the x-terms: lhsConst (op) rhsConst.
  const wantTrue = outcome === 1; // true statement → all real numbers
  const lessOp = op === "<" || op === "≤";
  const delta = rnd(1, 6);
  // Pick rhsConst so the constant comparison is true/false as needed.
  const rhsConst = wantTrue === lessOp ? lhsConst + delta : lhsConst - delta;
  return {
    num: idx,
    display: `${lhs} ${op} ${fmtCoefTerm(lhsSlope)} ${fmtAddConst(rhsConst)}`,
    answer: wantTrue ? "all real numbers" : "no solution",
  };
}

// ----- Tier 4: Compound Inequalities -----

function makeIneqCompoundAnd(opts: FluencyOptions, idx: number): Problem {
  // Build: a < x + k < b  →  a − k < x < b − k
  const k = rndCoef(opts, negsFor(opts));
  const lo = rndConst(opts, negsFor(opts));
  const range = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 11 : 14;
  const hi = lo + rnd(2, range);
  const kStr = k >= 0 ? `+ ${k}` : `− ${Math.abs(k)}`;
  return {
    num: idx,
    display: `${lo} < x ${kStr} < ${hi}`,
    answer: `${lo - k} < x < ${hi - k}`,
  };
}

function makeIneqCompoundOr(opts: FluencyOptions, idx: number): Problem {
  // x + k < a  OR  x + k > b
  const k = rndCoef(opts, negsFor(opts));
  const a = rndConst(opts, negsFor(opts));
  const b = a + rnd(3, opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 10 : 14);
  const kStr = k >= 0 ? `+ ${k}` : `− ${Math.abs(k)}`;
  return {
    num: idx,
    display: `x ${kStr} < ${a}   or   x ${kStr} > ${b}`,
    answer: `x < ${a - k}  or  x > ${b - k}`,
  };
}

const COMPOUND_PHRASES: ((opts: FluencyOptions) => { display: string; answer: string })[] = [
  (opts) => {
    const a = rnd(opts.allowNegatives ? -8 : 1, 5);
    const b = a + rnd(3, 8);
    return {
      display: `x is greater than ${a} and less than ${b}.`,
      answer: `${a} < x < ${b}`,
    };
  },
  (opts) => {
    const a = rnd(opts.allowNegatives ? -8 : 1, 5);
    const b = a + rnd(3, 8);
    return {
      display: `x is at least ${a} and at most ${b}.`,
      answer: `${a} ≤ x ≤ ${b}`,
    };
  },
  (opts) => {
    const a = rnd(opts.allowNegatives ? -5 : 1, 4);
    const b = a + rnd(4, 9);
    return {
      display: `x is less than ${a} or greater than ${b}.`,
      answer: `x < ${a}  or  x > ${b}`,
    };
  },
  (opts) => {
    const a = rnd(opts.allowNegatives ? -5 : 1, 5);
    return {
      display: `x is no more than ${a}.`,
      answer: `x ≤ ${a}`,
    };
  },
  (opts) => {
    const a = rnd(opts.allowNegatives ? -5 : 1, 5);
    return {
      display: `x is at least ${a}.`,
      answer: `x ≥ ${a}`,
    };
  },
];

function makeIneqCompoundTranslate(opts: FluencyOptions, idx: number): Problem {
  const pick = COMPOUND_PHRASES[rnd(0, COMPOUND_PHRASES.length - 1)];
  const r = pick(opts);
  return { num: idx, display: r.display, answer: r.answer };
}

// ----- Tier 5: Absolute Value Inequalities -----

function makeIneqAbsLess(opts: FluencyOptions, idx: number): Problem {
  // |x + a| < b  →  −b < x + a < b  →  −b − a < x < b − a
  // Also support ≤.
  const a = rndCoef(opts, negsFor(opts));
  const b = rnd(1, opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 11 : 14);
  const op: IneqOp = randomBool() ? "<" : "≤";
  return {
    num: idx,
    display: `|x ${fmtAddConst(a)}| ${op} ${b}`,
    answer: `${-b - a} ${op} x ${op} ${b - a}`,
  };
}

function makeIneqAbsGreater(opts: FluencyOptions, idx: number): Problem {
  // |x + a| > b  →  x + a < −b  OR  x + a > b
  const a = rndCoef(opts, negsFor(opts));
  const b = rnd(1, opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 11 : 14);
  const op: IneqOp = randomBool() ? ">" : "≥";
  return {
    num: idx,
    display: `|x ${fmtAddConst(a)}| ${op} ${b}`,
    answer: `x ${op === ">" ? "<" : "≤"} ${-b - a}  or  x ${op} ${b - a}`,
  };
}

// ───────────────────────────────────────────────────────────
//                        GEOMETRY
// ───────────────────────────────────────────────────────────
// Tier 1: forward problems — given dimensions, find area / perimeter /
// circumference. Tier 2: reverse — given the result, find the missing
// dimension. Each problem carries an inline ShapeSpec the worksheet
// renders next to the question.

const GEO_UNITS = ["cm", "m", "ft", "in"];

function pickUnit(): string {
  return GEO_UNITS[rnd(0, GEO_UNITS.length - 1)];
}

/** Format an answer in terms of π (e.g. 25π cm²). For decimal-style
 *  answers, use `formatPiDecimal`. */
function formatPi(coef: number, unit: string, square = false): string {
  if (coef === 1) return `π ${unit}${square ? "²" : ""}`;
  return `${coef}π ${unit}${square ? "²" : ""}`;
}

// ----- Tier 1 -----

function makeRectArea(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 20 : 30;
  const l = rnd(2, max);
  let w = rnd(2, max);
  while (w === l) w = rnd(2, max); // avoid accidentally a square
  return {
    num: idx,
    display: "",
    instruction: "Find the area.",
    answer: `${l * w} ${unit}²`,
    shape: {
      kind: "rectangle",
      labels: { length: `${l} ${unit}`, width: `${w} ${unit}` },
    },
  };
}

function makeRectPerim(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 20 : 30;
  const l = rnd(2, max);
  let w = rnd(2, max);
  while (w === l) w = rnd(2, max);
  return {
    num: idx,
    display: "",
    instruction: "Find the perimeter.",
    answer: `${2 * (l + w)} ${unit}`,
    shape: {
      kind: "rectangle",
      labels: { length: `${l} ${unit}`, width: `${w} ${unit}` },
    },
  };
}

function makeSquare(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 20 : 30;
  const s = rnd(2, max);
  const askPerim = randomBool();
  return {
    num: idx,
    display: askPerim ? `Find the perimeter.` : `Find the area.`,
    answer: askPerim ? `${4 * s} ${unit}` : `${s * s} ${unit}²`,
    shape: { kind: "square", labels: { side: `${s} ${unit}` } },
  };
}

function makeTriArea(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 20 : 28;
  // Pick base/height with base × height even so area is an integer.
  let b = rnd(2, max);
  const h = rnd(2, max);
  if ((b * h) % 2 !== 0) b += 1;
  return {
    num: idx,
    display: "",
    instruction: "Find the area.",
    answer: `${(b * h) / 2} ${unit}²`,
    shape: { kind: "triangle", labels: { base: `${b} ${unit}`, height: `${h} ${unit}` } },
  };
}

function makeParallelogramArea(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 20 : 28;
  const b = rnd(2, max);
  const h = rnd(2, max);
  return {
    num: idx,
    display: "",
    instruction: "Find the area.",
    answer: `${b * h} ${unit}²`,
    shape: { kind: "parallelogram", labels: { base: `${b} ${unit}`, height: `${h} ${unit}` } },
  };
}

function makeTrapArea(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 18 : 26;
  let b1 = rnd(4, max);
  let b2 = rnd(2, max);
  if (b1 === b2) b2 = b2 + 1; // distinguish so it doesn't read as a parallelogram
  if (b1 < b2) [b1, b2] = [b2, b1];
  let h = rnd(2, max);
  // Ensure area is integer.
  if (((b1 + b2) * h) % 2 !== 0) h += 1;
  return {
    num: idx,
    display: "",
    instruction: "Find the area.",
    answer: `${((b1 + b2) * h) / 2} ${unit}²`,
    shape: {
      kind: "trapezoid",
      labels: { base1: `${b1} ${unit}`, base2: `${b2} ${unit}`, height: `${h} ${unit}` },
    },
  };
}

function makeCircleArea(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 12 : 15;
  const r = rnd(2, max);
  // Hard: half the circles give the DIAMETER, so students must halve
  // it before squaring.
  const giveDiameter = opts.difficulty === "hard" && randomBool();
  return {
    num: idx,
    display: "",
    instruction: "Find the area in terms of π.",
    answer: formatPi(r * r, unit, true),
    shape: {
      kind: "circle",
      labels: giveDiameter
        ? { diameter: `d = ${2 * r} ${unit}` }
        : { radius: `r = ${r} ${unit}` },
    },
  };
}

function makeCircleCircumference(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 11 : 14;
  const r = rnd(2, max);
  const useDiameter = randomBool();
  return {
    num: idx,
    display: "",
    instruction: "Find the circumference in terms of π.",
    answer: formatPi(2 * r, unit, false),
    shape: {
      kind: "circle",
      labels: useDiameter ? { diameter: `d = ${2 * r} ${unit}` } : { radius: `r = ${r} ${unit}` },
    },
  };
}

// ----- Tier 2 — Reverse / Find Missing Dimension -----

function makeRectFindFromArea(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 18 : 26;
  const w = rnd(2, max);
  const x = rnd(2, max);
  const area = w * x;
  return {
    num: idx,
    display: `The area is ${area} ${unit}². Find the missing side x.`,
    answer: `x = ${x} ${unit}`,
    shape: {
      kind: "rectangle",
      labels: { length: `x`, width: `${w} ${unit}` },
    },
  };
}

function makeRectFindFromPerim(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 18 : 26;
  const w = rnd(2, max);
  const x = rnd(2, max);
  const perim = 2 * (w + x);
  return {
    num: idx,
    display: `The perimeter is ${perim} ${unit}. Find the missing side x.`,
    answer: `x = ${x} ${unit}`,
    shape: { kind: "rectangle", labels: { length: `x`, width: `${w} ${unit}` } },
  };
}

function makeSquareFind(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 10 : opts.difficulty === "medium" ? 14 : 18;
  const s = rnd(2, max);
  const givePerim = randomBool();
  return {
    num: idx,
    display: givePerim
      ? `The perimeter is ${4 * s} ${unit}. Find the side length x.`
      : `The area is ${s * s} ${unit}². Find the side length x.`,
    answer: `x = ${s} ${unit}`,
    shape: { kind: "square", labels: { side: `x` } },
  };
}

function makeTriFindBase(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 18 : 24;
  let b = rnd(2, max);
  const h = rnd(2, max);
  if ((b * h) % 2 !== 0) b += 1;
  const area = (b * h) / 2;
  return {
    num: idx,
    display: `The area is ${area} ${unit}². Find the base x.`,
    answer: `x = ${b} ${unit}`,
    shape: { kind: "triangle", labels: { base: `x`, height: `${h} ${unit}` } },
  };
}

function makeTriFindHeight(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 12 : opts.difficulty === "medium" ? 18 : 24;
  const b = rnd(2, max);
  let h = rnd(2, max);
  if ((b * h) % 2 !== 0) h += 1;
  const area = (b * h) / 2;
  return {
    num: idx,
    display: `The area is ${area} ${unit}². Find the height x.`,
    answer: `x = ${h} ${unit}`,
    shape: { kind: "triangle", labels: { base: `${b} ${unit}`, height: `x` } },
  };
}

function makeCircleFindRFromArea(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 10 : 13;
  const r = rnd(2, max);
  return {
    num: idx,
    display: `The area is ${formatPi(r * r, unit, true)}. Find the radius x.`,
    answer: `x = ${r} ${unit}`,
    shape: { kind: "circle", labels: { radius: `r = x` } },
  };
}

function makeCircleFindRFromCirc(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 10 : 13;
  const r = rnd(2, max);
  return {
    num: idx,
    display: `The circumference is ${formatPi(2 * r, unit, false)}. Find the radius x.`,
    answer: `x = ${r} ${unit}`,
    shape: { kind: "circle", labels: { radius: `r = x` } },
  };
}

// ----- Geometry: Tier 3 — Volume & Surface Area (forward) -----

function makeRectPrismV(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 10 : opts.difficulty === "medium" ? 14 : 18;
  const l = rnd(2, max);
  const w = rnd(2, max);
  const h = rnd(2, max);
  return {
    num: idx,
    display: "",
    instruction: "Find the volume.",
    answer: `${l * w * h} ${unit}³`,
    shape: {
      kind: "rect-prism",
      labels: { length: `${l} ${unit}`, width: `${w} ${unit}`, height: `${h} ${unit}` },
    },
  };
}

function makeRectPrismSA(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 10 : opts.difficulty === "medium" ? 14 : 18;
  const l = rnd(2, max);
  const w = rnd(2, max);
  const h = rnd(2, max);
  const sa = 2 * (l * w + l * h + w * h);
  return {
    num: idx,
    display: "",
    instruction: "Find the surface area.",
    answer: `${sa} ${unit}²`,
    shape: {
      kind: "rect-prism",
      labels: { length: `${l} ${unit}`, width: `${w} ${unit}`, height: `${h} ${unit}` },
    },
  };
}

function makeCube(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 10 : opts.difficulty === "medium" ? 12 : 16;
  const s = rnd(2, max);
  const askSA = randomBool();
  return {
    num: idx,
    display: askSA ? `Find the surface area.` : `Find the volume.`,
    answer: askSA ? `${6 * s * s} ${unit}²` : `${s * s * s} ${unit}³`,
    shape: { kind: "cube", labels: { side: `${s} ${unit}` } },
  };
}

function makeTriPrismV(opts: FluencyOptions, idx: number): Problem {
  // V = (1/2 · base · height) · length
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 10 : opts.difficulty === "medium" ? 14 : 18;
  let b = rnd(2, max);
  const h = rnd(2, max);
  if ((b * h) % 2 !== 0) b += 1;
  const length = rnd(2, max);
  const v = ((b * h) / 2) * length;
  return {
    num: idx,
    display: "",
    instruction: "Find the volume.",
    answer: `${v} ${unit}³`,
    shape: {
      kind: "tri-prism",
      labels: { base: `${b} ${unit}`, triHeight: `${h} ${unit}`, length: `${length} ${unit}` },
    },
  };
}

function makeTriPrismSA(opts: FluencyOptions, idx: number): Problem {
  // SA for an isoceles-style prism: 2·(½bh) + perimeter·length. To keep the
  // arithmetic clean we use a right-triangle base where legs are b and h
  // (so the hypotenuse is √(b² + h²)) and let SA = b·h + (b + h + √(b² + h²))·L.
  // For clean answers, pick a Pythagorean triple as the base.
  const unit = pickUnit();
  const triples: [number, number, number][] = [
    [3, 4, 5], [6, 8, 10], [5, 12, 13], [8, 15, 17], [9, 12, 15],
  ];
  const [b, h, hyp] = triples[rnd(0, triples.length - 1)];
  const length = rnd(2, opts.difficulty === "easy" ? 10 : opts.difficulty === "medium" ? 14 : 18);
  const triArea = (b * h) / 2;
  const sa = 2 * triArea + (b + h + hyp) * length;
  return {
    num: idx,
    display: "",
    instruction: "Find the surface area. (Right-triangle base.)",
    answer: `${sa} ${unit}²`,
    shape: {
      kind: "tri-prism",
      labels: { base: `${b} ${unit}`, triHeight: `${h} ${unit}`, length: `${length} ${unit}` },
    },
  };
}

function makeCylinderV(opts: FluencyOptions, idx: number): Problem {
  // V = π·r²·h. Leave answer in terms of π for clean fluency form.
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 10 : 13;
  const r = rnd(2, max);
  const h = rnd(2, max);
  return {
    num: idx,
    display: "",
    instruction: "Find the volume in terms of π.",
    answer: formatPi(r * r * h, unit, false).replace(unit, `${unit}³`),
    shape: {
      kind: "cylinder",
      labels: { radius: `r = ${r} ${unit}`, height: `h = ${h} ${unit}` },
    },
  };
}

function makeCylinderSA(opts: FluencyOptions, idx: number): Problem {
  // SA = 2π·r² + 2π·r·h = 2π·r·(r + h). Keep in terms of π.
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 10 : 13;
  const r = rnd(2, max);
  const h = rnd(2, max);
  const coef = 2 * r * (r + h);
  return {
    num: idx,
    display: "",
    instruction: "Find the surface area in terms of π.",
    answer: formatPi(coef, unit, true),
    shape: {
      kind: "cylinder",
      labels: { radius: `r = ${r} ${unit}`, height: `h = ${h} ${unit}` },
    },
  };
}

function makeConeV(opts: FluencyOptions, idx: number): Problem {
  // V = (1/3)π·r²·h. Need r²·h divisible by 3 for a clean integer · π answer.
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 8 : 11;
  const r = rnd(2, max);
  let h = rnd(3, max);
  // Force h to be a multiple of 3 if r²·h isn't already.
  if ((r * r * h) % 3 !== 0) h = h - (h % 3) + 3;
  const coef = (r * r * h) / 3;
  return {
    num: idx,
    display: "",
    instruction: "Find the volume in terms of π.",
    answer: formatPi(coef, unit, false).replace(unit, `${unit}³`),
    shape: {
      kind: "cone",
      labels: { radius: `r = ${r} ${unit}`, height: `h = ${h} ${unit}` },
    },
  };
}

function makeSphereV(opts: FluencyOptions, idx: number): Problem {
  // V = (4/3)π·r³. Pick r so 4r³/3 is integer.
  const unit = pickUnit();
  // r being a multiple of 3 makes 4r³/3 integer cleanly.
  const r = [3, 6, 9, 12][rnd(0, opts.difficulty === "easy" ? 1 : opts.difficulty === "medium" ? 2 : 3)];
  const coef = (4 * r * r * r) / 3;
  return {
    num: idx,
    display: "",
    instruction: "Find the volume in terms of π.",
    answer: formatPi(coef, unit, false).replace(unit, `${unit}³`),
    shape: { kind: "sphere", labels: { radius: `r = ${r} ${unit}` } },
  };
}

function makePyramidV(opts: FluencyOptions, idx: number): Problem {
  // V = (1/3)·b²·h for a square-base pyramid (b is the side of the base).
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 10 : 13;
  const b = rnd(2, max);
  let h = rnd(3, max);
  if ((b * b * h) % 3 !== 0) h = h - (h % 3) + 3;
  const v = (b * b * h) / 3;
  return {
    num: idx,
    display: "",
    instruction: "Find the volume of the square pyramid.",
    answer: `${v} ${unit}³`,
    shape: {
      kind: "pyramid",
      labels: { side: `${b} ${unit}`, height: `h = ${h} ${unit}` },
    },
  };
}

// ----- Geometry: Tier 4 — Find Missing Dimension from V/SA -----

function makeRectPrismFindH(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 10 : opts.difficulty === "medium" ? 14 : 18;
  const l = rnd(2, max);
  const w = rnd(2, max);
  const h = rnd(2, max);
  const v = l * w * h;
  return {
    num: idx,
    display: `The volume is ${v} ${unit}³. Find the height x.`,
    answer: `x = ${h} ${unit}`,
    shape: {
      kind: "rect-prism",
      labels: { length: `${l} ${unit}`, width: `${w} ${unit}`, height: `x` },
    },
  };
}

function makeCubeFindS(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 10 : 13;
  const s = rnd(2, max);
  const giveSA = randomBool();
  return {
    num: idx,
    display: giveSA
      ? `The surface area is ${6 * s * s} ${unit}². Find the side length x.`
      : `The volume is ${s * s * s} ${unit}³. Find the side length x.`,
    answer: `x = ${s} ${unit}`,
    shape: { kind: "cube", labels: { side: `x` } },
  };
}

function makeCylinderFindH(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 7 : opts.difficulty === "medium" ? 9 : 11;
  const r = rnd(2, max);
  const h = rnd(2, max);
  const coef = r * r * h;
  return {
    num: idx,
    display: `The volume is ${formatPi(coef, unit, false).replace(unit, `${unit}³`)}. Find the height x.`,
    answer: `x = ${h} ${unit}`,
    shape: {
      kind: "cylinder",
      labels: { radius: `r = ${r} ${unit}`, height: `h = x` },
    },
  };
}

function makeCylinderFindR(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 7 : 9;
  const r = rnd(2, max);
  const h = rnd(2, max);
  const coef = r * r * h;
  return {
    num: idx,
    display: `The volume is ${formatPi(coef, unit, false).replace(unit, `${unit}³`)} and the height is ${h} ${unit}. Find the radius x.`,
    answer: `x = ${r} ${unit}`,
    shape: {
      kind: "cylinder",
      labels: { radius: `r = x`, height: `h = ${h} ${unit}` },
    },
  };
}

function makeConeFindH(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 5 : opts.difficulty === "medium" ? 6 : 8;
  const r = rnd(2, max);
  let h = rnd(3, max);
  if ((r * r * h) % 3 !== 0) h = h - (h % 3) + 3;
  const coef = (r * r * h) / 3;
  return {
    num: idx,
    display: `The volume is ${formatPi(coef, unit, false).replace(unit, `${unit}³`)} and the radius is ${r} ${unit}. Find the height x.`,
    answer: `x = ${h} ${unit}`,
    shape: {
      kind: "cone",
      labels: { radius: `r = ${r} ${unit}`, height: `h = x` },
    },
  };
}

function makeSphereFindR(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const r = [3, 6, 9, 12][rnd(0, opts.difficulty === "easy" ? 1 : opts.difficulty === "medium" ? 2 : 3)];
  const coef = (4 * r * r * r) / 3;
  return {
    num: idx,
    display: `The volume is ${formatPi(coef, unit, false).replace(unit, `${unit}³`)}. Find the radius x.`,
    answer: `x = ${r} ${unit}`,
    shape: { kind: "sphere", labels: { radius: `r = x` } },
  };
}

// ----- Geometry: Tier 5 — Pythagorean Theorem -----

const PYTH_TRIPLES: [number, number, number][] = [
  [3, 4, 5], [6, 8, 10], [9, 12, 15], [12, 16, 20], [15, 20, 25],
  [5, 12, 13], [10, 24, 26],
  [8, 15, 17], [7, 24, 25], [20, 21, 29],
];

function pickPythTriple(diff: Difficulty): [number, number, number] {
  // Easy: classic 3-4-5 family. Medium: add 5-12-13. Hard: all.
  const easy = PYTH_TRIPLES.slice(0, 5);
  const med = PYTH_TRIPLES.slice(0, 7);
  const pool = diff === "easy" ? easy : diff === "medium" ? med : PYTH_TRIPLES;
  return pool[rnd(0, pool.length - 1)];
}

function makePythHyp(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const [a, b, c] = pickPythTriple(opts.difficulty);
  return {
    num: idx,
    display: "",
    instruction: "Find the length of the hypotenuse c.",
    answer: `c = ${c} ${unit}`,
    shape: {
      kind: "right-triangle",
      labels: { a: `a = ${a} ${unit}`, b: `b = ${b} ${unit}`, c: `c = ?` },
    },
  };
}

function makePythLeg(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const [a, b, c] = pickPythTriple(opts.difficulty);
  // Randomly hide a or b.
  const hideA = randomBool();
  if (hideA) {
    return {
      num: idx,
      display: `Find the length of the missing leg a.`,
      answer: `a = ${a} ${unit}`,
      shape: {
        kind: "right-triangle",
        labels: { a: `a = ?`, b: `b = ${b} ${unit}`, c: `c = ${c} ${unit}` },
      },
    };
  }
  return {
    num: idx,
    display: `Find the length of the missing leg b.`,
    answer: `b = ${b} ${unit}`,
    shape: {
      kind: "right-triangle",
      labels: { a: `a = ${a} ${unit}`, b: `b = ?`, c: `c = ${c} ${unit}` },
    },
  };
}

function makePythCheck(opts: FluencyOptions, idx: number): Problem {
  // 50/50 right vs. not right. For non-right we shift one side ±1 so it
  // fails the Pythagorean check.
  const isRight = randomBool();
  const [a, b, c] = pickPythTriple(opts.difficulty);
  if (isRight) {
    return {
      num: idx,
      display: `Is a triangle with sides ${a}, ${b}, ${c} a right triangle?`,
      answer: `Yes — ${a}² + ${b}² = ${a * a + b * b} = ${c}²`,
    };
  }
  const cBad = c + (randomBool() ? 1 : -1);
  return {
    num: idx,
    display: `Is a triangle with sides ${a}, ${b}, ${cBad} a right triangle?`,
    answer: `No — ${a}² + ${b}² = ${a * a + b * b} ≠ ${cBad * cBad} = ${cBad}²`,
  };
}

// Two template pools: "hyp" problems give both legs and ask for the
// hypotenuse; "leg" problems give the hypotenuse and one leg, so the
// student must work backwards (c² − a² instead of a² + b²). The
// generator alternates between the pools so every worksheet is a real
// mix. Templates use the worksheet's difficulty for the triple.
const PYTH_WORD_HYP: ((d: Difficulty) => { display: string; answer: string })[] = [
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `A rectangular swimming pool is ${a} m by ${b} m. How long is the diagonal?`,
      answer: `${c} m`,
    };
  },
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `A TV screen is ${a} in tall and ${b} in wide. What is the diagonal length?`,
      answer: `${c} in`,
    };
  },
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `Two cars start from the same point. One drives ${a} mi north and the other drives ${b} mi east. How far apart are they?`,
      answer: `${c} mi`,
    };
  },
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `A soccer field is ${a} yd wide and ${b} yd long. How far is it from corner to corner?`,
      answer: `${c} yd`,
    };
  },
];

const PYTH_WORD_LEG: ((d: Difficulty) => { display: string; answer: string })[] = [
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `A ladder ${c} ft long leans against a wall. The bottom is ${a} ft from the wall. How high up the wall does the ladder reach?`,
      answer: `${b} ft`,
    };
  },
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `A ${c}-ft guy wire runs from the top of a pole to a stake ${a} ft from its base. How tall is the pole?`,
      answer: `${b} ft`,
    };
  },
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `A kite is flying on ${c} ft of string, directly above a spot ${a} ft from where the string is held. How high is the kite?`,
      answer: `${b} ft`,
    };
  },
  (d) => {
    const [a, b, c] = pickPythTriple(d);
    return {
      display: `A ${c}-m ramp covers ${b} m of horizontal ground. How high does the ramp rise?`,
      answer: `${a} m`,
    };
  },
];

function makePythWord(opts: FluencyOptions, idx: number): Problem {
  // Alternate: odd problems find the hypotenuse, even problems work
  // backwards to a missing leg. Guarantees a 50/50 mix per worksheet.
  const pool = idx % 2 === 1 ? PYTH_WORD_HYP : PYTH_WORD_LEG;
  const pick = pool[rnd(0, pool.length - 1)];
  const r = pick(opts.difficulty);
  return { num: idx, display: r.display, answer: r.answer };
}

// ----- Geometry: Tier 6 — Coordinate Geometry -----

/** Pick two points whose Δx and Δy form a Pythagorean leg pair so the
 *  distance is a clean integer. */
function pickCoordPair(diff: Difficulty): { p1: [number, number]; p2: [number, number]; dist: number } {
  const [a, b, c] = pickPythTriple(diff);
  const x1 = rnd(diff === "hard" ? -8 : -4, 5);
  const y1 = rnd(diff === "hard" ? -8 : -4, 5);
  // Randomize the sign and orientation so points don't always lie up-right.
  const sx = randomBool() ? 1 : -1;
  const sy = randomBool() ? 1 : -1;
  const flip = randomBool();
  const dx = (flip ? b : a) * sx;
  const dy = (flip ? a : b) * sy;
  return { p1: [x1, y1], p2: [x1 + dx, y1 + dy], dist: c };
}

function makeCoordDistance(opts: FluencyOptions, idx: number): Problem {
  const { p1, p2, dist } = pickCoordPair(opts.difficulty);
  return {
    num: idx,
    display: `Find the distance between (${p1[0]}, ${p1[1]}) and (${p2[0]}, ${p2[1]}).`,
    answer: `${dist}`,
  };
}

function makeCoordMidpoint(opts: FluencyOptions, idx: number): Problem {
  // Ensure midpoint is an integer pair by making both Δx and Δy even.
  const range = opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 10 : 14;
  const x1 = rnd(-range, range);
  const y1 = rnd(-range, range);
  // pick even deltas
  const dx = 2 * rnd(1, range / 2);
  const dy = 2 * rnd(1, range / 2);
  const sx = randomBool() ? 1 : -1;
  const sy = randomBool() ? 1 : -1;
  const x2 = x1 + dx * sx;
  const y2 = y1 + dy * sy;
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  return {
    num: idx,
    display: `Find the midpoint of the segment from (${x1}, ${y1}) to (${x2}, ${y2}).`,
    answer: `(${mx}, ${my})`,
  };
}

// ───────────────────────────────────────────────────────────
//                   GRAPHING & RATES
// ───────────────────────────────────────────────────────────

/** Format a slope value: integers as "5"; fractions as "5/2"; negatives with
 *  the minus on the numerator. */
function fmtSlope(num: number, den: number): string {
  const [n, d] = simplify(num, den);
  if (d === 1) return `${n}`;
  return `${n}/${d}`;
}

/** Render y = mx + b cleanly: omit 1·x, hide +0, handle negative b. */
function fmtMxB(m: number, b: number, mDen: number = 1): string {
  // Slope term
  const [mn, md] = simplify(m, mDen);
  let mTerm: string;
  if (mn === 0) mTerm = "";
  else if (md === 1) {
    if (mn === 1) mTerm = "x";
    else if (mn === -1) mTerm = "−x";
    else mTerm = `${mn < 0 ? "−" : ""}${Math.abs(mn)}x`;
  } else {
    // No space before the variable — the UI stacks "3/4" vertically and
    // the x reads as an implied coefficient right beside it.
    mTerm = `${mn < 0 ? "−" : ""}${Math.abs(mn)}/${md}x`;
  }
  // Intercept
  let bTerm: string;
  if (b === 0) bTerm = "";
  else if (mTerm === "") bTerm = `${b}`;
  else bTerm = b < 0 ? ` − ${Math.abs(b)}` : ` + ${b}`;
  return `y = ${mTerm}${bTerm}` || "y = 0";
}

/** Format a point as (x, y). */
function fmtPoint(x: number, y: number): string {
  return `(${x}, ${y})`;
}

// Data tables are carried on `Problem.table` and rendered by the UI as
// real bordered x/y tables. (The old text-art table helper produced the
// "doesn't look like an xy-table" worksheets and is gone.)

// ----- Tier 1 — Rates & Unit Rates -----

// Rate sizes step up with difficulty; hard mixes in decimal money rates
// ($2.50-style unit prices) so the division isn't always whole.
const UNIT_RATE_CONTEXTS: ((d: Difficulty) => { display: string; answer: string })[] = [
  (dif) => {
    const r = rnd(2, dif === "easy" ? 9 : dif === "medium" ? 15 : 25);
    const t = rnd(2, dif === "easy" ? 5 : 8);
    return { display: `${r * t} miles in ${t} hours. Find the unit rate.`, answer: `${r} miles per hour` };
  },
  (dif) => {
    const r = rnd(2, dif === "easy" ? 12 : dif === "medium" ? 20 : 35);
    const t = rnd(2, dif === "easy" ? 5 : 8);
    return { display: `${r * t} words typed in ${t} minutes. Find the unit rate.`, answer: `${r} words per minute` };
  },
  (dif) => {
    if (dif === "hard") {
      const cents = rnd(5, 19) * 25; // $1.25 … $4.75 per pound
      const t = rnd(2, 6);
      const total = (cents * t) / 100;
      return {
        display: `$${total.toFixed(2)} for ${t} pounds. Find the unit price.`,
        answer: `$${(cents / 100).toFixed(2)} per pound`,
      };
    }
    const r = rnd(2, dif === "easy" ? 9 : 12);
    const t = rnd(2, 6);
    return { display: `$${r * t} for ${t} pounds. Find the unit price.`, answer: `$${r} per pound` };
  },
  (dif) => {
    const r = rnd(2, dif === "easy" ? 12 : dif === "medium" ? 20 : 30);
    const t = rnd(2, dif === "easy" ? 5 : 8);
    return { display: `${r * t} pages read in ${t} days. Find the unit rate.`, answer: `${r} pages per day` };
  },
];

function makeUnitRate(opts: FluencyOptions, idx: number): Problem {
  const pick = UNIT_RATE_CONTEXTS[rnd(0, UNIT_RATE_CONTEXTS.length - 1)];
  const r = pick(opts.difficulty);
  return { num: idx, display: r.display, answer: r.answer };
}

function makeRateTable(opts: FluencyOptions, idx: number): Problem {
  // Build a table with a missing entry. Rate = y/x.
  const rate = rnd(2, opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 8 : 11);
  const xs = [1, rnd(2, 4), rnd(5, 7), rnd(8, 12)];
  // Hide one of the y-values.
  const hide = rnd(1, xs.length - 1);
  const rows: (string | number)[][] = xs.map((x, i) => [x, i === hide ? "?" : x * rate]);
  return {
    num: idx,
    display: "",
    instruction: "Complete each table so the rate stays constant.",
    table: { headers: ["x", "y"], rows },
    answer: `? = ${xs[hide] * rate}`,
  };
}

function makeRateConvert(opts: FluencyOptions, idx: number): Problem {
  // Conversion pools by difficulty:
  //   easy   — single friendly factor (per-minute → per-hour, oz → lb)
  //   medium — metric time/mass conversions with clean factors
  //   hard   — cross-system conversions with messy factors (mph → ft/s)
  if (opts.difficulty === "easy") {
    if (randomBool()) {
      const perMin = rnd(2, 12);
      return {
        num: idx,
        display: `A pump moves ${perMin} gallons per minute. How many gallons per hour?`,
        answer: `${perMin * 60} gallons per hour`,
      };
    }
    const perOz = rnd(2, 9); // whole cents per ounce
    return {
      num: idx,
      display: `If a snack costs ${perOz}¢ per ounce, what is the price per pound (16 oz)?`,
      answer: `$${((perOz * 16) / 100).toFixed(2)} per pound`,
    };
  }
  if (opts.difficulty === "medium") {
    if (randomBool()) {
      const mPerSec = rnd(2, 20);
      const kmPerHr = (mPerSec * 3600) / 1000;
      return { num: idx, display: `Convert ${mPerSec} m/sec to km/hr.`, answer: `${kmPerHr} km/hr` };
    }
    const perOz = rnd(2, 12);
    return {
      num: idx,
      display: `If a snack costs $0.${String(perOz).padStart(2, "0")} per ounce, what is the price per pound?`,
      answer: `$${((perOz * 16) / 100).toFixed(2)} per pound`,
    };
  }
  if (randomBool()) {
    const mph = rnd(20, 80);
    const fps = Math.round(((mph * 5280) / 3600) * 100) / 100;
    return { num: idx, display: `Convert ${mph} mph to ft/sec.`, answer: `${fps} ft/sec` };
  }
  const ftPerSec = rnd(10, 60);
  const mph = Math.round(((ftPerSec * 3600) / 5280) * 100) / 100;
  return { num: idx, display: `Convert ${ftPerSec} ft/sec to mph.`, answer: `${mph} mph` };
}

// ----- Tier 2 — Proportional Relationships -----

function makePropKTable(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the tables have a FRACTIONAL k (x-values are multiples
  // of the denominator so every y stays whole).
  if (opts.difficulty === "hard" && randomBool()) {
    const d = rnd(2, 4);
    let n = rnd(1, 2 * d - 1);
    while (gcd(n, d) !== 1) n += 1;
    const xs = [d, 2 * d, 3 * d, 4 * d];
    const rows: (string | number)[][] = xs.map((x) => [x, (x / d) * n]);
    return {
      num: idx,
      display: "",
      instruction: "Find the constant of proportionality k for each table.",
      table: { headers: ["x", "y"], rows },
      answer: `k = ${n}/${d}`,
    };
  }
  const k = rnd(2, opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 8 : 11);
  // Skip x = 1 on medium/hard so k has to be computed as y/x rather
  // than read straight off the first row.
  const xs = opts.difficulty === "easy"
    ? [1, rnd(2, 4), rnd(5, 7), rnd(8, 11)]
    : [rnd(2, 3), rnd(4, 5), rnd(6, 8), rnd(9, 12)];
  const rows: (string | number)[][] = xs.map((x) => [x, x * k]);
  return {
    num: idx,
    display: "",
    instruction: "Find the constant of proportionality k for each table.",
    table: { headers: ["x", "y"], rows },
    answer: `k = ${k}`,
  };
}

function makePropKGraph(opts: FluencyOptions, idx: number): Problem {
  // The labeled point is deliberately NOT (1, k) — k has to be computed
  // by dividing the point's y-value by its x-value. Hard mixes in
  // fractional k (e.g. the line through (6, 9) → k = 3/2).
  if (opts.difficulty === "hard" && randomBool()) {
    const d = rnd(2, 4);
    let n = rnd(1, 2 * d - 1);
    while (gcd(n, d) !== 1) n += 1;
    const mMax = Math.max(1, Math.floor(9 / Math.max(d, n)));
    const m = rnd(1, mMax);
    const px = d * m;
    const py = n * m;
    return {
      num: idx,
      display: `Find the constant of proportionality k from the graph.`,
      answer: `k = ${n}/${d}`,
      shape: {
        kind: "grid",
        labels: {},
        grid: {
          range: 10,
          lines: [{ x1: 0, y1: 0, x2: px, y2: py }],
          points: [{ x: px, y: py, label: `(${px}, ${py})` }],
        },
      },
    };
  }
  // Integer k, labeled point at x ≥ 2 (kept inside the grid).
  const k = rnd(2, 4);
  const x0 = rnd(2, Math.max(2, Math.floor(9 / k)));
  const y0 = k * x0;
  return {
    num: idx,
    display: `Find the constant of proportionality k from the graph.`,
    answer: `k = ${k}`,
    shape: {
      kind: "grid",
      labels: {},
      grid: {
        range: 10,
        lines: [{ x1: 0, y1: 0, x2: x0, y2: y0 }],
        points: [{ x: x0, y: y0, label: `(${x0}, ${y0})` }],
      },
    },
  };
}

function makePropEquation(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the tables produce a fractional k (y = 3/2x style).
  if (opts.difficulty === "hard" && randomBool()) {
    const d = rnd(2, 4);
    let n = rnd(1, 2 * d - 1);
    while (gcd(n, d) !== 1) n += 1;
    const xs = [d, 2 * d, 3 * d, 4 * d];
    const rows: (string | number)[][] = xs.map((x) => [x, (x / d) * n]);
    return {
      num: idx,
      display: "",
      instruction: "Write each table's equation in the form y = kx.",
      table: { headers: ["x", "y"], rows },
      answer: `y = ${n}/${d}x`,
    };
  }
  const k = rnd(2, opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 7 : 9);
  const xs = opts.difficulty === "easy"
    ? [1, rnd(2, 4), rnd(5, 7), rnd(8, 11)]
    : [rnd(2, 3), rnd(4, 5), rnd(6, 8), rnd(9, 12)];
  const rows: (string | number)[][] = xs.map((x) => [x, x * k]);
  return {
    num: idx,
    display: "",
    instruction: "Write each table's equation in the form y = kx.",
    table: { headers: ["x", "y"], rows },
    answer: `y = ${k}x`,
  };
}

function makePropTableYN(opts: FluencyOptions, idx: number): Problem {
  const yes = randomBool();
  const k = rnd(2, 6);
  const xs = opts.difficulty === "easy" ? [1, 2, 3, 4] : [2, 3, 5, 8];
  let rows: (string | number)[][];
  if (yes) {
    rows = xs.map((x) => [x, x * k]);
  } else if (opts.difficulty === "hard") {
    // Near-miss: proportional in every row EXCEPT one — spotting the
    // single broken ratio takes checking all of them.
    const brokenIdx = rnd(1, xs.length - 1);
    rows = xs.map((x, i) => [x, x * k + (i === brokenIdx ? rnd(1, 2) : 0)]);
  } else {
    rows = xs.map((x, i) => [x, x * k + (i === 0 ? 0 : rnd(1, 3))]);
  }
  return {
    num: idx,
    display: "",
    instruction: "Is each table proportional? Write Yes or No, and justify.",
    table: { headers: ["x", "y"], rows },
    answer: yes ? `Yes — k = ${k}` : `No — y/x ratios are not equal`,
  };
}

function makePropGraphYN(opts: FluencyOptions, idx: number): Problem {
  // Three flavours:
  //   YES — straight line through the origin
  //   NO  — straight line that misses the origin
  //   NO  — CURVE through the origin (constant-rate check: passing
  //         through (0, 0) alone is not enough!)
  // Easy sticks to the two straight-line flavours; medium/hard mix the
  // curve in.
  const flavour = opts.difficulty === "easy" ? rnd(0, 1) : rnd(0, 2);
  const k = rnd(1, 4);
  if (flavour === 0) {
    return {
      num: idx,
      display: `Is the graph proportional? (Yes or No)`,
      answer: `Yes — straight line through (0, 0)`,
      shape: {
        kind: "grid",
        labels: {},
        grid: { range: 10, lines: [{ x1: 0, y1: 0, x2: 5, y2: 5 * k }] },
      },
    };
  }
  if (flavour === 1) {
    // Non-prop: line with non-zero y-intercept
    const b = rnd(1, 4);
    return {
      num: idx,
      display: `Is the graph proportional? (Yes or No)`,
      answer: `No — does not pass through the origin`,
      shape: {
        kind: "grid",
        labels: {},
        grid: { range: 10, lines: [{ x1: -3, y1: -3 * k + b, x2: 5, y2: 5 * k + b }] },
      },
    };
  }
  // Non-prop: a curve THROUGH the origin — rate of change isn't
  // constant, so it's not proportional even though it hits (0, 0).
  const curveKind = rnd(0, 2);
  const pts: [number, number][] = [];
  if (curveKind === 0) {
    // y = x²/c through the origin
    const c = rnd(1, 3);
    for (let x = 0; x <= 9; x += 0.5) {
      const y = (x * x) / (c + 1);
      if (y > 9.5) break;
      pts.push([x, y]);
    }
  } else if (curveKind === 1) {
    // y = a·√x — fast start that flattens out
    const a = rnd(2, 3);
    for (let x = 0; x <= 9; x += 0.25) {
      const y = a * Math.sqrt(x);
      if (y > 9.5) break;
      pts.push([x, y]);
    }
  } else {
    // Gentle cubic through the origin
    for (let x = 0; x <= 9; x += 0.25) {
      const y = (x * x * x) / 60;
      if (y > 9.5) break;
      pts.push([x, y]);
    }
  }
  return {
    num: idx,
    display: `Is the graph proportional? (Yes or No)`,
    answer: `No — curved, so the rate of change is not constant`,
    shape: { kind: "grid", labels: {}, grid: { range: 10, curve: pts } },
  };
}

// ----- Tier 3 — Slope from Two Points -----

function makeSlopePoints(opts: FluencyOptions, idx: number): Problem {
  const numPool = opts.difficulty === "easy" ? [1, 2, 3, -1, -2] : [1, 2, 3, 4, -1, -2, -3, -4];
  const num = numPool[rnd(0, numPool.length - 1)];
  const den = opts.difficulty === "hard" ? rnd(1, 4) : opts.difficulty === "medium" ? rnd(1, 3) : 1;
  const x1 = rnd(-6, 6);
  const y1 = rnd(-6, 6);
  const x2 = x1 + den;
  const y2 = y1 + num;
  return {
    num: idx,
    display: `Find the slope through ${fmtPoint(x1, y1)} and ${fmtPoint(x2, y2)}.`,
    answer: `m = ${fmtSlope(num, den)}`,
  };
}

function makeSlopeGraph(opts: FluencyOptions, idx: number): Problem {
  // Pick the slope FIRST (rise/run in lowest terms), then place both
  // marked points so they are guaranteed to sit inside the grid. The
  // old version computed the second point as first + 4·(run, rise),
  // which routinely pushed it off the edge of the plot.
  const range = 8;
  const den = opts.difficulty === "hard" ? rnd(2, 3) : opts.difficulty === "medium" ? rnd(1, 2) : 1;
  let num = rnd(1, opts.difficulty === "easy" ? 3 : 4);
  // Keep rise/run in lowest terms so the marked points show the slope
  // exactly as the answer states it.
  while (gcd(num, den) !== 1) num += 1;
  if (randomBool()) num = -num;
  // Number of slope-steps between the two marked points — as many as
  // fit with a 1-unit margin on every side.
  const kMax = Math.max(1, Math.floor((2 * (range - 1)) / Math.max(den, Math.abs(num))));
  const k = Math.min(rnd(2, 3), kMax);
  const dx = den * k;
  const dy = num * k;
  const x1 = rnd(-(range - 1), range - 1 - dx);
  const y1 = dy > 0
    ? rnd(-(range - 1), range - 1 - dy)
    : rnd(-(range - 1) - dy, range - 1);
  const x2 = x1 + dx;
  const y2 = y1 + dy;
  return {
    num: idx,
    display: `Find the slope from the graph.`,
    answer: `m = ${fmtSlope(num, den)}`,
    shape: {
      kind: "grid",
      labels: {},
      grid: {
        range,
        lines: [{ x1, y1, x2, y2 }],
        points: [{ x: x1, y: y1 }, { x: x2, y: y2 }],
      },
    },
  };
}

function makeSlopeTable(opts: FluencyOptions, idx: number): Problem {
  // Easy/medium: consecutive x-values, integer slope. Hard: x-values
  // step by 2 or 3 so the slope must be computed as Δy/Δx (and can be
  // a fraction).
  const step = opts.difficulty === "hard" ? rnd(2, 3) : 1;
  const num = rnd(1, opts.difficulty === "easy" ? 4 : 7) * (randomBool() ? 1 : -1);
  const x0 = rnd(0, 3);
  const y0 = rnd(-5, 5);
  const xs = [x0, x0 + step, x0 + 2 * step, x0 + 3 * step];
  const rows: (string | number)[][] = xs.map((x) => [x, y0 + num * (x - x0)]);
  return {
    num: idx,
    display: "",
    instruction: "Find the slope of the line represented by each table.",
    table: { headers: ["x", "y"], rows },
    answer: `m = ${num}`,
  };
}

function makeSlopeVerbal(opts: FluencyOptions, idx: number): Problem {
  const which = rnd(0, 2);
  const rise = rnd(2, opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 12 : 20);
  const run = rnd(2, opts.difficulty === "easy" ? 3 : 6);
  if (which === 0) {
    return {
      num: idx,
      display: `A balloon rises ${rise} ft every ${run} sec. What is the slope (rise over run)?`,
      answer: `m = ${fmtSlope(rise, run)}`,
    };
  }
  if (which === 1) {
    return {
      num: idx,
      display: `A submarine drops ${rise} m every ${run} sec. What is the slope?`,
      answer: `m = ${fmtSlope(-rise, run)}`,
    };
  }
  return {
    num: idx,
    display: `A car travels ${rise * 10} miles every ${run} hours. What is the slope (rate of change)?`,
    answer: `m = ${fmtSlope(rise * 10, run)}`,
  };
}

function makeSlopeClassify(opts: FluencyOptions, idx: number): Problem {
  // Students classify from a GRAPH, not from a pair of coordinates —
  // reading the direction of a drawn line is the actual grade-8 skill.
  const which = rnd(0, 3);
  const range = 6;
  const instruction =
    "Classify each line's slope as positive, negative, zero, or undefined.";
  const grid = (line: { x1: number; y1: number; x2: number; y2: number }): ShapeSpec => ({
    kind: "grid",
    labels: {},
    grid: { range, lines: [line] },
  });
  if (which === 0 || which === 1) {
    // Positive / negative — vary the steepness so the lines don't all
    // look alike (rise 1–3 over run 1–2).
    const rise = rnd(1, 3);
    const run = rnd(1, 2);
    const b = rnd(-2, 2);
    return {
      num: idx,
      display: "",
      instruction,
      answer: which === 0 ? "positive" : "negative",
      shape: grid({ x1: 0, y1: b, x2: run, y2: b + (which === 0 ? rise : -rise) }),
    };
  }
  if (which === 2) {
    // Horizontal line y = b (kept off the x-axis so it reads clearly).
    let b = rnd(-4, 4);
    if (b === 0) b = 2;
    return {
      num: idx,
      display: "",
      instruction,
      answer: "zero (horizontal)",
      shape: grid({ x1: -1, y1: b, x2: 1, y2: b }),
    };
  }
  // Vertical line x = a (kept off the y-axis).
  let a = rnd(-4, 4);
  if (a === 0) a = -2;
  return {
    num: idx,
    display: "",
    instruction,
    answer: "undefined (vertical)",
    shape: grid({ x1: a, y1: -1, x2: a, y2: 1 }),
  };
}

// ----- Tier 4 — Slope-Intercept Form -----

function makeSIIdentify(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the equations carry a fractional slope.
  if (opts.difficulty === "hard" && randomBool()) {
    const md = rnd(2, 5);
    let mn = rnd(1, md * 2 - 1);
    while (gcd(mn, md) !== 1) mn += 1;
    if (randomBool()) mn = -mn;
    const b = rndConst(opts, true);
    return {
      num: idx,
      display: `Identify m and b in: ${fmtMxB(mn, b, md)}`,
      answer: `m = ${fmtSimpleFrac(mn, md)}, b = ${b}`,
    };
  }
  const m = rndCoef(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  return {
    num: idx,
    display: `Identify m and b in: ${fmtMxB(m, b)}`,
    answer: `m = ${m}, b = ${b}`,
  };
}

function makeSIFromMB(opts: FluencyOptions, idx: number): Problem {
  // Clean three-line layout: givens on their own lines (y-intercept as
  // the ordered pair (0, b)), then a blank for the student's equation.
  // The old single-line prose version repeated the full instruction on
  // every problem and gave no obvious place to write the answer.
  //
  // Slope by difficulty: easy = small positive integer; medium = signed
  // integer; hard = mostly signed simple fractions.
  let mn: number;
  let md = 1;
  if (opts.difficulty === "easy") {
    mn = rnd(1, 6);
  } else if (opts.difficulty === "medium") {
    mn = rnd(1, 9) * (randomBool() ? 1 : -1);
  } else if (Math.random() < 0.3) {
    // Hard keeps ~30% integer slopes so the fractions stand out.
    mn = rnd(2, 9) * (randomBool() ? 1 : -1);
  } else {
    md = rnd(2, 5);
    mn = rnd(1, md * 2 - 1);
    while (gcd(mn, md) !== 1) mn += 1;
    if (randomBool()) mn = -mn;
  }
  const b = opts.difficulty === "easy"
    ? rnd(1, 9)
    : rnd(1, 12) * (randomBool() ? 1 : -1);
  const slopeStr = md === 1
    ? (mn < 0 ? `−${Math.abs(mn)}` : `${mn}`)
    : `${mn < 0 ? "−" : ""}${Math.abs(mn)}/${md}`;
  const bStr = b < 0 ? `−${Math.abs(b)}` : `${b}`;
  return {
    num: idx,
    display: `m = ${slopeStr}\ny-intercept: (0, ${bStr})\ny = ______________`,
    instruction:
      "Use the given slope and y-intercept to write each line's equation in y = mx + b form.",
    answer: fmtMxB(mn, b, md),
  };
}

function makeSIFromMP(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the problems use a fractional slope with a point whose
  // x-value is a multiple of the denominator (so b stays an integer).
  if (opts.difficulty === "hard" && randomBool()) {
    const md = rnd(2, 4);
    let mn = rnd(1, md * 2 - 1);
    while (gcd(mn, md) !== 1) mn += 1;
    if (randomBool()) mn = -mn;
    const x1 = md * rnd(-2, 2);
    const y1 = rnd(-5, 5);
    const b = y1 - (mn * x1) / md;
    return {
      num: idx,
      display: `Write the equation of the line with slope ${fmtSimpleFrac(mn, md)} through ${fmtPoint(x1, y1)}.`,
      answer: fmtMxB(mn, b, md),
    };
  }
  const m = rndCoef(opts, negsFor(opts));
  const x1 = rnd(-5, 5);
  const y1 = rnd(-5, 5);
  const b = y1 - m * x1;
  return {
    num: idx,
    display: `Write the equation of the line with slope ${m} through ${fmtPoint(x1, y1)}.`,
    answer: fmtMxB(m, b),
  };
}

function makeSIFromPP(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the problems yield a fractional slope — the points sit
  // a denominator apart so the rise/run division is the real work.
  if (opts.difficulty === "hard" && randomBool()) {
    const md = rnd(2, 4);
    let mn = rnd(1, md * 2 - 1);
    while (gcd(mn, md) !== 1) mn += 1;
    if (randomBool()) mn = -mn;
    const x1 = md * rnd(-1, 1);
    const y1 = rnd(-5, 5);
    const x2 = x1 + md;
    const y2 = y1 + mn;
    const b = y1 - (mn * x1) / md;
    return {
      num: idx,
      display: `Write the equation of the line through ${fmtPoint(x1, y1)} and ${fmtPoint(x2, y2)}.`,
      answer: fmtMxB(mn, b, md),
    };
  }
  const m = rndCoef(opts, negsFor(opts));
  const x1 = rnd(-5, 5);
  const y1 = rnd(-5, 5);
  const x2 = x1 + 1;
  const y2 = y1 + m;
  const b = y1 - m * x1;
  return {
    num: idx,
    display: `Write the equation of the line through ${fmtPoint(x1, y1)} and ${fmtPoint(x2, y2)}.`,
    answer: fmtMxB(m, b),
  };
}

function makeSIFromGraph(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the lines have slope ±1/2 (read the rise over TWO runs).
  if (opts.difficulty === "hard" && randomBool()) {
    const sign = randomBool() ? 1 : -1;
    const b = rnd(-4, 4);
    const x1 = -6;
    const y1 = (sign * x1) / 2 + b;
    const x2 = 6;
    const y2 = (sign * x2) / 2 + b;
    return {
      num: idx,
      display: `Write the equation of the line shown.`,
      answer: fmtMxB(sign, b, 2),
      shape: {
        kind: "grid",
        labels: {},
        grid: { range: 8, lines: [{ x1, y1, x2, y2 }], points: [{ x: 0, y: b }] },
      },
    };
  }
  const m = rnd(1, opts.difficulty === "easy" ? 3 : 4) * (randomBool() ? 1 : -1);
  const b = rnd(-5, 5);
  // Pick two points on the line to plot.
  const x1 = -4;
  const y1 = m * x1 + b;
  const x2 = 4;
  const y2 = m * x2 + b;
  return {
    num: idx,
    display: `Write the equation of the line shown.`,
    answer: fmtMxB(m, b),
    shape: {
      kind: "grid",
      labels: {},
      grid: {
        range: 10,
        lines: [{ x1, y1, x2, y2 }],
        points: [{ x: 0, y: b }],
      },
    },
  };
}

// ----- Tier 5 — Point-Slope & Standard Forms -----

function makeStdToSI(opts: FluencyOptions, idx: number): Problem {
  // Ax + By = C → y = -A/B x + C/B
  const a = rndCoef(opts, negsFor(opts));
  const b = Math.abs(rndCoef(opts, false)) || 2;
  const c = rndConst(opts, negsFor(opts));
  return {
    num: idx,
    display: `Convert to slope-intercept form: ${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c}`,
    answer: fmtMxB(-a, c, b).replace(" + ", " + ").replace(" − ", " − "),
  };
}

function makeSIToStd(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  // y = mx + b → -mx + y = b → preferred: mx - y = -b OR negate if m < 0
  // For "standard" form with positive leading coefficient:
  let A = -m;
  let B = 1;
  let C = b;
  if (A < 0) { A = -A; B = -B; C = -C; }
  return {
    num: idx,
    display: `Convert to standard form (Ax + By = C with integer A, B): ${fmtMxB(m, b)}`,
    answer: `${fmtCoefTerm(A)} ${fmtAddCoef(B, "y")} = ${C}`,
  };
}

function makePointSlopeWrite(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, negsFor(opts));
  const x1 = rnd(-6, 6);
  const y1 = rnd(-6, 6);
  const x1Str = x1 < 0 ? `(x + ${Math.abs(x1)})` : `(x − ${x1})`;
  const ySign = y1 < 0 ? ` + ${Math.abs(y1)}` : ` − ${y1}`;
  const mStr = m === 1 ? "" : m === -1 ? "−" : `${m}`;
  return {
    num: idx,
    display: `Write in point-slope form: slope ${m}, point ${fmtPoint(x1, y1)}.`,
    answer: `y${ySign} = ${mStr}${x1Str}`,
  };
}

function makePointSlopeToSI(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, negsFor(opts));
  const x1 = rnd(-5, 5);
  const y1 = rnd(-5, 5);
  const b = y1 - m * x1;
  const x1Str = x1 < 0 ? `(x + ${Math.abs(x1)})` : `(x − ${x1})`;
  const ySign = y1 < 0 ? ` + ${Math.abs(y1)}` : ` − ${y1}`;
  const mStr = m === 1 ? "" : m === -1 ? "−" : `${m}`;
  return {
    num: idx,
    display: `Convert to slope-intercept form: y${ySign} = ${mStr}${x1Str}`,
    answer: fmtMxB(m, b),
  };
}

// ----- Tier 6 — Graphing Lines (problem shows equation; answer shows the line) -----

function makeGraphSI(opts: FluencyOptions, idx: number): Problem {
  // Hard: half the equations carry slope ±1/2 so students graph a
  // fractional rise/run.
  if (opts.difficulty === "hard" && randomBool()) {
    const sign = randomBool() ? 1 : -1;
    const b = rnd(-4, 4);
    const x1 = -6, x2 = 6;
    const y1 = (sign * x1) / 2 + b;
    const y2 = (sign * x2) / 2 + b;
    return {
      num: idx,
      display: `Graph the line: ${fmtMxB(sign, b, 2)}`,
      answer: `(line plotted)`,
      shape: { kind: "grid", labels: {}, grid: { range: 10 } },
      answerShape: {
        kind: "grid",
        labels: {},
        grid: { range: 10, lines: [{ x1, y1, x2, y2 }] },
      },
    };
  }
  const m = rnd(1, opts.difficulty === "easy" ? 3 : 4) * (randomBool() ? 1 : -1);
  const b = rnd(-4, 4);
  const x1 = -4, x2 = 4;
  const y1 = m * x1 + b;
  const y2 = m * x2 + b;
  return {
    num: idx,
    display: `Graph the line: ${fmtMxB(m, b)}`,
    answer: `(line plotted)`,
    shape: { kind: "grid", labels: {}, grid: { range: 10 } },
    answerShape: {
      kind: "grid",
      labels: {},
      grid: { range: 10, lines: [{ x1, y1, x2, y2 }] },
    },
  };
}

function makeGraphTable(opts: FluencyOptions, idx: number): Problem {
  const m = rnd(1, 4) * (randomBool() ? 1 : -1);
  const b = rnd(-4, 4);
  const xs = [-2, -1, 0, 1, 2];
  const rows: (string | number)[][] = xs.map((x) => [x, m * x + b]);
  const y1 = m * -4 + b;
  const y2 = m * 4 + b;
  return {
    num: idx,
    display: "",
    instruction: "Graph the line represented by each table.",
    table: { headers: ["x", "y"], rows },
    answer: `(line plotted)`,
    shape: { kind: "grid", labels: {}, grid: { range: 10 } },
    answerShape: {
      kind: "grid",
      labels: {},
      grid: { range: 10, lines: [{ x1: -4, y1, x2: 4, y2 }] },
    },
  };
}

function makeGraphStd(opts: FluencyOptions, idx: number): Problem {
  const A = rnd(1, opts.difficulty === "easy" ? 3 : 5);
  const B = rnd(1, opts.difficulty === "easy" ? 3 : 5);
  // Easy keeps both intercepts positive; medium/hard mix negatives in.
  const span = opts.difficulty === "hard" ? 6 : 4;
  const xInt = (opts.difficulty === "easy" ? rnd(1, 4) : rnd(-span, span)) || 2;
  const yInt = (opts.difficulty === "easy" ? rnd(1, 4) : rnd(-span, span)) || 3;
  const C = A * xInt + B * yInt;
  return {
    num: idx,
    display: `Graph the line: ${fmtCoefTerm(A)} ${fmtAddCoef(B, "y")} = ${C}`,
    answer: `x-intercept ${xInt}, y-intercept ${yInt}`,
    shape: { kind: "grid", labels: {}, grid: { range: 10 } },
    answerShape: {
      kind: "grid",
      labels: {},
      grid: {
        range: 10,
        lines: [{ x1: xInt, y1: 0, x2: 0, y2: yInt }],
        points: [{ x: xInt, y: 0 }, { x: 0, y: yInt }],
      },
    },
  };
}

function makeGraphPoints(opts: FluencyOptions, idx: number): Problem {
  const reach = opts.difficulty === "easy" ? 4 : opts.difficulty === "medium" ? 6 : 8;
  const x1 = rnd(-reach, -1);
  const y1 = rnd(-reach, reach);
  const x2 = rnd(1, reach);
  const y2 = rnd(-reach, reach);
  return {
    num: idx,
    display: `Graph the line through ${fmtPoint(x1, y1)} and ${fmtPoint(x2, y2)}.`,
    answer: `(line plotted)`,
    shape: {
      kind: "grid",
      labels: {},
      grid: {
        range: 10,
        points: [{ x: x1, y: y1 }, { x: x2, y: y2 }],
      },
    },
    answerShape: {
      kind: "grid",
      labels: {},
      grid: {
        range: 10,
        lines: [{ x1, y1, x2, y2 }],
        points: [{ x: x1, y: y1 }, { x: x2, y: y2 }],
      },
    },
  };
}

// ----- Tier 9 — Functions on the Coordinate Plane -----

function makeFnVLTGraph(opts: FluencyOptions, idx: number): Problem {
  // A wide mix of graph families so the worksheet isn't just lines and
  // hyperbolas. PASSES the test: line, parabola, absolute value,
  // exponential, cubic, square root. FAILS: sideways parabola, circle,
  // ellipse, sideways absolute value.
  const yes = randomBool();
  const range = 6;
  const instruction = "Apply the vertical line test: is each graph a function?";
  const curve: [number, number][] = [];
  const sample = (f: (t: number) => [number, number], t0: number, t1: number, dt: number) => {
    for (let t = t0; t <= t1 + 1e-9; t += dt) curve.push(f(t));
  };

  if (yes) {
    // Family pool grows with difficulty: easy = line/parabola,
    // medium adds absolute value, hard adds exponential/cubic/root.
    const kindMax = opts.difficulty === "easy" ? 1 : opts.difficulty === "medium" ? 2 : 5;
    const kind = rnd(0, kindMax);
    if (kind === 0) {
      // Straight line
      const m = rnd(1, 3) * (randomBool() ? 1 : -1);
      const b = rnd(-3, 3);
      return {
        num: idx,
        display: "",
        instruction,
        answer: `Yes`,
        shape: {
          kind: "grid",
          labels: {},
          grid: { range, lines: [{ x1: -4, y1: m * -4 + b, x2: 4, y2: m * 4 + b }] },
        },
      };
    }
    if (kind === 1) {
      // Vertical parabola
      const a = (randomBool() ? 1 : -1) * (rnd(3, 6) / 10);
      const h = rnd(-2, 2);
      const k = randomBool() ? rnd(-3, 0) : rnd(0, 3);
      sample((x) => [x, a * (x - h) * (x - h) + k], h - 5, h + 5, 0.25);
    } else if (kind === 2) {
      // Absolute value V
      const a = randomBool() ? 1 : -1;
      const h = rnd(-2, 2);
      const k = a === 1 ? rnd(-4, 0) : rnd(0, 4);
      sample((x) => [x, a * Math.abs(x - h) + k], -6, 6, 0.25);
    } else if (kind === 3) {
      // Exponential growth/decay
      const flip = randomBool() ? 1 : -1; // reflect for decay-style
      sample((x) => [flip * x, 2 ** (x / 2) - 3], -6, 5.5, 0.25);
    } else if (kind === 4) {
      // Gentle cubic
      sample((x) => [x, (x * x * x) / 16], -5.5, 5.5, 0.25);
    } else {
      // Square root (half parabola on its side — still a function)
      const a = randomBool() ? 1.6 : -1.6;
      sample((x) => [x, a * Math.sqrt(x + 6) - (a > 0 ? 3 : -3)], -6, 6, 0.25);
    }
    return {
      num: idx,
      display: "",
      instruction,
      answer: `Yes`,
      shape: { kind: "grid", labels: {}, grid: { range, curve } },
    };
  }

  const kind = rnd(0, opts.difficulty === "easy" ? 1 : opts.difficulty === "medium" ? 2 : 3);
  if (kind === 0) {
    // Sideways parabola x = y²/c + h
    const c = rnd(1, 2);
    const h = rnd(-4, -1);
    sample((y) => [(y * y) / (c + 1) + h, y], -4, 4, 0.25);
  } else if (kind === 1) {
    // Circle
    const r = rnd(2, 4);
    const cx = rnd(-1, 1);
    const cy = rnd(-1, 1);
    sample((t) => [cx + r * Math.cos(t), cy + r * Math.sin(t)], 0, Math.PI * 2 + 0.1, Math.PI / 24);
  } else if (kind === 2) {
    // Ellipse
    const rx = rnd(3, 5);
    const ry = rnd(2, 3);
    sample((t) => [rx * Math.cos(t), ry * Math.sin(t)], 0, Math.PI * 2 + 0.1, Math.PI / 24);
  } else {
    // Sideways absolute value x = |y| + h
    const h = rnd(-4, -1);
    sample((y) => [Math.abs(y) + h, y], -4.5, 4.5, 0.25);
  }
  return {
    num: idx,
    display: "",
    instruction,
    answer: `No — fails the vertical line test`,
    shape: { kind: "grid", labels: {}, grid: { range, curve } },
  };
}

function makeFnTable(opts: FluencyOptions, idx: number): Problem {
  const yes = randomBool();
  if (yes) {
    const m = rnd(1, 5);
    const b = rnd(-3, 3);
    const xs = [1, 2, 3, 4];
    return {
      num: idx,
      display: "",
      instruction: "Does each table represent a function? Write Yes or No.",
      table: { headers: ["x", "y"], rows: xs.map((x) => [x, m * x + b]) },
      answer: `Yes — each x has exactly one y`,
    };
  }
  // Repeat an x with two different y-values. Randomize which x repeats
  // so the "No" tables don't all look identical.
  const repeatX = rnd(1, 3);
  const ys = [rnd(1, 5), rnd(6, 9), rnd(10, 14)];
  const rows: (string | number)[][] = [];
  let yi = 0;
  for (let x = 1; x <= 3; x++) {
    rows.push([x, ys[yi++]]);
    if (x === repeatX) rows.push([x, ys[yi - 1] + rnd(2, 5)]);
  }
  const dupY1 = rows.find((r) => r[0] === repeatX)![1];
  const dupY2 = (rows.filter((r) => r[0] === repeatX)[1] ?? rows[0])[1];
  return {
    num: idx,
    display: "",
    instruction: "Does each table represent a function? Write Yes or No.",
    table: { headers: ["x", "y"], rows },
    answer: `No — x = ${repeatX} maps to both ${dupY1} and ${dupY2}`,
  };
}

function makeFnEval(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, negsFor(opts));
  const b = rndConst(opts, negsFor(opts));
  const c = rndSolution(opts, negsFor(opts));
  return {
    num: idx,
    display: `Given f(x) = ${fmtMxB(m, b).replace("y = ", "")}, find f(${c}).`,
    answer: `f(${c}) = ${m * c + b}`,
  };
}

function makeFnReverse(opts: FluencyOptions, idx: number): Problem {
  const m = Math.abs(rndCoef(opts, false)) || 2;
  const b = rndConst(opts, negsFor(opts));
  const x = rndSolution(opts, negsFor(opts));
  const fx = m * x + b;
  return {
    num: idx,
    display: `Given f(x) = ${fmtMxB(m, b).replace("y = ", "")}, find x when f(x) = ${fx}.`,
    answer: `x = ${x}`,
  };
}

function makeFnDomainRange(opts: FluencyOptions, idx: number): Problem {
  // Simple linear segment from (a, ya) to (b, yb)
  const a = rnd(-4, -1);
  const b = rnd(1, 4);
  const ya = rnd(-4, 4);
  const yb = rnd(-4, 4);
  const yMin = Math.min(ya, yb);
  const yMax = Math.max(ya, yb);
  return {
    num: idx,
    display: `Find the domain and range of the function shown.`,
    answer: `Domain: [${a}, ${b}], Range: [${yMin}, ${yMax}]`,
    shape: {
      kind: "grid",
      labels: {},
      grid: { range: 6, lines: [{ x1: a, y1: ya, x2: b, y2: yb }], points: [{ x: a, y: ya }, { x: b, y: yb }] },
    },
  };
}

// ----- Tier 10 — Non-Linear & Comparison -----

function makeNonlinearClassify(opts: FluencyOptions, idx: number): Problem {
  const linear = randomBool();
  if (linear) {
    const m = rnd(2, 5);
    const b = rnd(-3, 3);
    const rows: (string | number)[][] = [1, 2, 3, 4].map((x) => [x, m * x + b]);
    return {
      num: idx,
      display: "",
      instruction: "Classify each table as Linear or Nonlinear.",
      table: { headers: ["x", "y"], rows },
      answer: `Linear (constant rate of change ${m})`,
    };
  }
  // Nonlinear: rotate through quadratic, exponential, and cubic shapes
  // so the "Nonlinear" answer isn't always x². Easy sticks to the
  // quadratic; medium/hard mix all three in.
  const kind = opts.difficulty === "easy" ? 0 : rnd(0, 2);
  const fn = kind === 0
    ? (x: number) => x * x
    : kind === 1
      ? (x: number) => 2 ** x
      : (x: number) => x * x * x - 2;
  const rows: (string | number)[][] = [1, 2, 3, 4].map((x) => [x, fn(x)]);
  return {
    num: idx,
    display: "",
    instruction: "Classify each table as Linear or Nonlinear.",
    table: { headers: ["x", "y"], rows },
    answer: `Nonlinear (differences are not constant)`,
  };
}

function makeRateCompare(opts: FluencyOptions, idx: number): Problem {
  // Easy: clearly different whole-dollar rates. Medium: closer whole
  // rates. Hard: half-dollar rates that differ by 50¢ — the comparison
  // takes real division.
  if (opts.difficulty === "hard") {
    const r1x2 = rnd(10, 29); // rate in half-dollars: $5.00 … $14.50
    let r2x2 = r1x2 + (randomBool() ? 1 : -1) * rnd(1, 2);
    if (r2x2 === r1x2) r2x2 += 1;
    const t1 = rnd(2, 6);
    const t2 = rnd(2, 6);
    const pay1 = (r1x2 * t1) / 2;
    const pay2 = (r2x2 * t2) / 2;
    const winner = r1x2 > r2x2 ? "Job A" : "Job B";
    const fmt = (v: number) => (Number.isInteger(v) ? `${v}` : v.toFixed(2));
    return {
      num: idx,
      display: `Job A pays $${fmt(pay1)} for ${t1} hours. Job B pays $${fmt(pay2)} for ${t2} hours. Which pays more per hour?`,
      answer: `${winner} ($${fmt(r1x2 / 2)}/hr vs $${fmt(r2x2 / 2)}/hr)`,
    };
  }
  const spread = opts.difficulty === "easy" ? 2 : 1;
  const r1 = rnd(2, 9);
  let r2 = rnd(2, 9);
  while (Math.abs(r1 - r2) < spread) r2 = rnd(2, 10);
  const t1 = rnd(2, 5);
  const t2 = rnd(2, 5);
  const winner = r1 > r2 ? "Job A" : "Job B";
  return {
    num: idx,
    display: `Job A pays $${r1 * t1} for ${t1} hours. Job B pays $${r2 * t2} for ${t2} hours. Which pays more per hour?`,
    answer: `${winner} ($${r1}/hr vs $${r2}/hr)`,
  };
}

function makeLinearCompare(opts: FluencyOptions, idx: number): Problem {
  const m1 = rndCoef(opts, negsFor(opts));
  const b1 = rndConst(opts, negsFor(opts));
  const m2 = rndCoef(opts, negsFor(opts));
  const b2 = rndConst(opts, negsFor(opts));
  const ask = randomBool();
  if (ask) {
    const winner = Math.abs(m1) > Math.abs(m2) ? "Line 1" : Math.abs(m1) < Math.abs(m2) ? "Line 2" : "Same";
    return {
      num: idx,
      display: `Which line is steeper?\nLine 1: ${fmtMxB(m1, b1)}\nLine 2: ${fmtMxB(m2, b2)}`,
      answer: `${winner} (|m₁| = ${Math.abs(m1)}, |m₂| = ${Math.abs(m2)})`,
    };
  }
  const winner = b1 > b2 ? "Line 1" : b1 < b2 ? "Line 2" : "Same";
  return {
    num: idx,
    display: `Which line has the greater y-intercept?\nLine 1: ${fmtMxB(m1, b1)}\nLine 2: ${fmtMxB(m2, b2)}`,
    answer: `${winner} (b₁ = ${b1}, b₂ = ${b2})`,
  };
}

function makeCoordSlope(opts: FluencyOptions, idx: number): Problem {
  // Pick a clean slope (integer or simple fraction) and back-compute points.
  const slopeNumPool = opts.difficulty === "easy" ? [1, 2, 3, -1, -2] : [1, 2, 3, 4, -1, -2, -3, -4];
  const slopeNum = slopeNumPool[rnd(0, slopeNumPool.length - 1)];
  // Denom: 1 makes it an integer slope; 2/3/4 makes it a fraction.
  const slopeDenom = opts.difficulty === "hard" ? rnd(1, 4) : opts.difficulty === "medium" ? rnd(1, 3) : 1;
  const x1 = rnd(-6, 6);
  const y1 = rnd(-6, 6);
  const x2 = x1 + slopeDenom;
  const y2 = y1 + slopeNum;
  const [sn, sd] = simplify(slopeNum, slopeDenom);
  const slopeStr = sd === 1 ? `${sn}` : `${sn}/${sd}`;
  return {
    num: idx,
    display: `Find the slope through (${x1}, ${y1}) and (${x2}, ${y2}).`,
    answer: `m = ${slopeStr}`,
  };
}

function makeIneqAbsIsolate(opts: FluencyOptions, idx: number): Problem {
  // c|x + a| + d (op) e — isolate first to get |x + a| (op) (e − d)/c, then split.
  const c = rnd(2, 5);
  const a = rndCoef(opts, negsFor(opts));
  const d = rndConst(opts, negsFor(opts));
  const k = rnd(1, opts.difficulty === "easy" ? 5 : opts.difficulty === "medium" ? 6 : 8);
  const e = c * k + d;
  const op: IneqOp = randomBool() ? "<" : ">";
  if (op === "<") {
    return {
      num: idx,
      display: `${c}|x ${fmtAddConst(a)}| ${fmtAddConst(d)} < ${e}`,
      answer: `${-k - a} < x < ${k - a}`,
    };
  }
  return {
    num: idx,
    display: `${c}|x ${fmtAddConst(a)}| ${fmtAddConst(d)} > ${e}`,
    answer: `x < ${-k - a}  or  x > ${k - a}`,
  };
}

function makeEquivalentForms(opts: FluencyOptions, idx: number): Problem {
  // Pick a rational, render in one form, ask for the other two.
  const den = pickTerminatingDenom(opts.difficulty);
  const num = rnd(1, den - 1);
  const sign = opts.allowNegatives && randomBool() ? -1 : 1;
  const signedNum = num * sign;
  const [sn, sd] = simplify(signedNum, den);
  const fracStr = sd === 1 ? String(sn) : `${sn}/${sd}`;
  const decStr = fractionToDecimalString(signedNum, den);
  const pct = (signedNum * 100) / den;
  const pctStr = Number.isInteger(pct) ? String(pct) : trimDecimal(pct, 4);
  // Which form to GIVE the student (others are blanks)
  const givenForm = ["frac", "dec", "pct"][Math.floor(Math.random() * 3)];
  let display: string;
  let answer: string;
  if (givenForm === "frac") {
    display = `${fracStr} = ____ = ____%`;
    answer = `${decStr} = ${pctStr}%`;
  } else if (givenForm === "dec") {
    display = `____ = ${decStr} = ____%`;
    answer = `${fracStr} = ${pctStr}%`;
  } else {
    display = `____ = ____ = ${pctStr}%`;
    answer = `${fracStr} = ${decStr}`;
  }
  return { num: idx, display, answer };
}

// ───────────────────── public API ─────────────────────

const DECIMAL_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "add-decimals",
  "subtract-decimals",
  "multiply-decimals",
  "divide-decimals",
]);

const FRACTION_MULDIV_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "multiply-fractions",
  "divide-fractions",
]);

export const CONVERTING_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "frac-to-dec-term",
  "frac-to-dec-rep",
  "dec-to-frac-term",
  "dec-to-frac-rep",
  "frac-to-percent",
  "percent-to-frac",
  "dec-to-percent",
  "percent-to-dec",
  "mixed-to-improper",
  "improper-to-mixed",
  "compare-rationals",
  "order-rationals",
  "equivalent-forms",
]);

export const GRAPHING_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "gr-unit-rate", "gr-rate-table", "gr-rate-convert",
  "gr-prop-k-table", "gr-prop-k-graph", "gr-prop-equation",
  "gr-prop-table-yn", "gr-prop-graph-yn",
  "gr-slope-points", "gr-slope-graph", "gr-slope-table",
  "gr-slope-verbal", "gr-slope-classify",
  "gr-si-identify", "gr-si-mb", "gr-si-mp", "gr-si-pp", "gr-si-graph",
  "gr-std-to-si", "gr-si-to-std", "gr-ps-write", "gr-ps-to-si",
  "gr-graph-si", "gr-graph-table", "gr-graph-std", "gr-graph-points",
  "gr-fn-vlt-graph", "gr-fn-table", "gr-fn-eval", "gr-fn-reverse", "gr-fn-domain-range",
  "gr-nonlinear-classify", "gr-rate-compare", "gr-linear-compare",
]);

/** Integer operations — signed-integer drill across the four operations.
 *  Distinct from fraction / decimal topics because they ignore the
 *  fraction-format toggles entirely. */
export const INTEGER_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "add-integers",
  "subtract-integers",
  "multiply-integers",
  "divide-integers",
  "integer-mixed",
]);

/** Rational operations — signed fraction drill. Internally delegated to
 *  the existing fraction generators with `allowNegatives` forced on. */
export const RATIONAL_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "add-rationals",
  "subtract-rationals",
  "multiply-rationals",
  "divide-rationals",
  "rational-mixed",
]);

/** Map a rational topic to the fraction topic that drives the generator.
 *  The dispatcher passes the modified options through to the existing
 *  generators so we don't duplicate any of the operand / simplification
 *  logic. */
const RATIONAL_TO_FRACTION: Record<string, FluencyTopic> = {
  "add-rationals":      "add-fractions",
  "subtract-rationals": "subtract-fractions",
  "multiply-rationals": "multiply-fractions",
  "divide-rationals":   "divide-fractions",
};

/** Number-theory drill — prime factorisation and perfect-square roots.
 *  Distinct from arithmetic topics because they have a single operand,
 *  not a binary operation. */
export const NUMBER_THEORY_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "prime-factorization",
  "perfect-square-roots",
]);

/** Percent applications — money-shaped drill for 7.RP.2. */
export const PERCENT_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "percent-of-change",
  "percent-application",
  "simple-interest",
]);

/** Algebraic expression drill — 7.AF.1 entry point. */
export const ALGEBRAIC_EXPR_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "combine-like-terms",
  "distribute-expand",
  "distribute-combine",
]);

export const GEOMETRY_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "geo-rect-area", "geo-rect-perim", "geo-square",
  "geo-tri-area", "geo-parallelogram-area", "geo-trap-area",
  "geo-circle-area", "geo-circle-circumference",
  "geo-rect-find-area", "geo-rect-find-perim", "geo-square-find",
  "geo-tri-find-base", "geo-tri-find-height",
  "geo-circle-find-r-area", "geo-circle-find-r-circ",
  "geo-rect-prism-v", "geo-rect-prism-sa", "geo-cube",
  "geo-tri-prism-v", "geo-tri-prism-sa",
  "geo-cylinder-v", "geo-cylinder-sa",
  "geo-cone-v", "geo-sphere-v", "geo-pyramid-v",
  "geo-rect-prism-find-h", "geo-cube-find-s",
  "geo-cylinder-find-h", "geo-cylinder-find-r",
  "geo-cone-find-h", "geo-sphere-find-r",
  "geo-pyth-hyp", "geo-pyth-leg", "geo-pyth-check", "geo-pyth-word",
  "geo-coord-distance", "geo-coord-midpoint", "geo-coord-slope",
]);

export const INEQUALITY_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "ineq-one-add", "ineq-one-sub", "ineq-one-mul", "ineq-one-div", "ineq-one-mixed",
  "ineq-two-pos", "ineq-two-neg", "ineq-two-rational", "ineq-two-dist",
  "ineq-multi-combine", "ineq-multi-dist", "ineq-multi-both", "ineq-multi-full", "ineq-multi-special",
  "ineq-compound-and", "ineq-compound-or", "ineq-compound-translate",
  "ineq-abs-less", "ineq-abs-greater", "ineq-abs-isolate",
]);

export const EQUATION_TOPICS: ReadonlySet<FluencyTopic> = new Set([
  "eq-one-add", "eq-one-sub", "eq-one-mul", "eq-one-div", "eq-one-mixed",
  "eq-two-pos", "eq-two-neg", "eq-two-rational", "eq-two-dist",
  "eq-multi-combine", "eq-multi-dist", "eq-multi-both", "eq-multi-full", "eq-multi-special",
  "eq-literal",
  "eq-prop", "eq-prop-word",
  "eq-abs-simple", "eq-abs-coef", "eq-abs-isolate",
  "eq-sys-sub", "eq-sys-elim", "eq-sys-special", "eq-sys-word",
  "eq-quad-sqrt", "eq-quad-trans", "eq-quad-fac-a1", "eq-quad-fac-an",
  "eq-quad-diff", "eq-quad-formula", "eq-quad-complete",
  "eq-rad-single", "eq-rad-double", "eq-rad-linear",
  "eq-rat-simple", "eq-rat-linear", "eq-rat-lcd",
  "eq-exp-bases",
]);

// ─────────────────────────────────────────────────────────────────────
// Integer Operations — signed-integer drill across +, −, ×, ÷.
// ─────────────────────────────────────────────────────────────────────

/** Per-difficulty operand cap for integer drill. Easy stays single-digit
 *  so students see the structure; hard pushes into two-digit territory
 *  without becoming a mental-arithmetic ordeal. */
function integerCap(diff: Difficulty): number {
  switch (diff) {
    case "easy":   return 9;
    case "medium": return 20;
    case "hard":   return 50;
  }
}

/** Random signed integer in [-cap, cap], excluding zero. We exclude zero
 *  in most contexts because "5 + 0" and "0 × 7" don't really teach the
 *  sign rules — they just confirm 0 behaviour students already know.
 *  Division uses a stricter form that forces clean quotients. */
function randSignedNonzero(cap: number): number {
  const mag = 1 + Math.floor(Math.random() * cap);
  return Math.random() < 0.5 ? -mag : mag;
}

/** Format a signed integer with parentheses around negatives so
 *  "5 + (-3)" reads correctly rather than "5 + -3". Positive numbers
 *  render unwrapped. */
function fmtSigned(n: number): string {
  return n < 0 ? `(${n})` : `${n}`;
}

function makeIntegerAdd(opts: FluencyOptions, num: number): Problem {
  const cap = integerCap(opts.difficulty);
  const a = randSignedNonzero(cap);
  const b = randSignedNonzero(cap);
  return {
    num,
    display: `${a} + ${fmtSigned(b)}`,
    answer: `${a + b}`,
  };
}

function makeIntegerSub(opts: FluencyOptions, num: number): Problem {
  const cap = integerCap(opts.difficulty);
  const a = randSignedNonzero(cap);
  const b = randSignedNonzero(cap);
  return {
    num,
    display: `${a} − ${fmtSigned(b)}`,
    answer: `${a - b}`,
  };
}

function makeIntegerMul(opts: FluencyOptions, num: number): Problem {
  const cap = integerCap(opts.difficulty);
  // Keep products bounded to avoid mental-arithmetic nightmares: cap each
  // factor to sqrt(cap*10) so even hard tops out around 50×3 ≈ 150.
  const factorCap = Math.max(3, Math.floor(Math.sqrt(cap * 12)));
  const a = randSignedNonzero(factorCap);
  const b = randSignedNonzero(factorCap);
  return {
    num,
    display: `${fmtSigned(a)} × ${fmtSigned(b)}`,
    answer: `${a * b}`,
  };
}

function makeIntegerDiv(opts: FluencyOptions, num: number): Problem {
  // Build the divisor first, then the quotient, then derive the dividend
  // so every problem has a clean integer answer.
  const cap = integerCap(opts.difficulty);
  const divisorCap = Math.max(3, Math.floor(Math.sqrt(cap * 12)));
  const divisor = randSignedNonzero(divisorCap);
  const quotient = randSignedNonzero(divisorCap);
  const dividend = divisor * quotient;
  return {
    num,
    display: `${fmtSigned(dividend)} ÷ ${fmtSigned(divisor)}`,
    answer: `${quotient}`,
  };
}

// ─────────────────────────────────────────────────────────────────────
// Number Theory — Prime Factorization & Perfect-Square Roots (7.NS.5/6)
// ─────────────────────────────────────────────────────────────────────

const SMALL_PRIMES = [2, 3, 5, 7, 11, 13];

/** Build a composite by multiplying together a small bag of primes. The
 *  difficulty band controls the bag size and the max prime used.
 *
 *    easy   : 2-3 prime factors, primes from {2,3,5,7}, product ≤ ~200
 *    medium : 3-4 prime factors, primes from {2,3,5,7,11}, product ≤ ~600
 *    hard   : 4-5 prime factors, primes from full list, product ≤ ~2500
 */
function makePrimeFactorisation(opts: FluencyOptions, num: number): Problem {
  const { diffSize, primePool, productCap } = (() => {
    switch (opts.difficulty) {
      case "easy":   return { diffSize: [2, 3], primePool: SMALL_PRIMES.slice(0, 4), productCap: 200 };
      case "medium": return { diffSize: [3, 4], primePool: SMALL_PRIMES.slice(0, 5), productCap: 600 };
      case "hard":   return { diffSize: [4, 5], primePool: SMALL_PRIMES, productCap: 2500 };
    }
  })();

  // Pick prime factors with replacement until we hit the size and cap.
  let factors: number[] = [];
  let product = 1;
  for (let tries = 0; tries < 50; tries++) {
    factors = [];
    product = 1;
    const target = rnd(diffSize[0], diffSize[1]);
    while (factors.length < target) {
      const p = primePool[Math.floor(Math.random() * primePool.length)];
      if (product * p > productCap) break;
      factors.push(p);
      product *= p;
    }
    if (factors.length >= diffSize[0]) break;
  }

  // Build the answer string with exponents for repeated primes.
  factors.sort((a, b) => a - b);
  const counts = new Map<number, number>();
  for (const p of factors) counts.set(p, (counts.get(p) ?? 0) + 1);
  const answerParts: string[] = [];
  for (const p of Array.from(counts.keys()).sort((a, b) => a - b)) {
    const c = counts.get(p)!;
    answerParts.push(c === 1 ? `${p}` : `${p}^${c}`);
  }

  return {
    num,
    display: `Prime factorisation of ${product}`,
    answer: answerParts.join(" · "),
  };
}

/** Perfect-square roots: √n for a known perfect square n.
 *
 *    easy   : roots 2–9   (squares 4–81)
 *    medium : roots 2–14  (squares 4–196)
 *    hard   : roots 2–25  (squares 4–625)
 */
function makePerfectSquareRoot(opts: FluencyOptions, num: number): Problem {
  const cap = opts.difficulty === "easy" ? 9 : opts.difficulty === "medium" ? 14 : 25;
  const root = rnd(2, cap);
  return {
    num,
    display: `√${root * root}`,
    answer: `${root}`,
  };
}

// ─────────────────────────────────────────────────────────────────────
// Percent Applications (7.RP.2)
// ─────────────────────────────────────────────────────────────────────

/** Percent of change between two whole-number values. Sign is reported
 *  as "increase" or "decrease" so the student commits to interpreting
 *  the sign, not just computing magnitude. */
function makePercentOfChange(opts: FluencyOptions, num: number): Problem {
  // Pick old value and a target percent so the new value lands on a
  // clean integer. We use percents from a fixed bag of "clean" values
  // that give whole-number new values across common old-value ranges.
  const CLEAN_PCTS = [5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 75, 80];
  const oldVal = (() => {
    switch (opts.difficulty) {
      case "easy":   return rnd(2, 10) * 10;  // 20 … 100
      case "medium": return rnd(5, 20) * 10;  // 50 … 200
      case "hard":   return rnd(10, 40) * 10; // 100 … 400
    }
  })();
  // Pick a sign (increase or decrease) and find a percent that yields
  // a whole-number new value.
  const isIncrease = Math.random() < 0.5;
  let pct = 0;
  let newVal = oldVal;
  for (let tries = 0; tries < 25; tries++) {
    const candidate = CLEAN_PCTS[Math.floor(Math.random() * CLEAN_PCTS.length)];
    const factor = isIncrease ? 1 + candidate / 100 : 1 - candidate / 100;
    const next = oldVal * factor;
    if (Number.isInteger(next) && next > 0 && next !== oldVal) {
      pct = candidate;
      newVal = next;
      break;
    }
  }
  // Fall back to a guaranteed clean pair if the random walk failed.
  if (pct === 0) {
    pct = 25;
    newVal = isIncrease ? oldVal * 1.25 : oldVal * 0.75;
  }
  return {
    num,
    display: `From ${oldVal} to ${newVal}`,
    answer: `${pct}% ${isIncrease ? "increase" : "decrease"}`,
  };
}

/** Percent application — tax / tip / markup / discount. Produces a
 *  starting price + percent + scenario, asks for the FINAL price (post
 *  application). One operation per problem, deliberate variety in the
 *  scenarios so the worksheet doesn't read as "20 × tax." */
function makePercentApplication(opts: FluencyOptions, num: number): Problem {
  // Difficulty bands tune the base-price range and the percent bag.
  // Easy bias toward 10% / 20% / 25% multiples that produce clean
  // money. Hard widens to less-clean but still-whole results.
  const SCENARIOS = [
    { tpl: (p: number, q: number) => ({
        prompt: `A $${p} item with ${q}% tax — total cost?`,
        factor: 1 + q / 100,
      }),
    },
    { tpl: (p: number, q: number) => ({
        prompt: `A $${p} bill plus a ${q}% tip — total paid?`,
        factor: 1 + q / 100,
      }),
    },
    { tpl: (p: number, q: number) => ({
        prompt: `A store marks up a $${p} item by ${q}% — selling price?`,
        factor: 1 + q / 100,
      }),
    },
    { tpl: (p: number, q: number) => ({
        prompt: `A $${p} item is on sale for ${q}% off — sale price?`,
        factor: 1 - q / 100,
      }),
    },
  ];
  const cleanPercents = opts.difficulty === "easy"
    ? [10, 20, 25, 50]
    : opts.difficulty === "medium"
      ? [5, 10, 15, 20, 25, 30, 40, 50]
      : [4, 5, 8, 10, 12, 15, 20, 25, 30, 40];

  // Try a few combinations until we hit a whole-dollar answer.
  for (let tries = 0; tries < 25; tries++) {
    const base = opts.difficulty === "easy" ? rnd(4, 20) * 5 : opts.difficulty === "medium" ? rnd(4, 30) * 5 : rnd(4, 50) * 10;
    const pct = cleanPercents[Math.floor(Math.random() * cleanPercents.length)];
    const scenario = SCENARIOS[Math.floor(Math.random() * SCENARIOS.length)];
    const { prompt, factor } = scenario.tpl(base, pct);
    const result = base * factor;
    if (Number.isInteger(result * 100)) {
      // Round to 2 decimal places for money display.
      const fmt = Number.isInteger(result) ? `${result}` : result.toFixed(2);
      return {
        num,
        display: prompt,
        answer: `$${fmt}`,
      };
    }
  }
  // Guaranteed fallback.
  return {
    num,
    display: "A $100 item with 10% tax — total cost?",
    answer: "$110",
  };
}

/** Simple interest: I = Prt. Asks for the interest amount (not total)
 *  to keep the answer separate from the principal. Rates are whole %,
 *  times are whole years, so calculations stay clean. */
function makeSimpleInterest(opts: FluencyOptions, num: number): Problem {
  const principalRange = opts.difficulty === "easy"
    ? [200, 500, 1000, 2000]
    : opts.difficulty === "medium"
      ? [500, 1000, 1500, 2000, 3000, 5000]
      : [1000, 2500, 5000, 7500, 10000, 15000, 20000];
  const rateRange = opts.difficulty === "easy" ? [2, 4, 5, 10] : opts.difficulty === "medium" ? [2, 3, 4, 5, 6, 8, 10] : [2, 3, 4, 5, 6, 7, 8, 9, 10, 12];
  const timeRange = opts.difficulty === "easy" ? [1, 2, 3] : opts.difficulty === "medium" ? [1, 2, 3, 4, 5] : [1, 2, 3, 4, 5, 6, 8, 10];

  const P = principalRange[Math.floor(Math.random() * principalRange.length)];
  const r = rateRange[Math.floor(Math.random() * rateRange.length)];
  const t = timeRange[Math.floor(Math.random() * timeRange.length)];
  const I = (P * r * t) / 100;
  const fmt = Number.isInteger(I) ? `${I}` : I.toFixed(2);
  return {
    num,
    display: `$${P} at ${r}% per year for ${t} year${t === 1 ? "" : "s"} — interest earned?`,
    answer: `$${fmt}`,
  };
}

// ─────────────────────────────────────────────────────────────────────
// Algebraic Expressions (7.AF.1)
// ─────────────────────────────────────────────────────────────────────

/** Format a coefficient + variable term. Handles ±1, 0, and the
 *  invisible-coefficient cases so the rendered expression reads
 *  naturally ("x" not "1x", "−x" not "−1x"). Constant terms (empty
 *  `variable`) keep their digit: ±1 renders as "1"/"−1", never as an
 *  orphaned sign or an empty string — an empty string here used to
 *  produce worksheets like "5x + 4x −" and answers that silently
 *  included a constant the problem never displayed. */
function fmtTerm(coef: number, variable: string): string {
  if (coef === 0) return "";
  if (!variable) return coef < 0 ? `−${Math.abs(coef)}` : `${coef}`;
  if (coef === 1) return variable;
  if (coef === -1) return `−${variable}`;
  // Typographic minus on leading negatives so "−22x" matches the rest
  // of the worksheet instead of rendering an ASCII hyphen.
  return coef < 0 ? `−${Math.abs(coef)}${variable}` : `${coef}${variable}`;
}

/** Insert a sign and a term into a running display, handling the
 *  leading-term case where we DON'T want "+ 3x" — just "3x". */
function appendTerm(running: string, coef: number, variable: string): string {
  const term = fmtTerm(coef, variable);
  if (!term) return running;
  if (!running) return term;
  return coef < 0
    ? `${running} − ${fmtTerm(-coef, variable)}`
    : `${running} + ${term}`;
}

/** Combine Like Terms — simplify ax + by + … expressions of the form
 *  c1·x + c2 + c3·x + c4 + … into ax + b. Difficulty controls term
 *  count and coefficient range.
 *
 *    easy   : 3-4 terms, |coef| ≤ 5, single variable x
 *    medium : 4-5 terms, |coef| ≤ 10, x or y (one variable per problem)
 *    hard   : 5-7 terms, |coef| ≤ 12, two variables mixed (x AND y)
 */
/** Hard-tier Combine Like Terms with rational coefficients — half the
 *  hard worksheet uses fraction coefficients (same denominator across
 *  the expression so combining stays natural, e.g. 3/4x + 1/4x − 1/2)
 *  and the other half one-decimal coefficients (0.5x + 1.2x − 0.7).
 *  Sums are computed in exact integer space (numerators / tenths). */
function makeCombineLikeTermsRational(opts: FluencyOptions, num: number): Problem {
  const useDec = randomBool();
  // Local sign-aware append for pre-formatted term bodies.
  const appendStr = (running: string, negative: boolean, body: string): string => {
    if (!running) return negative ? `−${body}` : body;
    return negative ? `${running} − ${body}` : `${running} + ${body}`;
  };

  // Term plan: at least two x-terms so there is always something to
  // combine, plus 1–2 constants.
  const kinds: ("x" | "k")[] = ["x", "x"];
  if (randomBool()) kinds.push("x");
  kinds.push("k");
  if (randomBool()) kinds.push("k");
  // Shuffle so the like terms aren't always adjacent.
  kinds.sort(() => Math.random() - 0.5);

  if (useDec) {
    // Coefficients are tenths (never a whole multiple of 10) so every
    // term shows one decimal place.
    let sumX = 0;
    let sumK = 0;
    let display = "";
    for (const kind of kinds) {
      let tenths = rnd(1, 30);
      if (tenths % 10 === 0) tenths += 1;
      const neg = randomBool();
      const signed = neg ? -tenths : tenths;
      const body = `${(tenths / 10).toFixed(1)}${kind === "x" ? "x" : ""}`;
      display = appendStr(display, neg, body);
      if (kind === "x") sumX += signed;
      else sumK += signed;
    }
    let answer = "";
    answer = appendDecTerm(answer, sumX / 10, "x");
    answer = appendDecTerm(answer, sumK / 10, "");
    if (!answer) answer = "0";
    return { num, display, answer };
  }

  // Fraction flavour: one shared denominator, numerators small.
  const den = [2, 3, 4][rnd(0, 2)];
  let sumXNum = 0;
  let sumKNum = 0;
  let display = "";
  for (const kind of kinds) {
    let n = rnd(1, 2 * den + 1);
    if (n % den === 0) n += 1; // keep every printed term a real fraction
    const neg = randomBool();
    const body = `${n}/${den}${kind === "x" ? "x" : ""}`;
    display = appendStr(display, neg, body);
    if (kind === "x") sumXNum += neg ? -n : n;
    else sumKNum += neg ? -n : n;
  }
  // Assemble the simplified answer, one part at a time.
  const partFor = (numer: number, v: string): { neg: boolean; body: string } | null => {
    if (numer === 0) return null;
    const [sn, sd] = simplify(Math.abs(numer), den);
    const body = sd === 1 ? `${sn === 1 && v ? "" : sn}${v}` : `${sn}/${sd}${v}`;
    return { neg: numer < 0, body: body || "1" };
  };
  let answer = "";
  const xPart = partFor(sumXNum, "x");
  if (xPart) answer = appendStr(answer, xPart.neg, xPart.body);
  const kPart = partFor(sumKNum, "");
  if (kPart) answer = appendStr(answer, kPart.neg, kPart.body);
  if (!answer) answer = "0";
  return { num, display, answer };
}

function makeCombineLikeTerms(opts: FluencyOptions, num: number): Problem {
  // Hard: half the worksheet switches to rational (fraction or decimal)
  // coefficients; the other half stays integer with more terms.
  if (opts.difficulty === "hard" && randomBool()) {
    return makeCombineLikeTermsRational(opts, num);
  }
  const { termCount, coefCap, useTwoVars } = (() => {
    switch (opts.difficulty) {
      case "easy":   return { termCount: rnd(3, 4), coefCap: 5, useTwoVars: false };
      case "medium": return { termCount: rnd(4, 5), coefCap: 10, useTwoVars: false };
      case "hard":   return { termCount: rnd(5, 7), coefCap: 12, useTwoVars: true };
    }
  })();

  const varName = useTwoVars ? "x" : Math.random() < 0.5 ? "x" : "y";
  const secondVar = useTwoVars ? "y" : varName;

  // Build a random list of terms: some x-coefficient, some y-coefficient
  // (if useTwoVars), some constant. Pick a kind per term so we mix
  // variable terms and constants throughout the expression.
  type Term = { coef: number; kind: "var1" | "var2" | "const" };
  const terms: Term[] = [];
  let sumVar1 = 0;
  let sumVar2 = 0;
  let sumConst = 0;
  for (let i = 0; i < termCount; i++) {
    const kindRoll = Math.random();
    const kind: Term["kind"] = useTwoVars
      ? (kindRoll < 0.4 ? "var1" : kindRoll < 0.75 ? "var2" : "const")
      : (kindRoll < 0.55 ? "var1" : "const");
    let coef = rnd(-coefCap, coefCap);
    if (coef === 0) coef = 1; // never pad with zero terms
    terms.push({ coef, kind });
    if (kind === "var1") sumVar1 += coef;
    else if (kind === "var2") sumVar2 += coef;
    else sumConst += coef;
  }

  // Render the display, term-by-term, threading signs through.
  let display = "";
  for (const t of terms) {
    const v = t.kind === "var1" ? varName : t.kind === "var2" ? secondVar : "";
    if (v) display = appendTerm(display, t.coef, v);
    else display = appendTerm(display, t.coef, "");
  }

  // Build the simplified answer.
  let answer = "";
  if (useTwoVars) {
    answer = appendTerm(answer, sumVar1, varName);
    answer = appendTerm(answer, sumVar2, secondVar);
    answer = appendTerm(answer, sumConst, "");
  } else {
    answer = appendTerm(answer, sumVar1, varName);
    answer = appendTerm(answer, sumConst, "");
  }
  if (!answer) answer = "0";

  return { num, display, answer };
}

/** Outside-coefficient kind for the distribute generators. Integer is
 *  the default; the "Fractions" and "Decimals" toggles in the UI mix
 *  unit-fraction (1/2, 1/3, 1/4, 1/5, 1/6) and friendly-decimal
 *  (0.1, 0.2, 0.25, 0.5) outside coefficients into the rotation. */
type DistOutside =
  | { kind: "int"; value: number }
  | { kind: "frac"; sign: 1 | -1; num: number; den: number }
  | { kind: "dec"; value: number };

/** Build a display string for the outside coefficient that gets
 *  rendered directly before "(…)" in the problem. Handles sign and the
 *  invisible-1 cases so we get "(2x + 3)" instead of "1(2x + 3)" and
 *  "−(2x + 3)" instead of "−1(2x + 3)". */
function fmtDistOutside(o: DistOutside): string {
  if (o.kind === "int") {
    if (o.value === 1) return "";
    if (o.value === -1) return "−";
    return `${o.value}`;
  }
  if (o.kind === "frac") {
    return `${o.sign === -1 ? "−" : ""}${o.num}/${o.den}`;
  }
  // Decimal — render as written; negatives use the typographic minus.
  if (o.value < 0) return `−${Math.abs(o.value)}`;
  return `${o.value}`;
}

/** Pick a unit fraction (1/d) outside coefficient. Sign is mixed-in
 *  when the difficulty allows negatives outside. The denominator is
 *  returned so the caller can pick inside terms that are divisible by
 *  it — keeping answers clean integers. */
function pickFracOutside(allowNeg: boolean): { sign: 1 | -1; num: number; den: number } {
  const denominators = [2, 3, 4, 5, 6];
  const den = denominators[rnd(0, denominators.length - 1)];
  const sign: 1 | -1 = allowNeg && Math.random() < 0.35 ? -1 : 1;
  return { sign, num: 1, den };
}

/** Pick a friendly decimal outside coefficient. Returns the value plus
 *  an effective "denominator-equivalent" so the caller can constrain
 *  inside terms to multiples of that denominator (0.5 → mult of 2,
 *  0.25 → mult of 4, 0.2 → mult of 5, 0.1 → mult of 10). */
function pickDecOutside(allowNeg: boolean): { value: number; effDen: number } {
  const choices: { value: number; effDen: number }[] = [
    { value: 0.5, effDen: 2 },
    { value: 0.25, effDen: 4 },
    { value: 0.2, effDen: 5 },
    { value: 0.1, effDen: 10 },
  ];
  const pick = choices[rnd(0, choices.length - 1)];
  const sign = allowNeg && Math.random() < 0.35 ? -1 : 1;
  return { value: sign * pick.value, effDen: pick.effDen };
}

/** Pick an inside coefficient that's a multiple of `den` so the
 *  distributed product (1/den) * coef stays integer. The caller
 *  supplies a target absolute-value cap and gets back a non-zero
 *  multiple within that range. */
function pickMultipleOf(den: number, absCap: number): number {
  // Possible non-zero multiples of `den` within ±absCap.
  const maxMult = Math.max(1, Math.floor(absCap / den));
  let v = rnd(-maxMult, maxMult);
  if (v === 0) v = 1;
  return v * den;
}

/** Format a fixed-decimal answer rounded to at most 2 places, trimming
 *  trailing zeros. (3.00 → "3", 2.50 → "2.5", 2.75 → "2.75") */
function fmtDecAnswerCoef(coef: number, variable: string): string {
  if (coef === 0) return "";
  // Round to 4 dp first to wash floating-point fuzz, then trim.
  const rounded = Math.round(coef * 10000) / 10000;
  if (rounded === 1 && variable) return variable;
  if (rounded === -1 && variable) return `−${variable}`;
  // Typographic minus for negatives so leading terms match the rest of
  // the worksheet ("−0.5x", not "-0.5x").
  const s = rounded < 0 ? `−${Math.abs(rounded)}` : rounded.toString();
  return `${s}${variable}`;
}

function appendDecTerm(running: string, coef: number, variable: string): string {
  const term = fmtDecAnswerCoef(coef, variable);
  if (!term) return running;
  if (!running) return term;
  return coef < 0
    ? `${running} − ${fmtDecAnswerCoef(-coef, variable)}`
    : `${running} + ${term}`;
}

/** Distributive Property — Expand only.
 *  Single-group expansion of the form a(bx ± c) → abx ± ac. No like
 *  terms to collect; just apply distribution cleanly. This is the
 *  isolated-skill drill before combining is layered in.
 *
 *    easy   : positive outside coefficient 2–6, inside |coef| ≤ 9,
 *             single variable x, "a(x + c)" or "a(bx + c)" forms.
 *    medium : outside coefficient 2–9 with ~40% chance of negative,
 *             inside |coef| ≤ 12, occasionally "a(c − bx)" ordering.
 *    hard   : outside coefficient ±2–12 (negatives common), inside
 *             |coef| ≤ 15, three-term inside like a(bx + cy + d).
 *
 *  When `distributeIncludeFractions` or `distributeIncludeDecimals` is
 *  on, ~⅓ of problems use a unit-fraction or friendly-decimal outside
 *  coefficient; inside terms are picked divisible by the denominator so
 *  answers stay integer-clean.
 */
function makeDistributeExpand(opts: FluencyOptions, num: number): Problem {
  const cfg = (() => {
    switch (opts.difficulty) {
      case "easy":
        return { aMin: 2, aMax: 6, allowNegA: false, coefCap: 9, threeTerm: false };
      case "medium":
        return { aMin: 2, aMax: 9, allowNegA: true, negAChance: 0.4, coefCap: 12, threeTerm: false };
      case "hard":
        return { aMin: 2, aMax: 12, allowNegA: true, negAChance: 0.55, coefCap: 15, threeTerm: true };
    }
  })();

  // Pick the outside-coefficient kind. With the Fractions/Decimals
  // toggles on, the rotation mixes ⅓ of each enabled kind alongside
  // integers — so a worksheet of 20 with both toggles ends up roughly
  // 7 integer / 7 fraction / 6 decimal. HARD always mixes rational
  // outside coefficients in, toggles or not — that's what makes the
  // hard tier hard.
  const wantFrac = !!opts.distributeIncludeFractions || opts.difficulty === "hard";
  const wantDec = !!opts.distributeIncludeDecimals || opts.difficulty === "hard";
  const kindRoll = Math.random();
  let outside: DistOutside;
  let effDen = 1; // multiplier that inside terms must be divisible by
  if (wantFrac && wantDec) {
    if (kindRoll < 1 / 3) {
      const f = pickFracOutside(cfg.allowNegA);
      outside = { kind: "frac", ...f };
      effDen = f.den;
    } else if (kindRoll < 2 / 3) {
      const d = pickDecOutside(cfg.allowNegA);
      outside = { kind: "dec", value: d.value };
      effDen = d.effDen;
    } else {
      let a = rnd(cfg.aMin, cfg.aMax);
      if (cfg.allowNegA && Math.random() < (cfg.negAChance ?? 0)) a = -a;
      outside = { kind: "int", value: a };
    }
  } else if (wantFrac) {
    if (kindRoll < 0.5) {
      const f = pickFracOutside(cfg.allowNegA);
      outside = { kind: "frac", ...f };
      effDen = f.den;
    } else {
      let a = rnd(cfg.aMin, cfg.aMax);
      if (cfg.allowNegA && Math.random() < (cfg.negAChance ?? 0)) a = -a;
      outside = { kind: "int", value: a };
    }
  } else if (wantDec) {
    if (kindRoll < 0.5) {
      const d = pickDecOutside(cfg.allowNegA);
      outside = { kind: "dec", value: d.value };
      effDen = d.effDen;
    } else {
      let a = rnd(cfg.aMin, cfg.aMax);
      if (cfg.allowNegA && Math.random() < (cfg.negAChance ?? 0)) a = -a;
      outside = { kind: "int", value: a };
    }
  } else {
    let a = rnd(cfg.aMin, cfg.aMax);
    if (cfg.allowNegA && Math.random() < (cfg.negAChance ?? 0)) a = -a;
    outside = { kind: "int", value: a };
  }

  // Multiplier applied to each inside term: for integer outside it's
  // the integer itself; for fraction (1/d) it's 1/d; for decimal it's
  // the decimal. We use this to compute the simplified answer.
  const mult =
    outside.kind === "int"
      ? outside.value
      : outside.kind === "frac"
        ? (outside.sign * outside.num) / outside.den
        : outside.value;

  // Inside terms get capped at the integer coef cap, but for fraction/
  // decimal outsides they must be multiples of `effDen` so the
  // distributed product is integer.
  const pickInsideCoef = (): number => {
    if (effDen === 1) {
      let v = rnd(-cfg.coefCap, cfg.coefCap);
      if (v === 0) v = 1;
      return v;
    }
    return pickMultipleOf(effDen, cfg.coefCap);
  };

  // Three-term inside (hard) uses two variables (x, y) + a constant.
  // Two-term inside (easy/medium) uses one variable x and a constant.
  const useThreeTerm = cfg.threeTerm && Math.random() < 0.5;

  if (useThreeTerm) {
    const b = pickInsideCoef();
    const c = pickInsideCoef();
    const d = pickInsideCoef();
    let inside = appendTerm("", b, "x");
    inside = appendTerm(inside, c, "y");
    inside = appendTerm(inside, d, "");
    const display = `${fmtDistOutside(outside)}(${inside})`;
    // Distribute — fraction and integer paths land on integer products
    // by construction; decimal path may land on a one-decimal answer.
    const ab = mult * b, ac = mult * c, ad = mult * d;
    let answer: string;
    if (outside.kind === "dec") {
      answer = appendDecTerm("", ab, "x");
      answer = appendDecTerm(answer, ac, "y");
      answer = appendDecTerm(answer, ad, "");
    } else {
      answer = appendTerm("", Math.round(ab), "x");
      answer = appendTerm(answer, Math.round(ac), "y");
      answer = appendTerm(answer, Math.round(ad), "");
    }
    if (!answer) answer = "0";
    return { num, display, answer };
  }

  // Two-term inside: bx + c (or c + bx ~40% of the time on medium+).
  let b = pickInsideCoef();
  const c = pickInsideCoef();
  // Ensure b is positive on easy so the inside reads as "x + c" or "bx + c"
  if (opts.difficulty === "easy") b = Math.abs(b);
  const constantFirst = opts.difficulty !== "easy" && Math.random() < 0.4;
  let inside: string;
  if (constantFirst) {
    inside = appendTerm("", c, "");
    inside = appendTerm(inside, b, "x");
  } else {
    inside = appendTerm("", b, "x");
    inside = appendTerm(inside, c, "");
  }
  const display = `${fmtDistOutside(outside)}(${inside})`;
  const ab = mult * b, ac = mult * c;
  let answer: string;
  if (outside.kind === "dec") {
    answer = appendDecTerm("", ab, "x");
    answer = appendDecTerm(answer, ac, "");
  } else {
    answer = appendTerm("", Math.round(ab), "x");
    answer = appendTerm(answer, Math.round(ac), "");
  }
  if (!answer) answer = "0";
  return { num, display, answer };
}

/** Distributive Property — Distribute AND Combine Like Terms.
 *  Mixes one or two parenthesized groups with stray loose terms, then
 *  the student must distribute and combine. Hard tier also drops in
 *  the implicit "−" before a group like "−(x + 5)".
 *
 *    easy   : ONE group "a(x + c)" plus one loose like-term, |coef|≤6
 *    medium : TWO groups "a(bx+c) + d(ex+f)", |coef|≤9, signs mixed
 *    hard   : TWO groups OR group + loose terms; ~50% chance of an
 *             implicit "−(stuff)" group; |coef|≤12; may include a y term.
 */
function makeDistributeCombine(opts: FluencyOptions, num: number): Problem {
  // Track running sums so the answer is computed alongside display.
  // Sums stay in floating-point so a decimal outside (e.g. 0.5) flows
  // through cleanly. With fraction/integer outside coefficients
  // constrained to divide inside terms evenly, the float math lands
  // on integers exactly; rounding at format time washes any noise.
  let sumX = 0;
  let sumY = 0;
  let sumK = 0;
  let display = "";
  // Whether ANY group/loose term contributed a decimal coefficient.
  // Used to pick which formatter renders the answer.
  let answerIsDecimal = false;

  /** Append a parenthesized group with an arbitrary outside coefficient
   *  (integer OR fraction OR decimal) to the display and update sums.
   *  `mult` is the numeric value of the outside coefficient (e.g. 0.5
   *  for "0.5", -1/3 for "−1/3"). */
  const addGroup = (
    outside: DistOutside,
    mult: number,
    b: number,
    c: number,
    d: number
  ) => {
    let inside = "";
    if (b !== 0) inside = appendTerm(inside, b, "x");
    if (c !== 0) inside = appendTerm(inside, c, "y");
    if (d !== 0) inside = appendTerm(inside, d, "");
    if (!inside) inside = "0";
    const aPart = fmtDistOutside(outside);
    const piece = `${aPart}(${inside})`;
    if (!display) display = piece;
    else display = mult < 0
      ? `${display} ${piece.startsWith("−") ? piece : `+ ${piece}`}`
      : `${display} + ${piece}`;
    sumX += mult * b;
    sumY += mult * c;
    sumK += mult * d;
    if (outside.kind === "dec") answerIsDecimal = true;
  };

  /** Append a loose (un-grouped) term to the display and update sums. */
  const addLoose = (coef: number, kind: "x" | "y" | "k") => {
    if (coef === 0) return;
    const v = kind === "k" ? "" : kind;
    display = display ? appendTerm(display, coef, v) : appendTerm("", coef, v);
    if (kind === "x") sumX += coef;
    else if (kind === "y") sumY += coef;
    else sumK += coef;
  };

  const cap = opts.difficulty === "easy" ? 6 : opts.difficulty === "medium" ? 9 : 12;
  const useY = opts.difficulty === "hard" && Math.random() < 0.5;
  const pickCoef = (allowZero = false) => {
    let v = rnd(-cap, cap);
    if (!allowZero && v === 0) v = 1;
    return v;
  };
  const pickInsideForDen = (den: number): number => {
    if (den === 1) return pickCoef();
    return pickMultipleOf(den, cap);
  };

  // Decide whether THIS problem uses a rational/decimal outside on
  // one of its groups. With both toggles on, ~⅔ of problems get a
  // rational group; with one toggle on, ~½ do. HARD always mixes
  // rational coefficients in, toggles or not.
  const wantFrac = !!opts.distributeIncludeFractions || opts.difficulty === "hard";
  const wantDec = !!opts.distributeIncludeDecimals || opts.difficulty === "hard";
  const useRationalThisProblem =
    (wantFrac || wantDec) && Math.random() < (wantFrac && wantDec ? 0.66 : 0.5);
  const useDecKind =
    useRationalThisProblem && wantDec && (!wantFrac || Math.random() < 0.5);

  // Build an integer-outside DistOutside for a given signed coef so the
  // group renderer can share one entrypoint.
  const intOutside = (v: number): DistOutside => ({ kind: "int", value: v });

  if (opts.difficulty === "easy") {
    // One group + one stray like-term. Group outside can be the
    // rational/decimal flavour if toggles are on.
    let outside: DistOutside;
    let mult: number;
    let den = 1;
    if (useRationalThisProblem && useDecKind) {
      const d = pickDecOutside(false);
      outside = { kind: "dec", value: Math.abs(d.value) };
      mult = Math.abs(d.value);
      den = d.effDen;
    } else if (useRationalThisProblem) {
      const f = pickFracOutside(false);
      outside = { kind: "frac", ...f, sign: 1 };
      mult = f.num / f.den;
      den = f.den;
    } else {
      const a = rnd(2, 5);
      outside = intOutside(a);
      mult = a;
    }
    const b = Math.abs(pickInsideForDen(den)) || den; // keep easy positive
    const c = Math.abs(pickInsideForDen(den)) || den;
    addGroup(outside, mult, b, 0, c);
    if (Math.random() < 0.5) addLoose(pickCoef(), "x");
    else addLoose(pickCoef(), "k");
  } else if (opts.difficulty === "medium") {
    // Two groups. If rationals are on, the FIRST group uses a rational
    // outside; the second stays integer so the algebra stays clean.
    let outside1: DistOutside;
    let mult1: number;
    let den1 = 1;
    if (useRationalThisProblem && useDecKind) {
      const d = pickDecOutside(true);
      outside1 = { kind: "dec", value: d.value };
      mult1 = d.value;
      den1 = d.effDen;
    } else if (useRationalThisProblem) {
      const f = pickFracOutside(true);
      outside1 = { kind: "frac", ...f };
      mult1 = (f.sign * f.num) / f.den;
      den1 = f.den;
    } else {
      const a1 = Math.random() < 0.7 ? rnd(2, 6) : -rnd(2, 6);
      outside1 = intOutside(a1);
      mult1 = a1;
    }
    const b1 = pickInsideForDen(den1);
    const c1 = pickInsideForDen(den1);
    addGroup(outside1, mult1, b1, 0, c1);

    const a2 = Math.random() < 0.5 ? rnd(2, 6) : -rnd(2, 6);
    const b2 = pickCoef();
    const c2 = pickCoef();
    addGroup(intOutside(a2), a2, b2, 0, c2);
  } else {
    // Hard: two groups OR group + loose terms; ~50% chance one of
    // the groups is the implicit-negative "−(…)" form. If rationals
    // are on, the FIRST group is the rational/decimal flavour.
    let outside1: DistOutside;
    let mult1: number;
    let den1 = 1;
    if (useRationalThisProblem && useDecKind) {
      const d = pickDecOutside(true);
      outside1 = { kind: "dec", value: d.value };
      mult1 = d.value;
      den1 = d.effDen;
    } else if (useRationalThisProblem) {
      const f = pickFracOutside(true);
      outside1 = { kind: "frac", ...f };
      mult1 = (f.sign * f.num) / f.den;
      den1 = f.den;
    } else {
      const useImplicitNeg = Math.random() < 0.5;
      const a1 = useImplicitNeg
        ? -1
        : Math.random() < 0.5 ? rnd(2, 8) : -rnd(2, 8);
      outside1 = intOutside(a1);
      mult1 = a1;
    }
    const b1 = pickInsideForDen(den1);
    const c1Y = useY && Math.random() < 0.5 ? pickInsideForDen(den1) : 0;
    const d1 = pickInsideForDen(den1);
    addGroup(outside1, mult1, b1, c1Y, d1);
    if (Math.random() < 0.7) {
      const a2 = Math.random() < 0.5 ? rnd(2, 8) : -rnd(2, 8);
      const b2 = pickCoef();
      const c2Y = useY && Math.random() < 0.5 ? pickCoef() : 0;
      const d2 = pickCoef();
      addGroup(intOutside(a2), a2, b2, c2Y, d2);
    } else {
      addLoose(pickCoef(), Math.random() < 0.5 ? "x" : "k");
      if (Math.random() < 0.5) addLoose(pickCoef(), useY && Math.random() < 0.5 ? "y" : "k");
    }
  }

  // Build the simplified answer. Fraction-outside problems are
  // constructed to land on integer coefficients (inside terms are
  // multiples of the denominator), so we round the float sums to wash
  // any FP noise. Decimal-outside problems may keep a decimal coef on
  // the rational group's contribution and are formatted via the
  // decimal formatter.
  let answer = "";
  if (answerIsDecimal) {
    answer = appendDecTerm(answer, sumX, "x");
    if (useY) answer = appendDecTerm(answer, sumY, "y");
    answer = appendDecTerm(answer, sumK, "");
  } else {
    answer = appendTerm(answer, Math.round(sumX), "x");
    if (useY) answer = appendTerm(answer, Math.round(sumY), "y");
    answer = appendTerm(answer, Math.round(sumK), "");
  }
  if (!answer) answer = "0";

  return { num, display, answer };
}

function makeIntegerMixed(opts: FluencyOptions, num: number): Problem {
  // Rotate through the four operations so each worksheet of 20 gets ~5
  // of each. Using num % 4 instead of random keeps the spread balanced.
  switch (num % 4) {
    case 0: return makeIntegerAdd(opts, num);
    case 1: return makeIntegerSub(opts, num);
    case 2: return makeIntegerMul(opts, num);
    default: return makeIntegerDiv(opts, num);
  }
}

// ─────────────────────────────────────────────────────────────────────
// Fraction-with-decimal problems (rational topics, opt-in toggle)
// ─────────────────────────────────────────────────────────────────────

/** One operand is a fraction, the other a decimal; the operation matches
 *  the topic. Fractions stick to terminating-friendly denominators so
 *  the answer key can show BOTH forms ("5/4 = 1.25") whenever the result
 *  terminates. Signs are baked in like the rest of the rational drill. */
function makeFracDecProblem(opts: FluencyOptions, idx: number, baseT: FluencyTopic): Problem {
  const op =
    baseT === "add-fractions" ? "+"
    : baseT === "subtract-fractions" ? "−"
    : baseT === "multiply-fractions" ? "×"
    : "÷";

  // Multiplying/dividing compounds the denominators, so those ops stick
  // to 1-place decimals and the friendliest fraction denominators —
  // otherwise answers land on 800ths. Adding/subtracting can afford a
  // wider range.
  const isMulDiv = op === "×" || op === "÷";
  const dens = opts.difficulty === "easy" || isMulDiv
    ? [2, 4, 5, 10]
    : [2, 4, 5, 8, 10, 20];
  const fd = dens[rnd(0, dens.length - 1)];
  let fn = rnd(1, fd - 1);
  // Hard mixes improper / mixed-number fractions into the rotation.
  if (opts.difficulty === "hard" && randomBool()) fn += fd * rnd(1, 2);
  if (randomBool()) fn = -fn;

  const places = opts.difficulty === "easy" || isMulDiv ? 1 : rnd(1, 2);
  const dd = 10 ** places;
  let dn = rnd(1, opts.difficulty === "easy" || isMulDiv ? 2 * dd - 1 : 4 * dd - 1);
  if (dn % 10 === 0) dn += 1; // keep the printed decimal at full places
  if (opts.difficulty !== "easy" && randomBool()) dn = -dn;

  // Randomize operand order, then compute A (op) B in fraction space.
  const fracFirst = randomBool();
  const A = fracFirst ? { n: fn, d: fd } : { n: dn, d: dd };
  const B = fracFirst ? { n: dn, d: dd } : { n: fn, d: fd };
  let rn: number;
  let rd: number;
  if (op === "+") { rn = A.n * B.d + B.n * A.d; rd = A.d * B.d; }
  else if (op === "−") { rn = A.n * B.d - B.n * A.d; rd = A.d * B.d; }
  else if (op === "×") { rn = A.n * B.n; rd = A.d * B.d; }
  else { rn = A.n * B.d; rd = A.d * B.n; }
  [rn, rd] = simplify(rn, rd);

  const fStr = fmtFraction(fn, fd, opts.formats.mixed);
  const dAbs = (Math.abs(dn) / dd).toFixed(places);
  const fDisp = fn < 0 ? wrapNegative(fStr) : fStr;
  const dDisp = dn < 0 ? `(−${dAbs})` : dAbs;
  const display = fracFirst
    ? `${fDisp} ${op} ${dDisp}`
    : `${dDisp} ${op} ${fDisp}`;

  // Answer: simplified fraction, plus the decimal form when it
  // terminates (denominator has only 2s and 5s).
  let answer = fmtFraction(rn, rd, opts.formats.mixed);
  let strip = rd;
  while (strip % 2 === 0) strip /= 2;
  while (strip % 5 === 0) strip /= 5;
  if (strip === 1 && rd !== 1) {
    answer = `${answer} = ${trimDecimal(rn / rd, 6)}`;
  }
  return { num: idx, display, answer };
}

// ─────────────────────────────────────────────────────────────────────
// Number lines for inequality worksheets
// ─────────────────────────────────────────────────────────────────────

/** Build the worksheet (blank) and answer-key (graphed) number-line
 *  shapes for an inequality problem by parsing its answer string.
 *  Handles the four answer shapes the generators emit:
 *    "x < 5"                       simple ray
 *    "−3 < x < 5"                  AND compound (also ≤)
 *    "x < −3  or  x > 5"           OR compound
 *    "no solution" / "all real numbers"
 *  Returns undefined for anything else so the problem just renders
 *  without a number line rather than with a wrong one. */
function numberLinesFor(answer: string): { shape: ShapeSpec; answerShape: ShapeSpec } | undefined {
  // Normalize the typographic minus to ASCII so one regex handles both.
  const a = answer.replace(/−/g, "-").replace(/\s+/g, " ").trim();

  type Ray = { boundary: number; open: boolean; dir: "left" | "right" };
  let rays: Ray[] = [];
  let between: { lo: number; hi: number; loOpen: boolean; hiOpen: boolean } | null = null;
  let allReal = false;
  let noSolution = false;

  const rayFor = (op: string, v: number): Ray => ({
    boundary: v,
    open: op === "<" || op === ">",
    dir: op === "<" || op === "≤" ? "left" : "right",
  });

  let m: RegExpExecArray | null;
  const NUM = "(-?\\d+(?:\\.\\d+)?)"; // integer or decimal boundary
  const orRe = new RegExp(`^x ?([<>≤≥]) ?${NUM} or x ?([<>≤≥]) ?${NUM}$`);
  const andRe = new RegExp(`^${NUM} ?([<≤]) ?x ?([<≤]) ?${NUM}$`);
  const simpleRe = new RegExp(`^x ?([<>≤≥]) ?${NUM}$`);
  if (a === "no solution") {
    noSolution = true;
  } else if (a === "all real numbers") {
    allReal = true;
  } else if ((m = orRe.exec(a))) {
    rays = [rayFor(m[1], parseFloat(m[2])), rayFor(m[3], parseFloat(m[4]))];
  } else if ((m = andRe.exec(a))) {
    between = {
      lo: parseFloat(m[1]),
      hi: parseFloat(m[4]),
      loOpen: m[2] === "<",
      hiOpen: m[3] === "<",
    };
  } else if ((m = simpleRe.exec(a))) {
    rays = [rayFor(m[1], parseFloat(m[2]))];
  } else {
    return undefined;
  }

  // Window: pad 3 ticks past every boundary; center a small default
  // window on 0 for the no-boundary answers.
  const bounds = between
    ? [between.lo, between.hi]
    : rays.map((r) => r.boundary);
  const lo = bounds.length ? Math.floor(Math.min(...bounds)) : -5;
  const hi = bounds.length ? Math.ceil(Math.max(...bounds)) : 5;
  let min = lo - 3;
  let max = hi + 3;
  // Keep at least 8 ticks of room so short windows don't look cramped.
  while (max - min < 8) { min -= 1; max += 1; }
  const step = max - min > 14 ? 2 : 1;

  const blank: ShapeSpec = { kind: "numberline", labels: {}, numberline: { min, max, step } };
  const graphed: ShapeSpec = { kind: "numberline", labels: {}, numberline: { min, max, step, points: [], segments: [] } };
  const nl = graphed.numberline!;

  if (allReal) {
    nl.segments!.push({ from: "-inf", to: "+inf" });
  } else if (between) {
    nl.points!.push({ x: between.lo, open: between.loOpen }, { x: between.hi, open: between.hiOpen });
    nl.segments!.push({ from: between.lo, to: between.hi });
  } else if (!noSolution) {
    for (const r of rays) {
      nl.points!.push({ x: r.boundary, open: r.open });
      nl.segments!.push(
        r.dir === "left" ? { from: "-inf", to: r.boundary } : { from: r.boundary, to: "+inf" }
      );
    }
  }
  // noSolution: the graphed line stays empty — the key's answer text
  // ("no solution") is the point.

  return { shape: blank, answerShape: graphed };
}

export function generateProblems(opts: FluencyOptions): Problem[] {
  const out: Problem[] = [];
  for (let i = 0; i < opts.count; i++) {
    const t = opts.topic;
    let p: Problem;
    if (GRAPHING_TOPICS.has(t)) {
      switch (t) {
        case "gr-unit-rate":         p = makeUnitRate(opts, i + 1); break;
        case "gr-rate-table":        p = makeRateTable(opts, i + 1); break;
        case "gr-rate-convert":      p = makeRateConvert(opts, i + 1); break;
        case "gr-prop-k-table":      p = makePropKTable(opts, i + 1); break;
        case "gr-prop-k-graph":      p = makePropKGraph(opts, i + 1); break;
        case "gr-prop-equation":     p = makePropEquation(opts, i + 1); break;
        case "gr-prop-table-yn":     p = makePropTableYN(opts, i + 1); break;
        case "gr-prop-graph-yn":     p = makePropGraphYN(opts, i + 1); break;
        case "gr-slope-points":      p = makeSlopePoints(opts, i + 1); break;
        case "gr-slope-graph":       p = makeSlopeGraph(opts, i + 1); break;
        case "gr-slope-table":       p = makeSlopeTable(opts, i + 1); break;
        case "gr-slope-verbal":      p = makeSlopeVerbal(opts, i + 1); break;
        case "gr-slope-classify":    p = makeSlopeClassify(opts, i + 1); break;
        case "gr-si-identify":       p = makeSIIdentify(opts, i + 1); break;
        case "gr-si-mb":             p = makeSIFromMB(opts, i + 1); break;
        case "gr-si-mp":             p = makeSIFromMP(opts, i + 1); break;
        case "gr-si-pp":             p = makeSIFromPP(opts, i + 1); break;
        case "gr-si-graph":          p = makeSIFromGraph(opts, i + 1); break;
        case "gr-std-to-si":         p = makeStdToSI(opts, i + 1); break;
        case "gr-si-to-std":         p = makeSIToStd(opts, i + 1); break;
        case "gr-ps-write":          p = makePointSlopeWrite(opts, i + 1); break;
        case "gr-ps-to-si":          p = makePointSlopeToSI(opts, i + 1); break;
        case "gr-graph-si":          p = makeGraphSI(opts, i + 1); break;
        case "gr-graph-table":       p = makeGraphTable(opts, i + 1); break;
        case "gr-graph-std":         p = makeGraphStd(opts, i + 1); break;
        case "gr-graph-points":      p = makeGraphPoints(opts, i + 1); break;
        case "gr-fn-vlt-graph":      p = makeFnVLTGraph(opts, i + 1); break;
        case "gr-fn-table":          p = makeFnTable(opts, i + 1); break;
        case "gr-fn-eval":           p = makeFnEval(opts, i + 1); break;
        case "gr-fn-reverse":        p = makeFnReverse(opts, i + 1); break;
        case "gr-fn-domain-range":   p = makeFnDomainRange(opts, i + 1); break;
        case "gr-nonlinear-classify":p = makeNonlinearClassify(opts, i + 1); break;
        case "gr-rate-compare":      p = makeRateCompare(opts, i + 1); break;
        case "gr-linear-compare":    p = makeLinearCompare(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (GEOMETRY_TOPICS.has(t)) {
      switch (t) {
        case "geo-rect-area":             p = makeRectArea(opts, i + 1); break;
        case "geo-rect-perim":            p = makeRectPerim(opts, i + 1); break;
        case "geo-square":                p = makeSquare(opts, i + 1); break;
        case "geo-tri-area":              p = makeTriArea(opts, i + 1); break;
        case "geo-parallelogram-area":    p = makeParallelogramArea(opts, i + 1); break;
        case "geo-trap-area":             p = makeTrapArea(opts, i + 1); break;
        case "geo-circle-area":           p = makeCircleArea(opts, i + 1); break;
        case "geo-circle-circumference":  p = makeCircleCircumference(opts, i + 1); break;
        case "geo-rect-find-area":        p = makeRectFindFromArea(opts, i + 1); break;
        case "geo-rect-find-perim":       p = makeRectFindFromPerim(opts, i + 1); break;
        case "geo-square-find":           p = makeSquareFind(opts, i + 1); break;
        case "geo-tri-find-base":         p = makeTriFindBase(opts, i + 1); break;
        case "geo-tri-find-height":       p = makeTriFindHeight(opts, i + 1); break;
        case "geo-circle-find-r-area":    p = makeCircleFindRFromArea(opts, i + 1); break;
        case "geo-circle-find-r-circ":    p = makeCircleFindRFromCirc(opts, i + 1); break;
        case "geo-rect-prism-v":          p = makeRectPrismV(opts, i + 1); break;
        case "geo-rect-prism-sa":         p = makeRectPrismSA(opts, i + 1); break;
        case "geo-cube":                  p = makeCube(opts, i + 1); break;
        case "geo-tri-prism-v":           p = makeTriPrismV(opts, i + 1); break;
        case "geo-tri-prism-sa":          p = makeTriPrismSA(opts, i + 1); break;
        case "geo-cylinder-v":            p = makeCylinderV(opts, i + 1); break;
        case "geo-cylinder-sa":           p = makeCylinderSA(opts, i + 1); break;
        case "geo-cone-v":                p = makeConeV(opts, i + 1); break;
        case "geo-sphere-v":              p = makeSphereV(opts, i + 1); break;
        case "geo-pyramid-v":             p = makePyramidV(opts, i + 1); break;
        case "geo-rect-prism-find-h":     p = makeRectPrismFindH(opts, i + 1); break;
        case "geo-cube-find-s":           p = makeCubeFindS(opts, i + 1); break;
        case "geo-cylinder-find-h":       p = makeCylinderFindH(opts, i + 1); break;
        case "geo-cylinder-find-r":       p = makeCylinderFindR(opts, i + 1); break;
        case "geo-cone-find-h":           p = makeConeFindH(opts, i + 1); break;
        case "geo-sphere-find-r":         p = makeSphereFindR(opts, i + 1); break;
        case "geo-pyth-hyp":              p = makePythHyp(opts, i + 1); break;
        case "geo-pyth-leg":              p = makePythLeg(opts, i + 1); break;
        case "geo-pyth-check":            p = makePythCheck(opts, i + 1); break;
        case "geo-pyth-word":             p = makePythWord(opts, i + 1); break;
        case "geo-coord-distance":        p = makeCoordDistance(opts, i + 1); break;
        case "geo-coord-midpoint":        p = makeCoordMidpoint(opts, i + 1); break;
        case "geo-coord-slope":           p = makeCoordSlope(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (INEQUALITY_TOPICS.has(t)) {
      switch (t) {
        case "ineq-one-add":          p = makeIneqOneAdd(opts, i + 1); break;
        case "ineq-one-sub":          p = makeIneqOneSub(opts, i + 1); break;
        case "ineq-one-mul":          p = makeIneqOneMul(opts, i + 1); break;
        case "ineq-one-div":          p = makeIneqOneDiv(opts, i + 1); break;
        case "ineq-one-mixed":        p = makeIneqOneMixed(opts, i + 1); break;
        case "ineq-two-pos":          p = makeIneqTwoPos(opts, i + 1); break;
        case "ineq-two-neg":          p = makeIneqTwoNeg(opts, i + 1); break;
        case "ineq-two-rational":     p = makeIneqTwoRational(opts, i + 1); break;
        case "ineq-two-dist":         p = makeIneqTwoDist(opts, i + 1); break;
        case "ineq-multi-combine":    p = makeIneqMultiCombine(opts, i + 1); break;
        case "ineq-multi-dist":       p = makeIneqMultiDist(opts, i + 1); break;
        case "ineq-multi-both":       p = makeIneqMultiBoth(opts, i + 1); break;
        case "ineq-multi-full":       p = makeIneqMultiFull(opts, i + 1); break;
        case "ineq-multi-special":    p = makeIneqMultiSpecial(opts, i + 1); break;
        case "ineq-compound-and":     p = makeIneqCompoundAnd(opts, i + 1); break;
        case "ineq-compound-or":      p = makeIneqCompoundOr(opts, i + 1); break;
        case "ineq-compound-translate": p = makeIneqCompoundTranslate(opts, i + 1); break;
        case "ineq-abs-less":         p = makeIneqAbsLess(opts, i + 1); break;
        case "ineq-abs-greater":      p = makeIneqAbsGreater(opts, i + 1); break;
        case "ineq-abs-isolate":      p = makeIneqAbsIsolate(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
      // Every inequality worksheet asks students to graph the solution,
      // so give each problem a blank number line to graph on and put
      // the graphed solution on the answer key.
      const nl = numberLinesFor(p.answer);
      if (nl) p = { ...p, shape: nl.shape, answerShape: nl.answerShape };
    } else if (EQUATION_TOPICS.has(t)) {
      switch (t) {
        case "eq-one-add":       p = makeOneStepAdd(opts, i + 1); break;
        case "eq-one-sub":       p = makeOneStepSub(opts, i + 1); break;
        case "eq-one-mul":       p = makeOneStepMul(opts, i + 1); break;
        case "eq-one-div":       p = makeOneStepDiv(opts, i + 1); break;
        case "eq-one-mixed":     p = makeOneStepMixed(opts, i + 1); break;
        case "eq-two-pos":       p = makeTwoStepPos(opts, i + 1); break;
        case "eq-two-neg":       p = makeTwoStepNeg(opts, i + 1); break;
        case "eq-two-rational":  p = makeTwoStepRational(opts, i + 1); break;
        case "eq-two-dist":      p = makeTwoStepDist(opts, i + 1); break;
        case "eq-multi-combine": p = makeMultiCombine(opts, i + 1); break;
        case "eq-multi-dist":    p = makeMultiDist(opts, i + 1); break;
        case "eq-multi-both":    p = makeMultiBoth(opts, i + 1); break;
        case "eq-multi-full":    p = makeMultiFull(opts, i + 1); break;
        case "eq-multi-special": p = makeMultiSpecial(opts, i + 1); break;
        case "eq-literal":       p = makeLiteral(opts, i + 1); break;
        case "eq-prop":          p = makeProportion(opts, i + 1); break;
        case "eq-prop-word":     p = makePropWord(opts, i + 1); break;
        case "eq-abs-simple":    p = makeAbsSimple(opts, i + 1); break;
        case "eq-abs-coef":      p = makeAbsCoef(opts, i + 1); break;
        case "eq-abs-isolate":   p = makeAbsIsolate(opts, i + 1); break;
        case "eq-sys-sub":       p = makeSysSub(opts, i + 1); break;
        case "eq-sys-elim":      p = makeSysElim(opts, i + 1); break;
        case "eq-sys-special":   p = makeSysSpecial(opts, i + 1); break;
        case "eq-sys-word":      p = makeSysWord(opts, i + 1); break;
        case "eq-quad-sqrt":     p = makeQuadSqrt(opts, i + 1); break;
        case "eq-quad-trans":    p = makeQuadTrans(opts, i + 1); break;
        case "eq-quad-fac-a1":   p = makeQuadFacA1(opts, i + 1); break;
        case "eq-quad-fac-an":   p = makeQuadFacAn(opts, i + 1); break;
        case "eq-quad-diff":     p = makeQuadDiff(opts, i + 1); break;
        case "eq-quad-formula":  p = makeQuadFormula(opts, i + 1); break;
        case "eq-quad-complete": p = makeQuadComplete(opts, i + 1); break;
        case "eq-rad-single":    p = makeRadSingle(opts, i + 1); break;
        case "eq-rad-double":    p = makeRadDouble(opts, i + 1); break;
        case "eq-rad-linear":    p = makeRadLinear(opts, i + 1); break;
        case "eq-rat-simple":    p = makeRatSimple(opts, i + 1); break;
        case "eq-rat-linear":    p = makeRatLinear(opts, i + 1); break;
        case "eq-rat-lcd":       p = makeRatLCD(opts, i + 1); break;
        case "eq-exp-bases":     p = makeExpBases(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (CONVERTING_TOPICS.has(t)) {
      switch (t) {
        case "frac-to-dec-term": p = makeFractionToDec(opts, i + 1, false); break;
        case "frac-to-dec-rep":  p = makeFractionToDec(opts, i + 1, true); break;
        case "dec-to-frac-term": p = makeDecToFrac(opts, i + 1, false); break;
        case "dec-to-frac-rep":  p = makeDecToFrac(opts, i + 1, true); break;
        case "frac-to-percent":  p = makeFracToPercent(opts, i + 1); break;
        case "percent-to-frac":  p = makePercentToFrac(opts, i + 1); break;
        case "dec-to-percent":   p = makeDecToPercent(opts, i + 1); break;
        case "percent-to-dec":   p = makePercentToDec(opts, i + 1); break;
        case "mixed-to-improper":p = makeMixedToImproper(opts, i + 1); break;
        case "improper-to-mixed":p = makeImproperToMixed(opts, i + 1); break;
        case "compare-rationals":p = makeCompareRationals(opts, i + 1); break;
        case "order-rationals":  p = makeOrderRationals(opts, i + 1); break;
        case "equivalent-forms": p = makeEquivalentForms(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (INTEGER_TOPICS.has(t)) {
      switch (t) {
        case "add-integers":      p = makeIntegerAdd(opts, i + 1); break;
        case "subtract-integers": p = makeIntegerSub(opts, i + 1); break;
        case "multiply-integers": p = makeIntegerMul(opts, i + 1); break;
        case "divide-integers":   p = makeIntegerDiv(opts, i + 1); break;
        case "integer-mixed":     p = makeIntegerMixed(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (NUMBER_THEORY_TOPICS.has(t)) {
      switch (t) {
        case "prime-factorization":  p = makePrimeFactorisation(opts, i + 1); break;
        case "perfect-square-roots": p = makePerfectSquareRoot(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (PERCENT_TOPICS.has(t)) {
      switch (t) {
        case "percent-of-change":    p = makePercentOfChange(opts, i + 1); break;
        case "percent-application":  p = makePercentApplication(opts, i + 1); break;
        case "simple-interest":      p = makeSimpleInterest(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (ALGEBRAIC_EXPR_TOPICS.has(t)) {
      switch (t) {
        case "combine-like-terms":   p = makeCombineLikeTerms(opts, i + 1); break;
        case "distribute-expand":    p = makeDistributeExpand(opts, i + 1); break;
        case "distribute-combine":   p = makeDistributeCombine(opts, i + 1); break;
        default: p = { num: i + 1, display: "?", answer: "?" };
      }
    } else if (RATIONAL_TOPICS.has(t)) {
      // Reuse the fraction generators with allowNegatives forced on. For
      // rational-mixed we rotate the four operations 4 problems at a
      // time so every worksheet gets a balanced spread.
      const baseT: FluencyTopic =
        t === "rational-mixed"
          ? (["add-fractions", "subtract-fractions", "multiply-fractions", "divide-fractions"][
              i % 4
            ] as FluencyTopic)
          : RATIONAL_TO_FRACTION[t];
      const shimmed: FluencyOptions = {
        ...opts,
        topic: baseT,
        allowNegatives: true,
      };
      if (opts.rationalIncludeFracDec && i % 3 === 1) {
        // Toggle on → every third problem pairs a fraction with a
        // decimal using this topic's operation.
        p = makeFracDecProblem(shimmed, i + 1, baseT);
      } else if (baseT === "multiply-fractions" || baseT === "divide-fractions") {
        p = generateFractionMulDivProblem(shimmed, i + 1);
      } else {
        p = generateFractionAddSubProblem(shimmed, i + 1);
      }
    } else if (DECIMAL_TOPICS.has(t)) {
      p = generateDecimalProblem(opts, i + 1);
    } else if (FRACTION_MULDIV_TOPICS.has(t)) {
      p = generateFractionMulDivProblem(opts, i + 1);
    } else {
      p = generateFractionAddSubProblem(opts, i + 1);
    }
    out.push(p);
  }
  return out;
}

/** Pretty topic labels for the UI. */
export const TOPIC_LABELS: Record<FluencyTopic, string> = {
  // Integer operations — surface first since they're the entry into
  // signed-number fluency for grade 7.
  "add-integers": "Adding Integers",
  "subtract-integers": "Subtracting Integers",
  "multiply-integers": "Multiplying Integers",
  "divide-integers": "Dividing Integers",
  "integer-mixed": "Integers: Mixed Operations",
  // Rational operations — signed fractions. Sits right after integers in
  // the picker so the progression integers → rationals is obvious.
  "add-rationals": "Adding Rational Numbers",
  "subtract-rationals": "Subtracting Rational Numbers",
  "multiply-rationals": "Multiplying Rational Numbers",
  "divide-rationals": "Dividing Rational Numbers",
  "rational-mixed": "Rational Numbers: Mixed Operations",
  // Number-theory drill (7.NS.5, 7.NS.6 — Indiana-specific).
  "prime-factorization": "Prime Factorisation",
  "perfect-square-roots": "Perfect Square Roots",
  // Percent applications (7.RP.2).
  "percent-of-change": "Percent of Change",
  "percent-application": "Tax / Tip / Markup / Discount",
  "simple-interest": "Simple Interest",
  // Algebraic expressions (7.AF.1).
  "combine-like-terms": "Combine Like Terms",
  "distribute-expand": "Distribute (Expand)",
  "distribute-combine": "Distribute & Combine Like Terms",
  "add-fractions": "Adding Fractions",
  "subtract-fractions": "Subtracting Fractions",
  "multiply-fractions": "Multiplying Fractions",
  "divide-fractions": "Dividing Fractions",
  "add-decimals": "Adding Decimals",
  "subtract-decimals": "Subtracting Decimals",
  "multiply-decimals": "Multiplying Decimals",
  "divide-decimals": "Dividing Decimals",
  "frac-to-dec-term": "Fraction → Decimal (Terminating)",
  "frac-to-dec-rep": "Fraction → Decimal (Repeating)",
  "dec-to-frac-term": "Decimal → Fraction (Terminating)",
  "dec-to-frac-rep": "Decimal → Fraction (Repeating)",
  "frac-to-percent": "Fraction → Percent",
  "percent-to-frac": "Percent → Fraction",
  "dec-to-percent": "Decimal → Percent",
  "percent-to-dec": "Percent → Decimal",
  "mixed-to-improper": "Mixed → Improper",
  "improper-to-mixed": "Improper → Mixed",
  "compare-rationals": "Compare Rationals",
  "order-rationals": "Order Rationals",
  "equivalent-forms": "Equivalent Forms",
  "eq-one-add": "One-Step: x + a = b",
  "eq-one-sub": "One-Step: x − a = b",
  "eq-one-mul": "One-Step: ax = b",
  "eq-one-div": "One-Step: x/a = b",
  "eq-one-mixed": "One-Step: Mixed",
  "eq-two-pos": "Two-Step: ax + b = c",
  "eq-two-neg": "Two-Step with Negatives",
  "eq-two-rational": "Two-Step with Rationals",
  "eq-two-dist": "Two-Step: p(x + q) = r",
  "eq-multi-combine": "Multi-Step: Combine Like Terms",
  "eq-multi-dist": "Multi-Step: Distributive",
  "eq-multi-both": "Variables on Both Sides",
  "eq-multi-full": "Multi-Step: Full Mash-Up",
  "eq-multi-special": "No Solution / Infinite Solutions",
  "eq-literal": "Literal Equations",
  "eq-prop": "Proportions: a/b = c/x",
  "eq-prop-word": "Proportions: Word Problems",
  "eq-abs-simple": "Absolute Value: |x + a| = b",
  "eq-abs-coef": "Absolute Value: |ax + b| = c",
  "eq-abs-isolate": "Absolute Value: Isolate First",
  "eq-sys-sub": "Systems: Substitution",
  "eq-sys-elim": "Systems: Elimination",
  "eq-sys-special": "Systems: No Sol / Infinite",
  "eq-sys-word": "Systems: Word Problems",
  "eq-quad-sqrt": "Quadratic: Square Root Method",
  "eq-quad-trans": "Quadratic: (x − h)² = k",
  "eq-quad-fac-a1": "Quadratic: Factor (a = 1)",
  "eq-quad-fac-an": "Quadratic: Factor (a > 1)",
  "eq-quad-diff": "Quadratic: Difference of Squares",
  "eq-quad-formula": "Quadratic Formula",
  "eq-quad-complete": "Completing the Square",
  "eq-rad-single": "Radical: √(ax + b) = c",
  "eq-rad-double": "Radical: Two Radicals",
  "eq-rad-linear": "Radical: With Linear (Extraneous)",
  "eq-rat-simple": "Rational: a/x = b",
  "eq-rat-linear": "Rational: (ax + b)/c = d",
  "eq-rat-lcd": "Rational: Multiply by LCD",
  "eq-exp-bases": "Exponential: Matching Bases",
  // A representative "<" stands in for the mix of inequality symbols —
  // the old "(op)" placeholder printed literally on worksheet titles.
  "ineq-one-add": "One-Step: x + a < b",
  "ineq-one-sub": "One-Step: x − a < b",
  "ineq-one-mul": "One-Step: ax < b",
  "ineq-one-div": "One-Step: x/a < b",
  "ineq-one-mixed": "One-Step: Mixed",
  "ineq-two-pos": "Two-Step: ax + b < c",
  "ineq-two-neg": "Two-Step with Negatives (Flip)",
  "ineq-two-rational": "Two-Step with Rationals",
  "ineq-two-dist": "Two-Step: p(x + q) < r",
  "ineq-multi-combine": "Multi-Step: Combine Like Terms",
  "ineq-multi-dist": "Multi-Step: Distributive",
  "ineq-multi-both": "Variables on Both Sides",
  "ineq-multi-full": "Multi-Step: Full Mash-Up",
  "ineq-multi-special": "No Solution / All Real Numbers",
  "ineq-compound-and": "Compound: AND (a < x < b)",
  "ineq-compound-or": "Compound: OR (x < a or x > b)",
  "ineq-compound-translate": "Compound: Translate from Words",
  "ineq-abs-less": "Absolute Value: |x + a| < b (AND)",
  "ineq-abs-greater": "Absolute Value: |x + a| > b (OR)",
  "ineq-abs-isolate": "Absolute Value: Isolate First",
  "geo-rect-area": "Rectangle: Area",
  "geo-rect-perim": "Rectangle: Perimeter",
  "geo-square": "Square: Area / Perimeter",
  "geo-tri-area": "Triangle: Area",
  "geo-parallelogram-area": "Parallelogram: Area",
  "geo-trap-area": "Trapezoid: Area",
  "geo-circle-area": "Circle: Area",
  "geo-circle-circumference": "Circle: Circumference",
  "geo-rect-find-area": "Rectangle: Find Side from Area",
  "geo-rect-find-perim": "Rectangle: Find Side from Perimeter",
  "geo-square-find": "Square: Find Side",
  "geo-tri-find-base": "Triangle: Find Base from Area",
  "geo-tri-find-height": "Triangle: Find Height from Area",
  "geo-circle-find-r-area": "Circle: Find Radius from Area",
  "geo-circle-find-r-circ": "Circle: Find Radius from Circumference",
  "geo-rect-prism-v": "Rectangular Prism: Volume",
  "geo-rect-prism-sa": "Rectangular Prism: Surface Area",
  "geo-cube": "Cube: Volume / Surface Area",
  "geo-tri-prism-v": "Triangular Prism: Volume",
  "geo-tri-prism-sa": "Triangular Prism: Surface Area",
  "geo-cylinder-v": "Cylinder: Volume",
  "geo-cylinder-sa": "Cylinder: Surface Area",
  "geo-cone-v": "Cone: Volume",
  "geo-sphere-v": "Sphere: Volume",
  "geo-pyramid-v": "Square Pyramid: Volume",
  "geo-rect-prism-find-h": "Rect Prism: Find Height from V",
  "geo-cube-find-s": "Cube: Find Side from V or SA",
  "geo-cylinder-find-h": "Cylinder: Find Height from V",
  "geo-cylinder-find-r": "Cylinder: Find Radius from V",
  "geo-cone-find-h": "Cone: Find Height from V",
  "geo-sphere-find-r": "Sphere: Find Radius from V",
  "geo-pyth-hyp": "Pythagorean: Find Hypotenuse",
  "geo-pyth-leg": "Pythagorean: Find Missing Leg",
  "geo-pyth-check": "Pythagorean: Is It a Right Triangle?",
  "geo-pyth-word": "Pythagorean: Word Problems",
  "geo-coord-distance": "Coordinate: Distance Between Points",
  "geo-coord-midpoint": "Coordinate: Midpoint",
  "geo-coord-slope": "Coordinate: Slope Between Points",
  "gr-unit-rate": "Find a Unit Rate",
  "gr-rate-table": "Rate Table: Complete the Values",
  "gr-rate-convert": "Convert a Rate",
  "gr-prop-k-table": "k from a Table",
  "gr-prop-k-graph": "k from a Graph",
  "gr-prop-equation": "Write y = kx from a Table",
  "gr-prop-table-yn": "Is the Table Proportional?",
  "gr-prop-graph-yn": "Is the Graph Proportional?",
  "gr-slope-points": "Slope from Two Points",
  "gr-slope-graph": "Slope from a Graph",
  "gr-slope-table": "Slope from a Table",
  "gr-slope-verbal": "Slope from a Verbal Description",
  "gr-slope-classify": "Classify Slope (+ / − / 0 / undef.)",
  "gr-si-identify": "Identify m and b from y = mx + b",
  "gr-si-mb": "Write y = mx + b from Slope and Intercept",
  "gr-si-mp": "Write y = mx + b from Slope and a Point",
  "gr-si-pp": "Write y = mx + b from Two Points",
  "gr-si-graph": "Write y = mx + b from a Graph",
  "gr-std-to-si": "Standard → Slope-Intercept",
  "gr-si-to-std": "Slope-Intercept → Standard",
  "gr-ps-write": "Write in Point-Slope Form",
  "gr-ps-to-si": "Point-Slope → Slope-Intercept",
  "gr-graph-si": "Graph y = mx + b",
  "gr-graph-table": "Graph from a Table",
  "gr-graph-std": "Graph from Standard Form",
  "gr-graph-points": "Graph from Two Points",
  "gr-fn-vlt-graph": "Vertical Line Test from a Graph",
  "gr-fn-table": "Function from a Table",
  "gr-fn-eval": "Evaluate f(x)",
  "gr-fn-reverse": "Find x Given f(x)",
  "gr-fn-domain-range": "Domain & Range from a Graph",
  "gr-nonlinear-classify": "Linear vs Nonlinear",
  "gr-rate-compare": "Compare Two Rates",
  "gr-linear-compare": "Compare Two Linear Models",
};

// ─────────────────────────────────────────────────────────────────────
// Per-topic difficulty descriptions
// ─────────────────────────────────────────────────────────────────────
//
// [easy, medium, hard] — shown under the difficulty slider so teachers
// can see EXACTLY what each level changes for the selected topic. The
// Record covers every topic (compiler-enforced), so no topic can fall
// back to a wrong generic description again.

type DifficultyHints = [string, string, string];

// Shared descriptions for families whose levels behave identically.
const H_INT_OPS: DifficultyHints = [
  "Single-digit values (−9 to 9).",
  "Values to ±20.",
  "Values to ±50; tougher division.",
];
const H_FRAC_ADDSUB: DifficultyHints = [
  "Same denominators (no LCD needed).",
  "One denominator divides the other.",
  "Unrelated denominators — find the LCD.",
];
const H_FRAC_MULDIV: DifficultyHints = [
  "Denominators up to 6.",
  "Denominators up to 10.",
  "Denominators up to your max setting.",
];
const H_DEC_ADDSUB: DifficultyHints = [
  "1 decimal place, values under 10.",
  "2 decimal places, values under 100.",
  "Mixed 1–3 decimal places.",
];
const H_CONV_TERM: DifficultyHints = [
  "Halves, fourths, fifths, tenths.",
  "Adds eighths, twentieths, twenty-fifths.",
  "Adds sixteenths, fiftieths, hundredths.",
];
const H_CONV_REP: DifficultyHints = [
  "Denominators 3 and 9.",
  "Adds 6 and 11.",
  "Adds 7, 12, 13 (longer repeating blocks).",
];
const H_EQ_ONE: DifficultyHints = [
  "All positive; numbers to 12.",
  "Negatives mixed in; larger numbers.",
  "Adds decimal and fraction values.",
];
const H_MIXED_FORMS: DifficultyHints = [
  "Whole parts to 5, denominators to 12.",
  "Whole parts to 9.",
  "Whole parts to 15.",
];
const H_EQ_MULTI: DifficultyHints = [
  "Small positive numbers.",
  "Negatives mixed in; larger numbers.",
  "Largest signed numbers.",
];

export const DIFFICULTY_HINTS: Record<FluencyTopic, DifficultyHints> = {
  // ----- Integers -----
  "add-integers": H_INT_OPS,
  "subtract-integers": H_INT_OPS,
  "multiply-integers": H_INT_OPS,
  "divide-integers": H_INT_OPS,
  "integer-mixed": H_INT_OPS,
  // ----- Rationals (signed fractions) -----
  "add-rationals": H_FRAC_ADDSUB,
  "subtract-rationals": H_FRAC_ADDSUB,
  "multiply-rationals": H_FRAC_MULDIV,
  "divide-rationals": H_FRAC_MULDIV,
  "rational-mixed": [
    "Same denominators; small values.",
    "Related denominators.",
    "Unrelated denominators (full LCD).",
  ],
  // ----- Number theory -----
  "prime-factorization": [
    "2–3 prime factors from 2, 3, 5, 7 (numbers to ~200).",
    "3–4 factors; adds 11 (numbers to ~600).",
    "4–5 factors; adds 13 (numbers to ~2500).",
  ],
  "perfect-square-roots": [
    "Squares of 2–9 (4 to 81).",
    "Squares of 2–14 (up to 196).",
    "Squares of 2–25 (up to 625).",
  ],
  // ----- Percent -----
  "percent-of-change": [
    "Starting values 20–100; friendly percents.",
    "Starting values 50–200.",
    "Starting values 100–400; includes 12.5%.",
  ],
  "percent-application": [
    "Prices to $100; 10/20/25/50%.",
    "Prices to $150; more percents.",
    "Prices to $500; includes 4%, 8%, 12%.",
  ],
  "simple-interest": [
    "Principal to $2,000; short terms.",
    "Principal to $5,000; terms to 5 years.",
    "Principal to $20,000; terms to 10 years.",
  ],
  // ----- Algebraic expressions -----
  "combine-like-terms": [
    "3–4 terms, one variable, coefficients to ±5.",
    "4–5 terms, coefficients to ±10.",
    "5–7 terms with two variables — plus fraction/decimal coefficients.",
  ],
  "distribute-expand": [
    "Positive multiplier 2–6, one variable.",
    "Negative multipliers appear; bigger numbers.",
    "Fraction/decimal multipliers and 3-term insides.",
  ],
  "distribute-combine": [
    "One group plus a loose term.",
    "Two groups; negatives mixed in.",
    "Fraction/decimal multipliers and −(…) groups.",
  ],
  // ----- Fractions / decimals -----
  "add-fractions": H_FRAC_ADDSUB,
  "subtract-fractions": H_FRAC_ADDSUB,
  "multiply-fractions": H_FRAC_MULDIV,
  "divide-fractions": H_FRAC_MULDIV,
  "add-decimals": H_DEC_ADDSUB,
  "subtract-decimals": H_DEC_ADDSUB,
  "multiply-decimals": [
    "1-place factors, values under 10.",
    "2-place factors, values under 100.",
    "Mixed 1–3 place factors.",
  ],
  "divide-decimals": [
    "Whole divisors; 1-place quotients.",
    "Divisors to 2 places.",
    "Mixed 1–3 place quotients and divisors.",
  ],
  // ----- Converting -----
  "frac-to-dec-term": H_CONV_TERM,
  "frac-to-dec-rep": H_CONV_REP,
  "dec-to-frac-term": H_CONV_TERM,
  "dec-to-frac-rep": H_CONV_REP,
  "frac-to-percent": H_CONV_TERM,
  "percent-to-frac": H_CONV_TERM,
  "dec-to-percent": H_CONV_TERM,
  "percent-to-dec": H_CONV_TERM,
  "mixed-to-improper": H_MIXED_FORMS,
  "improper-to-mixed": H_MIXED_FORMS,
  "compare-rationals": [
    "Values from friendly denominators.",
    "More denominators in the mix.",
    "Hardest values (16ths, 50ths, 100ths).",
  ],
  "order-rationals": [
    "Order 3 friendly values.",
    "Order 4 values.",
    "Order 4 values from the hardest set.",
  ],
  "equivalent-forms": H_CONV_TERM,
  // ----- Equations -----
  "eq-one-add": H_EQ_ONE,
  "eq-one-sub": H_EQ_ONE,
  "eq-one-mul": [
    "Positive whole coefficients.",
    "Negatives mixed in.",
    "Adds decimal and fraction coefficients.",
  ],
  "eq-one-div": [
    "Positive whole numbers.",
    "Negatives mixed in.",
    "Adds fraction answers (x/a = n/d).",
  ],
  "eq-one-mixed": H_EQ_ONE,
  "eq-two-pos": [
    "Small positive numbers.",
    "Larger positive numbers.",
    "Adds decimal coefficients (still all positive).",
  ],
  "eq-two-neg": [
    "Signed numbers, small.",
    "Signed numbers, larger.",
    "Adds decimal coefficients.",
  ],
  "eq-two-rational": [
    "Unit fractions (1/2x + 3 = 7), all positive.",
    "Any fraction coefficient; signs mixed.",
    "Fractions AND decimals; signs mixed.",
  ],
  "eq-two-dist": [
    "Positive p(x + q) = r.",
    "Negatives mixed in.",
    "Adds fraction multipliers like 1/2(x + 4).",
  ],
  "eq-multi-combine": [
    "Small positives; two like terms.",
    "Negatives mixed in.",
    "Adds decimal like terms (0.7x + 2.3x).",
  ],
  "eq-multi-dist": [
    "Small positive numbers.",
    "Negatives mixed in.",
    "Adds fraction distribution (1/3(x + 6)).",
  ],
  "eq-multi-both": [
    "Small positive numbers.",
    "Negatives mixed in.",
    "Adds decimal coefficients on both sides.",
  ],
  "eq-multi-full": H_EQ_MULTI,
  "eq-multi-special": [
    "Combine like terms first.",
    "Distribute one side first.",
    "Distribute BOTH sides first.",
  ],
  "eq-literal": [
    "One-step formulas (A = lw).",
    "Two-step formulas (y = mx + b).",
    "Multi-step formulas (F = 9/5C + 32).",
  ],
  "eq-prop": [
    "x in a numerator; whole answers.",
    "x anywhere; whole answers.",
    "Answers can be fractions.",
  ],
  "eq-prop-word": [
    "Small whole numbers.",
    "Bigger scale factors.",
    "Decimal money and measurements.",
  ],
  "eq-abs-simple": [
    "Small positive values.",
    "Negatives inside; values to 15.",
    "Values to 24.",
  ],
  "eq-abs-coef": [
    "Small values.",
    "Values to 15; fraction answers appear.",
    "Values to 24; fraction answers common.",
  ],
  "eq-abs-isolate": [
    "Small values after isolating.",
    "Larger values.",
    "Largest values.",
  ],
  "eq-sys-sub": [
    "Small numbers; y already isolated.",
    "Larger signed numbers.",
    "Largest signed numbers.",
  ],
  "eq-sys-elim": [
    "y-terms already cancel — just add.",
    "Multiply ONE equation first.",
    "Usually multiply BOTH equations.",
  ],
  "eq-sys-special": [
    "Second equation is a ×2 disguise.",
    "×2–3 disguises with signed numbers.",
    "Negative multipliers in the disguise.",
  ],
  "eq-sys-word": [
    "Small counts and prices.",
    "Larger counts.",
    "Largest numbers.",
  ],
  "eq-quad-sqrt": [
    "Perfect squares to 81.",
    "Perfect squares to 169.",
    "Adds non-perfect squares (x = ±3√2).",
  ],
  "eq-quad-trans": [
    "Small shifts; squares to 64.",
    "Larger shifts and squares.",
    "Largest values.",
  ],
  "eq-quad-fac-a1": [
    "Positive roots to 9.",
    "Signed roots to 12.",
    "Signed roots to 18.",
  ],
  "eq-quad-fac-an": [
    "a = 2–3; small positive roots.",
    "a = 2–3; signed roots.",
    "a = 2–3; larger signed roots.",
  ],
  "eq-quad-diff": [
    "Small perfect squares.",
    "Mid-size squares.",
    "Largest squares; fraction answers.",
  ],
  "eq-quad-formula": [
    "a to 2; small b and c.",
    "a to 3; larger b and c.",
    "Largest coefficients.",
  ],
  "eq-quad-complete": [
    "Small even b; squares to 36.",
    "Squares to 64.",
    "Squares to 121.",
  ],
  "eq-rad-single": [
    "Small radicands and results.",
    "Larger values; negatives mixed in.",
    "Largest values.",
  ],
  "eq-rad-double": H_EQ_MULTI,
  "eq-rad-linear": [
    "Small solutions — check for extraneous roots.",
    "Larger solutions.",
    "Largest solutions.",
  ],
  "eq-rat-simple": [
    "Small positive values.",
    "Negatives mixed in.",
    "Largest values.",
  ],
  "eq-rat-linear": H_EQ_MULTI,
  "eq-rat-lcd": [
    "Denominators to 6.",
    "Denominators to 10.",
    "Denominators to 12.",
  ],
  "eq-exp-bases": [
    "Exponents to 5.",
    "Exponents to 7.",
    "Exponents to 9.",
  ],
  // ----- Inequalities -----
  "ineq-one-add": [
    "All positive; small numbers.",
    "Negatives mixed in.",
    "Adds decimal values.",
  ],
  "ineq-one-sub": [
    "All positive; small numbers.",
    "Negatives mixed in.",
    "Adds decimal values.",
  ],
  "ineq-one-mul": [
    "Positive coefficients — no flip yet.",
    "Negative coefficients — flips appear.",
    "Decimal/fraction coefficients with flips.",
  ],
  "ineq-one-div": [
    "Positive divisors — no flip yet.",
    "Negative divisors — flips appear.",
    "Adds fraction boundaries.",
  ],
  "ineq-one-mixed": [
    "All positive; no flips.",
    "Negatives and flips appear.",
    "Decimals, fractions, and flips.",
  ],
  "ineq-two-pos": [
    "Small positives (no flip).",
    "Larger positives.",
    "Adds decimal coefficients.",
  ],
  "ineq-two-neg": [
    "Flip required; small numbers.",
    "Flip; larger numbers.",
    "Flip; decimal coefficients.",
  ],
  "ineq-two-rational": [
    "Unit fractions, all positive.",
    "Any fraction coefficient; flips appear.",
    "Fractions AND decimals; flips.",
  ],
  "ineq-two-dist": [
    "Positive multipliers.",
    "Negative multipliers — flips.",
    "Fraction multipliers like 1/2(x + 4).",
  ],
  "ineq-multi-combine": H_EQ_MULTI,
  "ineq-multi-dist": H_EQ_MULTI,
  "ineq-multi-both": H_EQ_MULTI,
  "ineq-multi-full": H_EQ_MULTI,
  "ineq-multi-special": [
    "Combine like terms first.",
    "Distribute first.",
    "Distribute with negative multipliers.",
  ],
  "ineq-compound-and": [
    "Narrow windows, small numbers.",
    "Wider windows; negatives mixed in.",
    "Widest windows.",
  ],
  "ineq-compound-or": [
    "Close boundaries, small numbers.",
    "Wider gaps; negatives mixed in.",
    "Widest gaps.",
  ],
  "ineq-compound-translate": [
    "Positive boundaries.",
    "Negatives mixed in.",
    "Negatives mixed in.",
  ],
  "ineq-abs-less": [
    "Small boundaries.",
    "Boundaries to 14; negatives inside.",
    "Boundaries to 20.",
  ],
  "ineq-abs-greater": [
    "Small boundaries.",
    "Boundaries to 14; negatives inside.",
    "Boundaries to 20.",
  ],
  "ineq-abs-isolate": [
    "Small values after isolating.",
    "Larger values.",
    "Largest values.",
  ],
  // ----- Geometry: 2-D -----
  "geo-rect-area": ["Sides to 12.", "Sides to 20.", "Sides to 30."],
  "geo-rect-perim": ["Sides to 12.", "Sides to 20.", "Sides to 30."],
  "geo-square": ["Sides to 12.", "Sides to 20.", "Sides to 30."],
  "geo-tri-area": ["Dimensions to 12.", "Dimensions to 20.", "Dimensions to 28."],
  "geo-parallelogram-area": ["Dimensions to 12.", "Dimensions to 20.", "Dimensions to 28."],
  "geo-trap-area": ["Dimensions to 12.", "Dimensions to 18.", "Dimensions to 26."],
  "geo-circle-area": [
    "Radius to 8.",
    "Radius to 12.",
    "Radius to 15 — sometimes only the diameter is given.",
  ],
  "geo-circle-circumference": [
    "Radius/diameter to 8.",
    "To 11.",
    "To 14.",
  ],
  "geo-rect-find-area": ["Sides to 12.", "Sides to 18.", "Sides to 26."],
  "geo-rect-find-perim": ["Sides to 12.", "Sides to 18.", "Sides to 26."],
  "geo-square-find": ["Sides to 10.", "Sides to 14.", "Sides to 18."],
  "geo-tri-find-base": ["Dimensions to 12.", "To 18.", "To 24."],
  "geo-tri-find-height": ["Dimensions to 12.", "To 18.", "To 24."],
  "geo-circle-find-r-area": ["Radius to 8.", "To 10.", "To 13."],
  "geo-circle-find-r-circ": ["Radius to 8.", "To 10.", "To 13."],
  // ----- Geometry: 3-D -----
  "geo-rect-prism-v": ["Dimensions to 10.", "To 14.", "To 18."],
  "geo-rect-prism-sa": ["Dimensions to 10.", "To 14.", "To 18."],
  "geo-cube": ["Sides to 10.", "To 12.", "To 16."],
  "geo-tri-prism-v": ["Dimensions to 10.", "To 14.", "To 18."],
  "geo-tri-prism-sa": [
    "3-4-5-style bases; lengths to 10.",
    "Lengths to 14.",
    "Lengths to 18.",
  ],
  "geo-cylinder-v": ["r and h to 8.", "To 10.", "To 13."],
  "geo-cylinder-sa": ["r and h to 8.", "To 10.", "To 13."],
  "geo-cone-v": ["r and h to 6.", "To 8.", "To 11."],
  "geo-sphere-v": ["Radius 3 or 6.", "Adds 9.", "Adds 12."],
  "geo-pyramid-v": ["Dimensions to 8.", "To 10.", "To 13."],
  "geo-rect-prism-find-h": ["Dimensions to 10.", "To 14.", "To 18."],
  "geo-cube-find-s": ["Sides to 8.", "To 10.", "To 13."],
  "geo-cylinder-find-h": ["Values to 7.", "To 9.", "To 11."],
  "geo-cylinder-find-r": ["Values to 6.", "To 7.", "To 9."],
  "geo-cone-find-h": ["Values to 5.", "To 6.", "To 8."],
  "geo-sphere-find-r": ["Radius 3 or 6.", "Adds 9.", "Adds 12."],
  // ----- Geometry: Pythagorean + coordinate -----
  "geo-pyth-hyp": [
    "3-4-5 family triples.",
    "Adds the 5-12-13 family.",
    "All triples (8-15-17, 7-24-25, 20-21-29).",
  ],
  "geo-pyth-leg": [
    "3-4-5 family triples.",
    "Adds the 5-12-13 family.",
    "All triples.",
  ],
  "geo-pyth-check": [
    "3-4-5 family triples.",
    "Adds the 5-12-13 family.",
    "All triples.",
  ],
  "geo-pyth-word": [
    "3-4-5 family; hypotenuse AND missing-leg problems.",
    "Adds 5-12-13; both problem types.",
    "All triples; both problem types.",
  ],
  "geo-coord-distance": [
    "Small triples near the origin.",
    "Adds 5-12-13 distances.",
    "All triples; points spread farther out.",
  ],
  "geo-coord-midpoint": [
    "Coordinates to ±6.",
    "To ±10.",
    "To ±14.",
  ],
  "geo-coord-slope": [
    "Whole-number slopes.",
    "Simple fraction slopes.",
    "Any fraction slope.",
  ],
  // ----- Graphing & Rates -----
  "gr-unit-rate": [
    "Whole rates to 12.",
    "Whole rates to 20.",
    "Adds decimal money rates ($2.75/lb).",
  ],
  "gr-rate-table": [
    "Rates to 6.",
    "Rates to 8.",
    "Rates to 11.",
  ],
  "gr-rate-convert": [
    "One friendly factor (per-minute → per-hour).",
    "Metric conversions (m/s → km/h).",
    "Cross-system (mph ↔ ft/sec).",
  ],
  "gr-prop-k-table": [
    "x = 1 row shows k directly.",
    "No x = 1 row — divide y by x.",
    "Adds fractional k (k = 3/2).",
  ],
  "gr-prop-k-graph": [
    "Whole k; labeled point to divide.",
    "Whole k; labeled point to divide.",
    "Adds fractional k from points like (6, 9).",
  ],
  "gr-prop-equation": [
    "x = 1 row shows k directly.",
    "No x = 1 row — divide y by x.",
    "Adds fractional k (y = 3/2x).",
  ],
  "gr-prop-table-yn": [
    "Obvious breaks in the ratio.",
    "Bigger x-values to check.",
    "Near-misses — only ONE row breaks the ratio.",
  ],
  "gr-prop-graph-yn": [
    "Straight lines only.",
    "Adds curves through the origin.",
    "Adds curves through the origin.",
  ],
  "gr-slope-points": [
    "Whole-number slopes.",
    "Simple fraction slopes.",
    "Any fraction slope.",
  ],
  "gr-slope-graph": [
    "Whole-number slopes.",
    "Runs of 1–2.",
    "Fraction slopes (rise over 2–3).",
  ],
  "gr-slope-table": [
    "x steps by 1; slopes to ±4.",
    "x steps by 1; slopes to ±7.",
    "x steps by 2–3 — compute Δy/Δx.",
  ],
  "gr-slope-verbal": [
    "Small rises and runs.",
    "Larger values.",
    "Largest values.",
  ],
  "gr-slope-classify": [
    "Classify drawn lines (all four types).",
    "Classify drawn lines (all four types).",
    "Classify drawn lines (all four types).",
  ],
  "gr-si-identify": [
    "Whole m and b, positive.",
    "Negatives mixed in.",
    "Adds fractional slopes.",
  ],
  "gr-si-mb": [
    "Positive whole slopes.",
    "Signed whole slopes.",
    "Mostly fractional slopes.",
  ],
  "gr-si-mp": [
    "Whole slopes, small points.",
    "Negatives mixed in.",
    "Adds fractional slopes.",
  ],
  "gr-si-pp": [
    "Whole slopes (points 1 apart).",
    "Negatives mixed in.",
    "Adds fractional slopes (points farther apart).",
  ],
  "gr-si-graph": [
    "Whole slopes to ±3.",
    "Whole slopes to ±4.",
    "Adds slope ±1/2 lines.",
  ],
  "gr-std-to-si": [
    "Small positive coefficients.",
    "Negatives mixed in.",
    "Largest coefficients; fraction slopes.",
  ],
  "gr-si-to-std": [
    "Small positive m and b.",
    "Negatives mixed in.",
    "Largest values.",
  ],
  "gr-ps-write": [
    "Small positive slopes and points.",
    "Negatives mixed in.",
    "Largest values.",
  ],
  "gr-ps-to-si": [
    "Small positive values.",
    "Negatives mixed in.",
    "Largest values.",
  ],
  "gr-graph-si": [
    "Whole slopes to ±3.",
    "Whole slopes to ±4.",
    "Adds slope ±1/2 lines.",
  ],
  "gr-graph-table": [
    "Whole slopes and intercepts.",
    "Whole slopes and intercepts.",
    "Whole slopes and intercepts.",
  ],
  "gr-graph-std": [
    "Positive intercepts.",
    "Signed intercepts.",
    "Larger coefficients and intercepts.",
  ],
  "gr-graph-points": [
    "Points within ±4.",
    "Points within ±6.",
    "Points within ±8.",
  ],
  "gr-fn-vlt-graph": [
    "Lines, parabolas, circles.",
    "Adds absolute value and ellipses.",
    "Adds exponentials, cubics, and square roots.",
  ],
  "gr-fn-table": [
    "Small whole values.",
    "Small whole values.",
    "Small whole values.",
  ],
  "gr-fn-eval": [
    "Positive m, b, and inputs.",
    "Negatives mixed in.",
    "Largest values.",
  ],
  "gr-fn-reverse": [
    "Positive values.",
    "Negatives mixed in.",
    "Largest values.",
  ],
  "gr-fn-domain-range": [
    "Whole-number endpoints.",
    "Whole-number endpoints.",
    "Whole-number endpoints.",
  ],
  "gr-nonlinear-classify": [
    "Linear vs. quadratic tables.",
    "Adds exponential and cubic tables.",
    "Adds exponential and cubic tables.",
  ],
  "gr-rate-compare": [
    "Rates clearly apart.",
    "Rates close together.",
    "Half-dollar rates 50¢ apart.",
  ],
  "gr-linear-compare": [
    "Small positive slopes/intercepts.",
    "Negatives mixed in.",
    "Largest values.",
  ],
};

/** The slider hint for a topic at a difficulty — always accurate to the
 *  generator because DIFFICULTY_HINTS covers every topic explicitly. */
export function difficultyHint(topic: FluencyTopic, d: Difficulty): string {
  const h = DIFFICULTY_HINTS[topic];
  return d === "easy" ? h[0] : d === "medium" ? h[1] : h[2];
}

/** A sub-group of topics shown under its own small heading inside a
 *  category. Used to break long lists (Equations, Converting) into clear
 *  skill tiers. */
export interface TopicTier {
  label: string;
  topics: FluencyTopic[];
  /** Marks a tier as a roadmap entry — appears in the picker but its
   *  topics are disabled. */
  comingSoon?: boolean;
}

/** Topic groups for the landing-page picker. Order here is the order shown
 *  on the picker. Use `topics` for flat lists or `tiers` for grouped
 *  (Equations is grouped by skill tier). */
export const TOPIC_CATEGORIES: ReadonlyArray<{
  label: string;
  blurb: string;
  color: string;
  /** Flat list of topics. Mutually exclusive with `tiers`. */
  topics?: FluencyTopic[];
  /** Grouped list of topics organized into named tiers. */
  tiers?: TopicTier[];
  /** Whole-category roadmap entry — no clickable cards inside. */
  comingSoon?: boolean;
}> = [
  {
    // Top of the picker per Dave's request — integer fluency is the
    // grade-7 entry point and we want it discoverable in one glance.
    // Using the design-system accent teal-600 for the tile colour so
    // it lines up with other primary actions across the app.
    label: "Integers",
    blurb: "Signed-integer drill across +, −, ×, ÷. Single-digit through two-digit.",
    color: "#0d9488",
    topics: [
      "add-integers",
      "subtract-integers",
      "multiply-integers",
      "divide-integers",
      "integer-mixed",
    ],
  },
  {
    // Sits immediately after Integers to make the integers → rationals
    // progression visible in the picker. Same accent teal so signed
    // number topics cluster visually.
    label: "Rational Numbers",
    blurb: "Signed fractions and mixed numbers across +, −, ×, ÷. Negatives baked in.",
    color: "#0d9488",
    topics: [
      "add-rationals",
      "subtract-rationals",
      "multiply-rationals",
      "divide-rationals",
      "rational-mixed",
    ],
  },
  {
    // Indiana-specific number theory work (7.NS.5 / 7.NS.6). Separated
    // from arithmetic categories because these are single-operand drills
    // (factor THIS number, root of THIS square).
    label: "Number Theory",
    blurb: "Prime factorisation and perfect-square roots. Indiana 7.NS.5 / 7.NS.6.",
    color: "#475569",
    topics: ["prime-factorization", "perfect-square-roots"],
  },
  {
    // Percent applications group. Distinct from "Converting" (which is
    // form-translation drill) — this category exercises percent
    // arithmetic on money: tax, tip, markup, discount, simple interest,
    // and percent-of-change.
    label: "Percent",
    blurb: "Percent of change plus money applications: tax, tip, markup, discount, simple interest.",
    color: "#f97316",
    topics: ["percent-of-change", "percent-application", "simple-interest"],
  },
  {
    // Algebraic expression drill. Currently a single topic — slot for
    // add / subtract / factor linear expressions later when those
    // generators are authored.
    label: "Algebraic Expressions",
    blurb: "Combine like terms, distribute, and expand. Coefficients with mixed signs.",
    color: "#dc2626",
    topics: [
      "combine-like-terms",
      "distribute-expand",
      "distribute-combine",
    ],
  },
  {
    label: "Fractions",
    blurb: "Add, subtract, multiply, divide. Proper, improper, mixed, whole.",
    color: "#2dd4bf",
    topics: [
      "add-fractions",
      "subtract-fractions",
      "multiply-fractions",
      "divide-fractions",
    ],
  },
  {
    label: "Decimals",
    blurb: "All four operations with up to 3-place decimals.",
    color: "#3f42d9",
    topics: [
      "add-decimals",
      "subtract-decimals",
      "multiply-decimals",
      "divide-decimals",
    ],
  },
  {
    label: "Converting",
    blurb: "Move between fraction, decimal, and percent forms.",
    color: "#f97316",
    tiers: [
      {
        label: "Fraction ↔ Decimal",
        topics: ["frac-to-dec-term", "frac-to-dec-rep", "dec-to-frac-term", "dec-to-frac-rep"],
      },
      {
        label: "Fraction ↔ Percent",
        topics: ["frac-to-percent", "percent-to-frac"],
      },
      {
        label: "Decimal ↔ Percent",
        topics: ["dec-to-percent", "percent-to-dec"],
      },
      {
        label: "Within Fractions",
        topics: ["mixed-to-improper", "improper-to-mixed"],
      },
      {
        label: "Compare / Order",
        topics: ["compare-rationals", "order-rationals", "equivalent-forms"],
      },
    ],
  },
  {
    label: "Equations",
    blurb: "Incremental progression from one-step through Algebra 1.",
    color: "#dc2626",
    tiers: [
      {
        label: "Tier 1 — One-Step (grade 6)",
        topics: ["eq-one-add", "eq-one-sub", "eq-one-mul", "eq-one-div", "eq-one-mixed"],
      },
      {
        label: "Tier 2 — Two-Step (grade 7)",
        topics: ["eq-two-pos", "eq-two-neg", "eq-two-rational", "eq-two-dist"],
      },
      {
        label: "Tier 3 — Multi-Step (grade 8)",
        topics: [
          "eq-multi-combine",
          "eq-multi-dist",
          "eq-multi-both",
          "eq-multi-full",
          "eq-multi-special",
        ],
      },
      {
        label: "Tier 4 — Literal Equations",
        topics: ["eq-literal"],
      },
      {
        label: "Tier 5 — Proportions (Algebra 1)",
        topics: ["eq-prop", "eq-prop-word"],
      },
      {
        label: "Tier 6 — Absolute Value (Algebra 1)",
        topics: ["eq-abs-simple", "eq-abs-coef", "eq-abs-isolate"],
      },
      {
        label: "Tier 7 — Systems of Equations (Alg 1)",
        topics: ["eq-sys-sub", "eq-sys-elim", "eq-sys-special", "eq-sys-word"],
      },
      {
        label: "Tier 8 — Quadratic Equations (Alg 1)",
        topics: [
          "eq-quad-sqrt", "eq-quad-trans", "eq-quad-fac-a1", "eq-quad-fac-an",
          "eq-quad-diff", "eq-quad-formula", "eq-quad-complete",
        ],
      },
      {
        label: "Tier 9 — Radical Equations (Alg 1)",
        topics: ["eq-rad-single", "eq-rad-double", "eq-rad-linear"],
      },
      {
        label: "Tier 10 — Rational Equations (Alg 1)",
        topics: ["eq-rat-simple", "eq-rat-linear", "eq-rat-lcd"],
      },
      {
        label: "Tier 11 — Exponential (Alg 1 intro)",
        topics: ["eq-exp-bases"],
      },
    ],
  },
  {
    label: "Inequalities",
    blurb: "Incremental progression from one-step through Algebra 1.",
    color: "#7c3aed",
    tiers: [
      {
        label: "Tier 1 — One-Step (grade 6)",
        topics: ["ineq-one-add", "ineq-one-sub", "ineq-one-mul", "ineq-one-div", "ineq-one-mixed"],
      },
      {
        label: "Tier 2 — Two-Step (grade 7)",
        topics: ["ineq-two-pos", "ineq-two-neg", "ineq-two-rational", "ineq-two-dist"],
      },
      {
        label: "Tier 3 — Multi-Step (grade 8)",
        topics: [
          "ineq-multi-combine",
          "ineq-multi-dist",
          "ineq-multi-both",
          "ineq-multi-full",
          "ineq-multi-special",
        ],
      },
      {
        label: "Tier 4 — Compound (Algebra 1)",
        topics: ["ineq-compound-and", "ineq-compound-or", "ineq-compound-translate"],
      },
      {
        label: "Tier 5 — Absolute Value (Algebra 1)",
        topics: ["ineq-abs-less", "ineq-abs-greater", "ineq-abs-isolate"],
      },
      {
        label: "Tier 6 — Systems & Graphing (Alg 1)",
        topics: [],
        comingSoon: true,
      },
    ],
  },
  {
    label: "Geometry",
    blurb: "Pick a shape — each one has forward and reverse problems.",
    color: "#16a34a",
    tiers: [
      // ----- 2-D Shapes -----
      {
        label: "Rectangle",
        topics: ["geo-rect-area", "geo-rect-perim", "geo-rect-find-area", "geo-rect-find-perim"],
      },
      {
        label: "Square",
        topics: ["geo-square", "geo-square-find"],
      },
      {
        label: "Triangle",
        topics: ["geo-tri-area", "geo-tri-find-base", "geo-tri-find-height"],
      },
      {
        label: "Parallelogram",
        topics: ["geo-parallelogram-area"],
      },
      {
        label: "Trapezoid",
        topics: ["geo-trap-area"],
      },
      {
        label: "Circle",
        topics: ["geo-circle-area", "geo-circle-circumference", "geo-circle-find-r-area", "geo-circle-find-r-circ"],
      },
      // ----- 3-D Shapes -----
      {
        label: "Rectangular Prism",
        topics: ["geo-rect-prism-v", "geo-rect-prism-sa", "geo-rect-prism-find-h"],
      },
      {
        label: "Cube",
        topics: ["geo-cube", "geo-cube-find-s"],
      },
      {
        label: "Triangular Prism",
        topics: ["geo-tri-prism-v", "geo-tri-prism-sa"],
      },
      {
        label: "Cylinder",
        topics: ["geo-cylinder-v", "geo-cylinder-sa", "geo-cylinder-find-h", "geo-cylinder-find-r"],
      },
      {
        label: "Cone",
        topics: ["geo-cone-v", "geo-cone-find-h"],
      },
      {
        label: "Sphere",
        topics: ["geo-sphere-v", "geo-sphere-find-r"],
      },
      {
        label: "Square Pyramid",
        topics: ["geo-pyramid-v"],
      },
      // ----- Right Triangle (Pythagorean) & Coordinate Plane -----
      {
        label: "Right Triangle (Pythagorean)",
        topics: ["geo-pyth-hyp", "geo-pyth-leg", "geo-pyth-check", "geo-pyth-word"],
      },
      {
        label: "Coordinate Plane",
        // Slope lives in the Graphing & Rates category, not here.
        topics: ["geo-coord-distance", "geo-coord-midpoint"],
      },
    ],
  },
  {
    label: "Graphing & Rates",
    blurb: "Unit rates, proportions, slope, lines, and functions on the coordinate plane.",
    color: "#0ea5e9",
    tiers: [
      {
        label: "Tier 1 — Rates & Unit Rates (grade 6)",
        topics: ["gr-unit-rate", "gr-rate-table", "gr-rate-convert"],
      },
      {
        label: "Tier 2 — Proportional Relationships (grade 7)",
        topics: [
          "gr-prop-k-table",
          "gr-prop-k-graph",
          "gr-prop-equation",
          "gr-prop-table-yn",
          "gr-prop-graph-yn",
        ],
      },
      {
        label: "Tier 3 — Slope from Two Points (grade 8)",
        topics: [
          "gr-slope-points",
          "gr-slope-graph",
          "gr-slope-table",
          "gr-slope-verbal",
          "gr-slope-classify",
        ],
      },
      {
        label: "Tier 4 — Slope-Intercept Form (grade 8)",
        topics: [
          "gr-si-identify",
          "gr-si-mb",
          "gr-si-mp",
          "gr-si-pp",
          "gr-si-graph",
        ],
      },
      {
        label: "Tier 5 — Point-Slope & Standard Forms (Algebra 1)",
        topics: ["gr-std-to-si", "gr-si-to-std", "gr-ps-write", "gr-ps-to-si"],
      },
      {
        label: "Tier 6 — Graphing Lines (Algebra 1)",
        topics: ["gr-graph-si", "gr-graph-table", "gr-graph-std", "gr-graph-points"],
      },
      {
        label: "Tier 9 — Functions on the Coordinate Plane (Algebra 1)",
        topics: [
          "gr-fn-vlt-graph",
          "gr-fn-table",
          "gr-fn-eval",
          "gr-fn-reverse",
          "gr-fn-domain-range",
        ],
      },
      {
        label: "Tier 10 — Non-Linear & Comparison (Algebra 1)",
        topics: ["gr-nonlinear-classify", "gr-rate-compare", "gr-linear-compare"],
      },
    ],
  },
];
