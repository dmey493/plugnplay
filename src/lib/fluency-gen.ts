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
    | "grid";
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
  let num = rnd(1, den - 1);
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
  const a = rndCoef(opts, false);
  const x = rndSolution(opts, opts.allowNegatives);
  const b = x + a;
  return { num: idx, display: `x + ${a} = ${b}`, answer: `x = ${x}` };
}

function makeOneStepSub(opts: FluencyOptions, idx: number): Problem {
  const a = rndCoef(opts, false);
  const x = rndSolution(opts, opts.allowNegatives);
  const b = x - a;
  return { num: idx, display: `x − ${a} = ${b}`, answer: `x = ${x}` };
}

function makeOneStepMul(opts: FluencyOptions, idx: number): Problem {
  const a = rndCoef(opts, opts.allowNegatives);
  const x = rndSolution(opts, opts.allowNegatives);
  const b = a * x;
  return { num: idx, display: `${fmtCoefTerm(a)} = ${b}`, answer: `x = ${x}` };
}

function makeOneStepDiv(opts: FluencyOptions, idx: number): Problem {
  const a = rndCoef(opts, opts.allowNegatives);
  // Solution can be anything; we still display as x/a = b. Solution = a*b.
  const b = rndConst(opts, opts.allowNegatives);
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
  const a = Math.abs(rndCoef(opts, false));
  const b = Math.abs(rndConst(opts, false));
  const x = Math.abs(rndSolution(opts, false));
  const c = a * x + b;
  return { num: idx, display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${c}`, answer: `x = ${x}` };
}

function makeTwoStepNeg(opts: FluencyOptions, idx: number): Problem {
  // Same shape but with allowNegatives forced on so negatives appear.
  const a = rndCoef(opts, true);
  const b = rndConst(opts, true);
  const x = rndSolution(opts, true);
  const c = a * x + b;
  return { num: idx, display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${c}`, answer: `x = ${x}` };
}

function makeTwoStepRational(opts: FluencyOptions, idx: number): Problem {
  // Coefficient is a unit fraction 1/d; constant + result remain integers.
  const d = [2, 3, 4, 5, 6][rnd(0, 4)];
  const b = rndConst(opts, opts.allowNegatives);
  const x = rndSolution(opts, opts.allowNegatives) * d; // ensure (1/d)x is whole
  const c = x / d + b;
  return {
    num: idx,
    display: `1/${d} · x ${fmtAddConst(b)} = ${c}`,
    answer: `x = ${x}`,
  };
}

function makeTwoStepDist(opts: FluencyOptions, idx: number): Problem {
  // p(x + q) = r — pick x, p, q; compute r.
  const p = rndCoef(opts, opts.allowNegatives);
  const q = rndConst(opts, opts.allowNegatives);
  const x = rndSolution(opts, opts.allowNegatives);
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
  // ax + bx + c = d → (a+b)x + c = d → x = (d−c)/(a+b)
  const a = rndCoef(opts, opts.allowNegatives);
  let b = rndCoef(opts, opts.allowNegatives);
  // Avoid a + b = 0 (would erase the variable).
  if (a + b === 0) b += 1;
  const c = rndConst(opts, opts.allowNegatives);
  const x = rndSolution(opts, opts.allowNegatives);
  const d = (a + b) * x + c;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddCoef(b)} ${fmtAddConst(c)} = ${d}`,
    answer: `x = ${x}`,
  };
}

function makeMultiDist(opts: FluencyOptions, idx: number): Problem {
  // p(x + q) + r = s
  const p = rndCoef(opts, opts.allowNegatives);
  const q = rndConst(opts, opts.allowNegatives);
  const r = rndConst(opts, opts.allowNegatives);
  const x = rndSolution(opts, opts.allowNegatives);
  const s = p * (x + q) + r;
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)} = ${s}`,
    answer: `x = ${x}`,
  };
}

function makeMultiBoth(opts: FluencyOptions, idx: number): Problem {
  // ax + b = cx + d → (a−c)x = d − b
  const a = rndCoef(opts, opts.allowNegatives);
  let c = rndCoef(opts, opts.allowNegatives);
  if (a === c) c += 1; // ensure (a-c) != 0
  const x = rndSolution(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
  const d = (a - c) * x + b;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${fmtCoefTerm(c)} ${fmtAddConst(d)}`,
    answer: `x = ${x}`,
  };
}

function makeMultiFull(opts: FluencyOptions, idx: number): Problem {
  // p(x + q) + r = sx + t
  const p = rndCoef(opts, opts.allowNegatives);
  const q = rndConst(opts, opts.allowNegatives);
  const r = rndConst(opts, opts.allowNegatives);
  let s = rndCoef(opts, opts.allowNegatives);
  if (p === s) s += 1;
  const x = rndSolution(opts, opts.allowNegatives);
  const t = p * (x + q) + r - s * x;
  const qStr = q < 0 ? `− ${Math.abs(q)}` : `+ ${q}`;
  return {
    num: idx,
    display: `${p < 0 ? `−${Math.abs(p)}` : p}(x ${qStr}) ${fmtAddConst(r)} = ${fmtCoefTerm(s)} ${fmtAddConst(t)}`,
    answer: `x = ${x}`,
  };
}

function makeMultiSpecial(opts: FluencyOptions, idx: number): Problem {
  // Two flavors: no solution OR infinite solutions.
  const noSol = randomBool();
  const a = rndCoef(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
  if (noSol) {
    // ax + b = ax + (b + k), k != 0 → no solution
    const k = rndCoef(opts, opts.allowNegatives) || 1;
    return {
      num: idx,
      display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${fmtCoefTerm(a)} ${fmtAddConst(b + k)}`,
      answer: "no solution",
    };
  }
  // Infinite: ax + b = ax + b (or distributed equivalent)
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} = ${fmtCoefTerm(a)} ${fmtAddConst(b)}`,
    answer: "all real numbers",
  };
}

// ----- Tier 4: Literal -----

const LITERAL_FORMULAS: { display: string; answer: string }[] = [
  { display: "Solve for w:  A = lw", answer: "w = A/l" },
  { display: "Solve for h:  A = (1/2)bh", answer: "h = 2A/b" },
  { display: "Solve for r:  C = 2πr", answer: "r = C/(2π)" },
  { display: "Solve for t:  d = rt", answer: "t = d/r" },
  { display: "Solve for r:  d = rt", answer: "r = d/t" },
  { display: "Solve for x:  y = mx + b", answer: "x = (y − b)/m" },
  { display: "Solve for m:  y = mx + b", answer: "m = (y − b)/x" },
  { display: "Solve for l:  P = 2l + 2w", answer: "l = (P − 2w)/2" },
  { display: "Solve for h:  V = lwh", answer: "h = V/(lw)" },
  { display: "Solve for C:  F = (9/5)C + 32", answer: "C = (5/9)(F − 32)" },
  { display: "Solve for b:  A = (1/2)h(b + c)", answer: "b = (2A/h) − c" },
  { display: "Solve for a:  P = a + b + c", answer: "a = P − b − c" },
];

function makeLiteral(_opts: FluencyOptions, idx: number): Problem {
  const pick = LITERAL_FORMULAS[rnd(0, LITERAL_FORMULAS.length - 1)];
  return { num: idx, display: pick.display, answer: pick.answer };
}

// ----- Tier 5: Proportions -----

function makeProportion(opts: FluencyOptions, idx: number): Problem {
  // Build a true proportion a/b = c/d (i.e., a·d = b·c), then hide one of
  // the four terms behind x. Coefficients scale with difficulty.
  const max = opts.difficulty === "easy" ? 8 : opts.difficulty === "medium" ? 12 : 18;
  const a = rnd(2, max);
  const b = rnd(2, max);
  const k = rnd(2, 6);
  const c = a * k;
  const d = b * k;
  const pos = rnd(0, 3);
  let display: string;
  let answer: string;
  if (pos === 0) {        display = `x/${b} = ${c}/${d}`; answer = `x = ${a}`; }
  else if (pos === 1) {   display = `${a}/x = ${c}/${d}`; answer = `x = ${b}`; }
  else if (pos === 2) {   display = `${a}/${b} = x/${d}`; answer = `x = ${c}`; }
  else {                  display = `${a}/${b} = ${c}/x`; answer = `x = ${d}`; }
  return { num: idx, display, answer };
}

const PROPORTION_WORDS: ((opts: FluencyOptions) => { display: string; answer: string })[] = [
  (opts) => {
    const a = rnd(2, 5);
    const b = rnd(2, 6);
    const k = rnd(2, 6);
    return {
      display: `If ${a} apples cost $${b}, how much do ${a * k} apples cost?`,
      answer: `$${b * k}`,
    };
  },
  (opts) => {
    const cm = rnd(2, 5);
    const km = rnd(3, 8);
    const k = rnd(2, 6);
    return {
      display: `On a map, ${cm} cm represents ${km} km. How many km does ${cm * k} cm represent?`,
      answer: `${km * k} km`,
    };
  },
  (opts) => {
    const a = rnd(3, 7);
    const b = rnd(2, 5);
    const k = rnd(2, 5);
    return {
      display: `A recipe uses ${a} cups of flour per ${b} cups of sugar. How many cups of flour for ${b * k} cups of sugar?`,
      answer: `${a * k} cups`,
    };
  },
  (opts) => {
    const a = rnd(2, 4);
    const b = rnd(5, 9);
    const k = rnd(2, 4);
    return {
      display: `A car travels ${a * k * b} miles in ${a * k} hours. At the same rate, how many miles in ${a} hours?`,
      answer: `${a * b} miles`,
    };
  },
];

function makePropWord(opts: FluencyOptions, idx: number): Problem {
  const pick = PROPORTION_WORDS[rnd(0, PROPORTION_WORDS.length - 1)];
  const r = pick(opts);
  return { num: idx, display: r.display, answer: r.answer };
}

// ----- Tier 6: Absolute Value -----

function makeAbsSimple(opts: FluencyOptions, idx: number): Problem {
  const a = rndCoef(opts, opts.allowNegatives);
  const b = rnd(1, opts.difficulty === "easy" ? 9 : 15);
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
  const b = rndCoef(opts, opts.allowNegatives);
  const c = rnd(1, opts.difficulty === "easy" ? 9 : 15);
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
  const b = rndCoef(opts, opts.allowNegatives);
  const c = rnd(2, 5); // multiplier outside
  const d = rndConst(opts, opts.allowNegatives);
  const k = rnd(1, opts.difficulty === "easy" ? 4 : 8); // |…| equals k
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
  const x = rndSolution(opts, opts.allowNegatives);
  const y = rndSolution(opts, opts.allowNegatives);
  const a1 = rndCoef(opts, opts.allowNegatives);
  const b1 = rndCoef(opts, opts.allowNegatives);
  const c1 = a1 * x + b1 * y;
  // Second equation: keep it different. Often "y = …" form so substitution
  // is the natural route.
  const m = rndCoef(opts, opts.allowNegatives);
  const k = y - m * x;
  const eq2 = `y = ${fmtCoefTerm(m)} ${fmtAddConst(k)}`;
  return {
    num: idx,
    display: `${fmtCoefTerm(a1)} ${fmtAddCoef(b1, "y")} = ${c1}\n${eq2}`,
    answer: `(${x}, ${y})`,
  };
}

function makeSysElim(opts: FluencyOptions, idx: number): Problem {
  const x = rndSolution(opts, opts.allowNegatives);
  const y = rndSolution(opts, opts.allowNegatives);
  const a1 = rndCoef(opts, opts.allowNegatives);
  const b1 = rndCoef(opts, opts.allowNegatives);
  const c1 = a1 * x + b1 * y;
  const a2 = rndCoef(opts, opts.allowNegatives);
  let b2 = rndCoef(opts, opts.allowNegatives);
  if (a1 * b2 - a2 * b1 === 0) b2 += 1; // avoid parallel lines
  const c2 = a2 * x + b2 * y;
  return {
    num: idx,
    display: `${fmtCoefTerm(a1)} ${fmtAddCoef(b1, "y")} = ${c1}\n${fmtCoefTerm(a2)} ${fmtAddCoef(b2, "y")} = ${c2}`,
    answer: `(${x}, ${y})`,
  };
}

function makeSysSpecial(opts: FluencyOptions, idx: number): Problem {
  const noSol = randomBool();
  const a = rndCoef(opts, opts.allowNegatives);
  const b = rndCoef(opts, opts.allowNegatives);
  const c = rndConst(opts, opts.allowNegatives);
  if (noSol) {
    // Same LHS, different RHS → parallel lines, no solution
    return {
      num: idx,
      display: `${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c}\n${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c + 1 + rnd(1, 3)}`,
      answer: "no solution",
    };
  }
  // Same line written two ways → infinite solutions
  const k = rnd(2, 4);
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c}\n${fmtCoefTerm(a * k)} ${fmtAddCoef(b * k, "y")} = ${c * k}`,
    answer: "infinitely many solutions",
  };
}

const SYSTEM_WORDS: ((opts: FluencyOptions) => { display: string; answer: string })[] = [
  () => {
    const cost1 = rnd(2, 4);
    const cost2 = rnd(5, 8);
    const n1 = rnd(2, 6);
    const n2 = rnd(2, 6);
    return {
      display: `Tickets cost $${cost1} for students and $${cost2} for adults. ${n1 + n2} tickets sold for a total of $${cost1 * n1 + cost2 * n2}. How many of each were sold?`,
      answer: `${n1} student, ${n2} adult`,
    };
  },
  () => {
    const a = rnd(2, 5);
    const b = rnd(3, 7);
    const k = rnd(2, 5);
    const total = (a + b) * k;
    return {
      display: `The sum of two numbers is ${total} and one number is ${b - a < 0 ? Math.abs(b - a) : (b - a)} ${b > a ? "more" : "less"} than the other. Find the numbers.`,
      answer: `${a * k} and ${b * k}`,
    };
  },
];

function makeSysWord(opts: FluencyOptions, idx: number): Problem {
  const pick = SYSTEM_WORDS[rnd(0, SYSTEM_WORDS.length - 1)];
  const r = pick(opts);
  return { num: idx, display: r.display, answer: r.answer };
}

// ----- Tier 8: Quadratics -----
// We use Unicode ² for x² in display strings — renders cleanly in any sans
// or serif font without needing a sup tag.

function makeQuadSqrt(opts: FluencyOptions, idx: number): Problem {
  // x² = c → x = ±√c
  const r = rnd(2, opts.difficulty === "easy" ? 9 : 12);
  const c = r * r;
  return { num: idx, display: `x² = ${c}`, answer: `x = ±${r}` };
}

function makeQuadTrans(opts: FluencyOptions, idx: number): Problem {
  // (x − h)² = k where k is a perfect square
  const h = rndConst(opts, opts.allowNegatives);
  const r = rnd(1, opts.difficulty === "easy" ? 8 : 12);
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
  const r1 = rndSolution(opts, opts.allowNegatives);
  let r2 = rndSolution(opts, opts.allowNegatives);
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
  const p = rndSolution(opts, opts.allowNegatives);
  const q = rndSolution(opts, opts.allowNegatives);
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
  const a = rnd(2, opts.difficulty === "easy" ? 4 : 8);
  const b = rnd(2, opts.difficulty === "easy" ? 6 : 12);
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
  const b = rndCoef(opts, opts.allowNegatives);
  const c = rndConst(opts, opts.allowNegatives);
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
  let bHalf = rndCoef(opts, opts.allowNegatives);
  if (bHalf === 0) bHalf = 1;
  const b = 2 * bHalf;
  // Pick a target k such that (x + bHalf)² = k has integer answers.
  const r = rnd(1, opts.difficulty === "easy" ? 6 : 10);
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
  const c = rnd(2, opts.difficulty === "easy" ? 7 : 12);
  const x = rndSolution(opts, opts.allowNegatives);
  const b = c * c - a * x;
  return {
    num: idx,
    display: `√(${fmtCoefTerm(a)} ${fmtAddConst(b)}) = ${c}`,
    answer: `x = ${x}`,
  };
}

function makeRadDouble(opts: FluencyOptions, idx: number): Problem {
  // √(ax + b) = √(cx + d) → ax + b = cx + d → x = (d − b)/(a − c)
  const a = rndCoef(opts, opts.allowNegatives);
  let c = rndCoef(opts, opts.allowNegatives);
  if (c === a) c += 1;
  const x = rndSolution(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
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
  const x = rndSolution(opts, opts.allowNegatives);
  const a = b * x;
  return { num: idx, display: `${a}/x = ${b}`, answer: `x = ${x}` };
}

function makeRatLinear(opts: FluencyOptions, idx: number): Problem {
  // (ax + b)/c = d → ax + b = cd → x = (cd − b)/a
  const a = Math.abs(rndCoef(opts, false)) || 1;
  const c = Math.abs(rndCoef(opts, false)) || 1;
  const x = rndSolution(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
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
  const p = rnd(2, 10);
  let q = rnd(2, 10);
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

/** Format an inequality solution: "x (op) value". Uses `fmtSolution`'s
 *  fraction-aware formatter under the hood. */
function fmtIneqAnswer(num: number, den: number, op: IneqOp): string {
  return fmtSolution(num, den).replace(" = ", ` ${op} `);
}

// ----- Tier 1: One-Step Inequalities -----

function makeIneqOneAdd(opts: FluencyOptions, idx: number): Problem {
  const a = rndCoef(opts, false);
  const op = pickIneqOp();
  const x = rndSolution(opts, opts.allowNegatives);
  const b = x + a;
  return {
    num: idx,
    display: `x + ${a} ${op} ${b}`,
    answer: `x ${op} ${x}`,
  };
}

function makeIneqOneSub(opts: FluencyOptions, idx: number): Problem {
  const a = rndCoef(opts, false);
  const op = pickIneqOp();
  const x = rndSolution(opts, opts.allowNegatives);
  const b = x - a;
  return {
    num: idx,
    display: `x − ${a} ${op} ${b}`,
    answer: `x ${op} ${x}`,
  };
}

function makeIneqOneMul(opts: FluencyOptions, idx: number): Problem {
  // ax (op) b → x (op) b/a if a>0; x (flipped) b/a if a<0
  const a = rndCoef(opts, opts.allowNegatives);
  const op = pickIneqOp();
  const x = rndSolution(opts, opts.allowNegatives);
  const b = a * x;
  const outOp = a < 0 ? flipOp(op) : op;
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${op} ${b}`,
    answer: `x ${outOp} ${x}`,
  };
}

function makeIneqOneDiv(opts: FluencyOptions, idx: number): Problem {
  // x/a (op) b → x (op) ab if a>0; x (flipped) ab if a<0
  const a = rndCoef(opts, opts.allowNegatives);
  const op = pickIneqOp();
  const b = rndConst(opts, opts.allowNegatives);
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
  const a = Math.abs(rndCoef(opts, false)) || 1;
  const b = Math.abs(rndConst(opts, false));
  const op = pickIneqOp();
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
  let a = rndCoef(opts, true);
  if (a > 0) a = -a;
  const b = rndConst(opts, true);
  const op = pickIneqOp();
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
  // (1/d)x + b (op) c. Pick x so (1/d)x is integer.
  const d = [2, 3, 4, 5, 6][rnd(0, 4)];
  const b = rndConst(opts, opts.allowNegatives);
  const op = pickIneqOp();
  const x = rndSolution(opts, opts.allowNegatives) * d;
  const c = x / d + b;
  return {
    num: idx,
    display: `1/${d} · x ${fmtAddConst(b)} ${op} ${c}`,
    answer: `x ${op} ${x}`,
  };
}

function makeIneqTwoDist(opts: FluencyOptions, idx: number): Problem {
  // p(x + q) (op) r
  const p = rndCoef(opts, opts.allowNegatives);
  const q = rndConst(opts, opts.allowNegatives);
  const op = pickIneqOp();
  const x = rndSolution(opts, opts.allowNegatives);
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
  const a = rndCoef(opts, opts.allowNegatives);
  let b = rndCoef(opts, opts.allowNegatives);
  if (a + b === 0) b += 1;
  const c = rndConst(opts, opts.allowNegatives);
  const op = pickIneqOp();
  const x = rndSolution(opts, opts.allowNegatives);
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
  const p = rndCoef(opts, opts.allowNegatives);
  const q = rndConst(opts, opts.allowNegatives);
  const r = rndConst(opts, opts.allowNegatives);
  const op = pickIneqOp();
  const x = rndSolution(opts, opts.allowNegatives);
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
  const a = rndCoef(opts, opts.allowNegatives);
  let c = rndCoef(opts, opts.allowNegatives);
  if (a === c) c += 1;
  const x = rndSolution(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
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
  const p = rndCoef(opts, opts.allowNegatives);
  const q = rndConst(opts, opts.allowNegatives);
  const r = rndConst(opts, opts.allowNegatives);
  let s = rndCoef(opts, opts.allowNegatives);
  if (p === s) s += 1;
  const x = rndSolution(opts, opts.allowNegatives);
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
  const noSol = randomBool();
  const a = rndCoef(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
  const op = pickIneqOp();
  if (noSol) {
    // ax + b (op) ax + b + k where k makes it impossible
    // E.g., 2x + 3 < 2x + 1 → no solution
    return {
      num: idx,
      display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} ${op === "<" || op === "≤" ? op : op} ${fmtCoefTerm(a)} ${fmtAddConst(b - 2)}`,
      answer: op === "<" || op === "≤" ? "no solution" : "all real numbers",
    };
  }
  return {
    num: idx,
    display: `${fmtCoefTerm(a)} ${fmtAddConst(b)} ${op === ">" || op === "≥" ? op : op} ${fmtCoefTerm(a)} ${fmtAddConst(b - 2)}`,
    answer: op === ">" || op === "≥" ? "all real numbers" : "no solution",
  };
}

// ----- Tier 4: Compound Inequalities -----

function makeIneqCompoundAnd(opts: FluencyOptions, idx: number): Problem {
  // Build: a < x + k < b  →  a − k < x < b − k
  const k = rndCoef(opts, opts.allowNegatives);
  const lo = rndConst(opts, opts.allowNegatives);
  const range = opts.difficulty === "easy" ? 8 : 14;
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
  const k = rndCoef(opts, opts.allowNegatives);
  const a = rndConst(opts, opts.allowNegatives);
  const b = a + rnd(3, 10);
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
  const a = rndCoef(opts, opts.allowNegatives);
  const b = rnd(1, opts.difficulty === "easy" ? 8 : 14);
  const op: IneqOp = randomBool() ? "<" : "≤";
  return {
    num: idx,
    display: `|x ${fmtAddConst(a)}| ${op} ${b}`,
    answer: `${-b - a} ${op} x ${op} ${b - a}`,
  };
}

function makeIneqAbsGreater(opts: FluencyOptions, idx: number): Problem {
  // |x + a| > b  →  x + a < −b  OR  x + a > b
  const a = rndCoef(opts, opts.allowNegatives);
  const b = rnd(1, opts.difficulty === "easy" ? 8 : 14);
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
  const max = opts.difficulty === "easy" ? 12 : 20;
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
  const max = opts.difficulty === "easy" ? 12 : 24;
  // Pick base/height with base × height even so area is an integer.
  let b = rnd(2, max);
  let h = rnd(2, max);
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
  const max = opts.difficulty === "easy" ? 12 : 24;
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
  const max = opts.difficulty === "easy" ? 12 : 20;
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
  const max = opts.difficulty === "easy" ? 8 : 14;
  const r = rnd(2, max);
  return {
    num: idx,
    display: "",
    instruction: "Find the area in terms of π.",
    answer: formatPi(r * r, unit, true),
    shape: { kind: "circle", labels: { radius: `r = ${r} ${unit}` } },
  };
}

function makeCircleCircumference(opts: FluencyOptions, idx: number): Problem {
  const unit = pickUnit();
  const max = opts.difficulty === "easy" ? 8 : 14;
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
  const max = opts.difficulty === "easy" ? 12 : 20;
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
  const max = opts.difficulty === "easy" ? 12 : 20;
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
  const max = opts.difficulty === "easy" ? 10 : 16;
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
  const max = opts.difficulty === "easy" ? 12 : 22;
  let b = rnd(2, max);
  let h = rnd(2, max);
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
  const max = opts.difficulty === "easy" ? 12 : 22;
  let b = rnd(2, max);
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
  const max = opts.difficulty === "easy" ? 8 : 12;
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
  const max = opts.difficulty === "easy" ? 8 : 12;
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
  const max = opts.difficulty === "easy" ? 10 : 16;
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
  const max = opts.difficulty === "easy" ? 10 : 16;
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
  const max = opts.difficulty === "easy" ? 10 : 14;
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
  const max = opts.difficulty === "easy" ? 10 : 16;
  let b = rnd(2, max);
  let h = rnd(2, max);
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
  const length = rnd(2, opts.difficulty === "easy" ? 10 : 16);
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
  const max = opts.difficulty === "easy" ? 8 : 12;
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
  const max = opts.difficulty === "easy" ? 8 : 12;
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
  const max = opts.difficulty === "easy" ? 6 : 10;
  let r = rnd(2, max);
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
  const r = [3, 6, 9, 12][rnd(0, opts.difficulty === "easy" ? 1 : 3)];
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
  const max = opts.difficulty === "easy" ? 8 : 12;
  let b = rnd(2, max);
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
  const max = opts.difficulty === "easy" ? 10 : 16;
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
  const max = opts.difficulty === "easy" ? 8 : 12;
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
  const max = opts.difficulty === "easy" ? 7 : 10;
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
  const max = opts.difficulty === "easy" ? 6 : 9;
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
  const max = opts.difficulty === "easy" ? 5 : 8;
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
  const r = [3, 6, 9, 12][rnd(0, opts.difficulty === "easy" ? 1 : 3)];
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

const PYTH_WORD_TEMPLATES: ((opts: FluencyOptions) => { display: string; answer: string })[] = [
  () => {
    const [a, b, c] = pickPythTriple("medium");
    return {
      display: `A ladder ${c} ft long leans against a wall. The bottom is ${a} ft from the wall. How high up the wall does the ladder reach?`,
      answer: `${b} ft`,
    };
  },
  () => {
    const [a, b, c] = pickPythTriple("medium");
    return {
      display: `A rectangular swimming pool is ${a} m by ${b} m. How long is the diagonal?`,
      answer: `${c} m`,
    };
  },
  () => {
    const [a, b, c] = pickPythTriple("easy");
    return {
      display: `A TV screen is ${a} in tall and ${b} in wide. What is the diagonal length?`,
      answer: `${c} in`,
    };
  },
  () => {
    const [a, b, c] = pickPythTriple("medium");
    return {
      display: `Two cars start from the same point. One drives ${a} mi north and the other drives ${b} mi east. How far apart are they?`,
      answer: `${c} mi`,
    };
  },
];

function makePythWord(opts: FluencyOptions, idx: number): Problem {
  const pick = PYTH_WORD_TEMPLATES[rnd(0, PYTH_WORD_TEMPLATES.length - 1)];
  const r = pick(opts);
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
    mTerm = `${mn < 0 ? "−" : ""}${Math.abs(mn)}/${md} x`;
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

/** Tiny text-table helper for "x | y" style displays. */
function fmtTable(headers: string[], rows: (string | number)[][]): string {
  const lines = [headers.join("   "), "─".repeat(20)];
  for (const r of rows) lines.push(r.map((v) => String(v)).join("   "));
  return lines.join("\n");
}

// ----- Tier 1 — Rates & Unit Rates -----

const UNIT_RATE_CONTEXTS: ((opts: FluencyOptions) => { display: string; answer: string })[] = [
  () => {
    const r = rnd(2, 12);
    const t = rnd(2, 8);
    return { display: `${r * t} miles in ${t} hours. Find the unit rate.`, answer: `${r} miles per hour` };
  },
  () => {
    const r = rnd(2, 15);
    const t = rnd(2, 8);
    return { display: `${r * t} words typed in ${t} minutes. Find the unit rate.`, answer: `${r} words per minute` };
  },
  () => {
    const r = rnd(2, 12);
    const t = rnd(2, 6);
    return { display: `$${r * t} for ${t} pounds. Find the unit price.`, answer: `$${r} per pound` };
  },
  () => {
    const r = rnd(2, 15);
    const t = rnd(2, 8);
    return { display: `${r * t} pages read in ${t} days. Find the unit rate.`, answer: `${r} pages per day` };
  },
];

function makeUnitRate(opts: FluencyOptions, idx: number): Problem {
  const pick = UNIT_RATE_CONTEXTS[rnd(0, UNIT_RATE_CONTEXTS.length - 1)];
  const r = pick(opts);
  return { num: idx, display: r.display, answer: r.answer };
}

function makeRateTable(opts: FluencyOptions, idx: number): Problem {
  // Build a table with a missing entry. Rate = y/x.
  const rate = rnd(2, opts.difficulty === "easy" ? 6 : 10);
  const xs = [1, rnd(2, 4), rnd(5, 7), rnd(8, 12)];
  // Hide one of the y-values.
  const hide = rnd(1, xs.length - 1);
  const rows = xs.map((x, i) => [x, i === hide ? "?" : x * rate]);
  return {
    num: idx,
    display: `Complete the rate table.\n${fmtTable(["x", "y"], rows)}`,
    answer: `? = ${xs[hide] * rate}`,
  };
}

function makeRateConvert(opts: FluencyOptions, idx: number): Problem {
  const which = rnd(0, 2);
  if (which === 0) {
    const mph = rnd(20, 80);
    const fps = Math.round((mph * 5280) / 3600 * 100) / 100;
    return { num: idx, display: `Convert ${mph} mph to ft/sec.`, answer: `${fps} ft/sec` };
  }
  if (which === 1) {
    const perOz = rnd(2, 12); // cents/oz
    const perLb = perOz * 16;
    return { num: idx, display: `If a snack costs $0.${String(perOz).padStart(2, "0")} per ounce, what is the price per pound?`, answer: `$${(perLb / 100).toFixed(2)} per pound` };
  }
  const mPerSec = rnd(2, 20);
  const kmPerHr = (mPerSec * 3600) / 1000;
  return { num: idx, display: `Convert ${mPerSec} m/sec to km/hr.`, answer: `${kmPerHr} km/hr` };
}

// ----- Tier 2 — Proportional Relationships -----

function makePropKTable(opts: FluencyOptions, idx: number): Problem {
  const k = rnd(2, opts.difficulty === "easy" ? 6 : 10);
  const xs = [1, rnd(2, 4), rnd(5, 7), rnd(8, 11)];
  const rows = xs.map((x) => [x, x * k]);
  return {
    num: idx,
    display: `Find the constant of proportionality k.\n${fmtTable(["x", "y"], rows)}`,
    answer: `k = ${k}`,
  };
}

function makePropKGraph(opts: FluencyOptions, idx: number): Problem {
  // Pick a clean slope; the line passes through origin.
  const k = rnd(2, opts.difficulty === "easy" ? 4 : 6);
  return {
    num: idx,
    display: `Find the constant of proportionality k from the graph.`,
    answer: `k = ${k}`,
    shape: {
      kind: "grid",
      labels: {},
      grid: {
        range: 10,
        lines: [{ x1: 0, y1: 0, x2: 5, y2: 5 * k }],
        points: [{ x: 1, y: k, label: `(1, ${k})` }],
      },
    },
  };
}

function makePropEquation(opts: FluencyOptions, idx: number): Problem {
  const k = rnd(2, opts.difficulty === "easy" ? 6 : 9);
  const xs = [1, rnd(2, 4), rnd(5, 7), rnd(8, 11)];
  const rows = xs.map((x) => [x, x * k]);
  return {
    num: idx,
    display: `Write the equation in the form y = kx.\n${fmtTable(["x", "y"], rows)}`,
    answer: `y = ${k}x`,
  };
}

function makePropTableYN(opts: FluencyOptions, idx: number): Problem {
  const yes = randomBool();
  const k = rnd(2, 6);
  const xs = [1, 2, 3, 4];
  const rows = yes
    ? xs.map((x) => [x, x * k])
    : xs.map((x, i) => [x, x * k + (i === 0 ? 0 : rnd(1, 3))]);
  return {
    num: idx,
    display: `Is the table proportional? (Yes or No)\n${fmtTable(["x", "y"], rows)}`,
    answer: yes ? `Yes — k = ${k}` : `No — y/x ratios are not equal`,
  };
}

function makePropGraphYN(opts: FluencyOptions, idx: number): Problem {
  const yes = randomBool();
  const k = rnd(1, 4);
  if (yes) {
    return {
      num: idx,
      display: `Is the graph proportional? (Yes or No)`,
      answer: `Yes — line passes through (0, 0)`,
      shape: {
        kind: "grid",
        labels: {},
        grid: { range: 10, lines: [{ x1: 0, y1: 0, x2: 5, y2: 5 * k }] },
      },
    };
  }
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
  const num = rnd(1, opts.difficulty === "easy" ? 3 : 5) * (randomBool() ? 1 : -1);
  const den = opts.difficulty === "hard" ? rnd(1, 3) : 1;
  // Pick a starting point that keeps the line on-screen.
  const x1 = rnd(-4, 0);
  const y1 = rnd(-4, 4);
  const x2 = x1 + 4 * den;
  const y2 = y1 + 4 * num;
  return {
    num: idx,
    display: `Find the slope from the graph.`,
    answer: `m = ${fmtSlope(num, den)}`,
    shape: {
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

function makeSlopeTable(opts: FluencyOptions, idx: number): Problem {
  const num = rnd(1, opts.difficulty === "easy" ? 4 : 7) * (randomBool() ? 1 : -1);
  const x0 = rnd(0, 3);
  const y0 = rnd(-5, 5);
  const xs = [x0, x0 + 1, x0 + 2, x0 + 3];
  const rows = xs.map((x) => [x, y0 + num * (x - x0)]);
  return {
    num: idx,
    display: `Find the slope from the table.\n${fmtTable(["x", "y"], rows)}`,
    answer: `m = ${num}`,
  };
}

function makeSlopeVerbal(opts: FluencyOptions, idx: number): Problem {
  const which = rnd(0, 2);
  const rise = rnd(2, 12);
  const run = rnd(2, 6);
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
  const which = rnd(0, 3);
  const x1 = rnd(-5, 5);
  const y1 = rnd(-5, 5);
  if (which === 0) {
    return {
      num: idx,
      display: `Classify the slope through ${fmtPoint(x1, y1)} and ${fmtPoint(x1 + 3, y1 + 4)}.`,
      answer: `positive`,
    };
  }
  if (which === 1) {
    return {
      num: idx,
      display: `Classify the slope through ${fmtPoint(x1, y1)} and ${fmtPoint(x1 + 3, y1 - 4)}.`,
      answer: `negative`,
    };
  }
  if (which === 2) {
    return {
      num: idx,
      display: `Classify the slope through ${fmtPoint(x1, y1)} and ${fmtPoint(x1 + 3, y1)}.`,
      answer: `zero (horizontal)`,
    };
  }
  return {
    num: idx,
    display: `Classify the slope through ${fmtPoint(x1, y1)} and ${fmtPoint(x1, y1 + 3)}.`,
    answer: `undefined (vertical)`,
  };
}

// ----- Tier 4 — Slope-Intercept Form -----

function makeSIIdentify(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
  return {
    num: idx,
    display: `Identify m and b in: ${fmtMxB(m, b)}`,
    answer: `m = ${m}, b = ${b}`,
  };
}

function makeSIFromMB(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
  return {
    num: idx,
    display: `Write the equation in y = mx + b form. Slope: ${m}, y-intercept: ${b}.`,
    answer: fmtMxB(m, b),
  };
}

function makeSIFromMP(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, opts.allowNegatives);
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
  const m = rndCoef(opts, opts.allowNegatives);
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
  const a = rndCoef(opts, opts.allowNegatives);
  const b = Math.abs(rndCoef(opts, false)) || 2;
  const c = rndConst(opts, opts.allowNegatives);
  return {
    num: idx,
    display: `Convert to slope-intercept form: ${fmtCoefTerm(a)} ${fmtAddCoef(b, "y")} = ${c}`,
    answer: fmtMxB(-a, c, b).replace(" + ", " + ").replace(" − ", " − "),
  };
}

function makeSIToStd(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
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
  const m = rndCoef(opts, opts.allowNegatives);
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
  const m = rndCoef(opts, opts.allowNegatives);
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
  const rows = xs.map((x) => [x, m * x + b]);
  const y1 = m * -4 + b;
  const y2 = m * 4 + b;
  return {
    num: idx,
    display: `Graph the line from the table.\n${fmtTable(["x", "y"], rows)}`,
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
  const A = rnd(1, 4);
  const B = rnd(1, 4);
  const xInt = rnd(-4, 4) || 2;
  const yInt = rnd(-4, 4) || 3;
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
  const x1 = rnd(-5, -1);
  const y1 = rnd(-5, 5);
  const x2 = rnd(1, 5);
  const y2 = rnd(-5, 5);
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
  const yes = randomBool();
  // Yes: any linear function. No: a sideways parabola / circle-like curve.
  if (yes) {
    const m = rnd(1, 3) * (randomBool() ? 1 : -1);
    const b = rnd(-3, 3);
    return {
      num: idx,
      display: `Is this a function? (Apply the vertical line test.)`,
      answer: `Yes`,
      shape: {
        kind: "grid",
        labels: {},
        grid: { range: 10, lines: [{ x1: -4, y1: m * -4 + b, x2: 4, y2: m * 4 + b }] },
      },
    };
  }
  // Sideways parabola: x = y² shape
  const pts: [number, number][] = [];
  for (let y = -3; y <= 3; y += 0.5) {
    pts.push([y * y - 2, y]);
  }
  return {
    num: idx,
    display: `Is this a function? (Apply the vertical line test.)`,
    answer: `No — fails the vertical line test`,
    shape: { kind: "grid", labels: {}, grid: { range: 10, curve: pts } },
  };
}

function makeFnTable(opts: FluencyOptions, idx: number): Problem {
  const yes = randomBool();
  if (yes) {
    const m = rnd(1, 5);
    const xs = [1, 2, 3, 4];
    return {
      num: idx,
      display: `Is this table a function? (Yes or No)\n${fmtTable(["x", "y"], xs.map((x) => [x, m * x]))}`,
      answer: `Yes — each x has exactly one y`,
    };
  }
  // Repeat an x with different y
  return {
    num: idx,
    display: `Is this table a function? (Yes or No)\n${fmtTable(["x", "y"], [[1, 4], [2, 6], [2, 9], [3, 11]])}`,
    answer: `No — x = 2 maps to both 6 and 9`,
  };
}

function makeFnEval(opts: FluencyOptions, idx: number): Problem {
  const m = rndCoef(opts, opts.allowNegatives);
  const b = rndConst(opts, opts.allowNegatives);
  const c = rndSolution(opts, opts.allowNegatives);
  return {
    num: idx,
    display: `Given f(x) = ${fmtMxB(m, b).replace("y = ", "")}, find f(${c}).`,
    answer: `f(${c}) = ${m * c + b}`,
  };
}

function makeFnReverse(opts: FluencyOptions, idx: number): Problem {
  const m = Math.abs(rndCoef(opts, false)) || 2;
  const b = rndConst(opts, opts.allowNegatives);
  const x = rndSolution(opts, opts.allowNegatives);
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
    const rows = [1, 2, 3, 4].map((x) => [x, m * x]);
    return {
      num: idx,
      display: `Classify this table as Linear or Nonlinear.\n${fmtTable(["x", "y"], rows)}`,
      answer: `Linear (constant rate of change ${m})`,
    };
  }
  // Quadratic-ish
  const rows = [1, 2, 3, 4].map((x) => [x, x * x]);
  return {
    num: idx,
    display: `Classify this table as Linear or Nonlinear.\n${fmtTable(["x", "y"], rows)}`,
    answer: `Nonlinear (differences are not constant)`,
  };
}

function makeRateCompare(opts: FluencyOptions, idx: number): Problem {
  const r1 = rnd(2, 9);
  const t1 = rnd(2, 5);
  const r2 = rnd(2, 9);
  const t2 = rnd(2, 5);
  const u1 = (r1 * t1) / (t1 * 1); // r1 (per unit)
  const u2 = (r2 * t2) / (t2 * 1);
  // Just compare per-unit rates directly:
  const rate1 = r1;
  const rate2 = r2;
  const winner = rate1 > rate2 ? "Job A" : rate1 < rate2 ? "Job B" : "Equal";
  return {
    num: idx,
    display: `Job A pays $${r1 * t1} for ${t1} hours. Job B pays $${r2 * t2} for ${t2} hours. Which pays more per hour?`,
    answer: `${winner} ($${rate1}/hr vs $${rate2}/hr)`,
  };
}

function makeLinearCompare(opts: FluencyOptions, idx: number): Problem {
  const m1 = rndCoef(opts, opts.allowNegatives);
  const b1 = rndConst(opts, opts.allowNegatives);
  const m2 = rndCoef(opts, opts.allowNegatives);
  const b2 = rndConst(opts, opts.allowNegatives);
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
  const a = rndCoef(opts, opts.allowNegatives);
  const d = rndConst(opts, opts.allowNegatives);
  const k = rnd(1, opts.difficulty === "easy" ? 5 : 8);
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
 *  naturally ("x" not "1x", "−x" not "−1x"). */
function fmtTerm(coef: number, variable: string): string {
  if (coef === 0) return "";
  if (coef === 1) return variable;
  if (coef === -1) return `−${variable}`;
  return `${coef}${variable}`;
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
function makeCombineLikeTerms(opts: FluencyOptions, num: number): Problem {
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
  const s = rounded.toString();
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
  // 7 integer / 7 fraction / 6 decimal.
  const wantFrac = !!opts.distributeIncludeFractions;
  const wantDec = !!opts.distributeIncludeDecimals;
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
  let c = pickInsideCoef();
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
  // rational group; with one toggle on, ~½ do.
  const wantFrac = !!opts.distributeIncludeFractions;
  const wantDec = !!opts.distributeIncludeDecimals;
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
      if (baseT === "multiply-fractions" || baseT === "divide-fractions") {
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
  "ineq-one-add": "One-Step: x + a (op) b",
  "ineq-one-sub": "One-Step: x − a (op) b",
  "ineq-one-mul": "One-Step: ax (op) b",
  "ineq-one-div": "One-Step: x/a (op) b",
  "ineq-one-mixed": "One-Step: Mixed",
  "ineq-two-pos": "Two-Step: ax + b (op) c",
  "ineq-two-neg": "Two-Step with Negatives (Flip)",
  "ineq-two-rational": "Two-Step with Rationals",
  "ineq-two-dist": "Two-Step: p(x + q) (op) r",
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
