/**
 * Short teacher-friendly labels for the standards codes that appear on tasks.
 * Used by the Tasks Library and detail page so a teacher scanning "7.AF.2"
 * sees "Solve two-step equations" alongside it.
 *
 * Lookup falls back gracefully:
 *   1. Exact match (e.g., "7.AF.4a")
 *   2. Strip the trailing letter (e.g., "7.AF.4")
 *   3. Family fallback (e.g., "7.AF" → "Algebra & Functions, Grade 7")
 *   4. Generic empty string — caller can decide whether to render anything.
 */

import type { StandardsSystem } from "./tasks-filter";

const FAMILY_LABELS: Record<string, string> = {
  "6.RP": "Ratios & Proportional Relationships, Grade 6",
  "6.NS": "Number Sense, Grade 6",
  "6.AF": "Algebra & Functions, Grade 6",
  "6.GM": "Geometry & Measurement, Grade 6",
  "6.DSP": "Data Analysis & Statistics, Grade 6",

  "7.NS": "Number Sense, Grade 7",
  "7.C": "Computation, Grade 7",
  "7.AF": "Algebra & Functions, Grade 7",
  "7.GM": "Geometry & Measurement, Grade 7",
  "7.DSP": "Data, Statistics & Probability, Grade 7",
  "7.EE": "Expressions & Equations, Grade 7",
  "7.RP": "Ratios & Proportional Relationships, Grade 7",
  "7.SP": "Statistics & Probability, Grade 7",
  "7.G": "Geometry, Grade 7",

  "8.NS": "Number Sense, Grade 8",
  "8.AF": "Algebra & Functions, Grade 8",
  "8.EE": "Expressions & Equations, Grade 8",
  "8.F": "Functions, Grade 8",
  "8.G": "Geometry, Grade 8",

  MP: "Mathematical Practices",
};

// Authoritative 2023 IAS-M Grade 7 descriptions, sourced from the
// Indiana DOE Grade-7 IAS-CCSS Correlation Guide (updated July 2024).
// Phrasing is condensed for chip display; the full standard text is the
// source of truth.
const INDIANA_2023: Record<string, string> = {
  // ----- Grade 7 Number Sense -----
  "7.NS.1": "Additive inverses and sums of rational numbers (number line)",
  "7.NS.2": "Distance between rational numbers as |difference|",
  "7.NS.3": "Multiply signed numbers via distributive property",
  "7.NS.4": "Divide integers; –(p/q) = (–p)/q = p/(–q)",
  "7.NS.5": "Prime factorization using exponents",
  "7.NS.6": "Square roots of perfect square whole numbers",
  "7.NS.7": "Compute fluently with rational numbers",

  // ----- Grade 7 Ratios and Proportional Reasoning -----
  "7.RP.1": "Identify the unit rate / constant of proportionality",
  "7.RP.2": "Multi-step ratio & percent problems (tax, markup, interest)",
  "7.RP.3": "Represent proportional relationships; y = mx",

  // ----- Grade 7 Algebra and Functions -----
  "7.AF.1": "Create equivalent linear expressions; justify each step",
  "7.AF.2": "Solve real-world problems using one or two operations",
  "7.AF.3": "Solve px + q = r and p(x + q) = r in context",
  "7.AF.4": "Solve and graph inequalities px + q ≥/≤ r in context",
  "7.AF.5": "Slope as constant rate of change; constant vs varying",
  "7.AF.6": "Graph a line from slope and a point; find slope from graph",

  // ----- Grade 7 Geometry and Measurement -----
  "7.GM.1": "Scale drawings: real-world lengths and areas",
  "7.GM.2": "Area & circumference of circles; informal derivation",
  "7.GM.3": "Volume of cylinders & composite right prisms",

  // ----- Grade 7 Data, Statistics, and Probability -----
  "7.DSP.1": "Random sampling produces representative samples",
  "7.DSP.2": "Measures of center and spread; compare two populations",
  "7.DSP.3": "Visual overlap of distributions; effect of outliers",
  "7.DSP.4": "Probability as a number 0–1; likelihood vocabulary",
  "7.DSP.5": "Probability models; predicted vs observed frequency",

  // ----- Grade 6 (cross-grade codes our tasks use, per 2023 IAS) -----
  "6.RP.4": "Solve real-world problems with rates and ratios using models",
  "6.GM.4": "Volume of right rectangular prisms with fractional edges",

  // ----- Grade 8 (cross-grade codes our tasks use, per 2023 IAS) -----
  "8.NS.1": "Rational vs. irrational numbers; decimal expansions",
  "8.NS.4": "Real-world problems with rationals using multiple operations",
  "8.AF.1": "Solve linear equations & inequalities with rational coefficients",
};

const COMMON_CORE: Record<string, string> = {
  // ----- 7.RP — Ratios & Proportional Relationships -----
  "7.RP.A.1": "Compute unit rates including ratios of fractions",
  "7.RP.A.2": "Recognize and represent proportional relationships",
  "7.RP.A.2a": "Decide whether two quantities are in proportion",
  "7.RP.A.2b": "Identify the constant of proportionality (k)",
  "7.RP.A.2c": "Represent proportions by y = kx",
  "7.RP.A.3": "Use proportional relationships to solve multistep problems",

  // ----- 7.NS — The Number System -----
  "7.NS.A.1": "Add and subtract rational numbers",
  "7.NS.A.2": "Multiply and divide rational numbers",
  "7.NS.A.3": "Solve real-world problems with rational numbers",

  // ----- 7.EE — Expressions & Equations -----
  "7.EE.A.1": "Add, subtract, factor, and expand linear expressions",
  "7.EE.A.2": "Rewrite expressions to reveal new meaning",
  "7.EE.B.3": "Multi-step real-world problems with rational numbers",
  "7.EE.B.4": "Use variables to write equations and inequalities",
  "7.EE.B.4a": "Solve word problems leading to px + q = r and p(x+q) = r",
  "7.EE.B.4b": "Solve word problems leading to inequalities px + q > r",

  // ----- 7.G — Geometry -----
  "7.G.A.1": "Scale drawings of geometric figures",
  "7.G.B.4": "Area and circumference of circles",
  "7.G.B.6": "Area, volume, and surface area of 2-D and 3-D figures",

  // ----- 7.SP — Statistics & Probability -----
  "7.SP.A.1": "Understand random sampling",
  "7.SP.A.2": "Use a sample to draw inferences about a population",
  "7.SP.B.3": "Visually compare two populations",
  "7.SP.B.4": "Use measures of center / variability to compare populations",
  "7.SP.C.5": "Probability of a chance event as a number 0–1",
  "7.SP.C.6": "Approximate probabilities from data",
  "7.SP.C.7": "Develop a probability model",
  "7.SP.C.8": "Find probabilities of compound events",

  // ----- 6.* and 8.* (cross-grade extension codes our tasks use) -----
  "6.RP.A.3": "Use ratio reasoning to solve real-world problems",
  "6.NS.B.4": "Greatest common factor and least common multiple",
  "6.G.A.4": "Represent 3-D figures with nets; find surface area",
  "8.EE.A.2": "Square roots and cube roots",
  "8.EE.B.5": "Graph proportional relationships; compare different rates",
  "8.F.A.3": "Linear vs. nonlinear functions",
  "8.F.B.4": "Construct linear functions from descriptions or tables",
  "8.F.B.5": "Describe a function qualitatively from its graph",
  "8.G.C.9": "Volume of cylinders, cones, and spheres",
  "8.NS.A.2": "Approximate irrational numbers; locate on a number line",

  // ----- Mathematical Practices -----
  "MP.1": "Make sense of problems and persevere",
  "MP.7": "Look for and make use of structure",
};

/**
 * Look up a teacher-friendly phrase for a standard code. Falls back to the
 * family label (e.g., "Algebra & Functions, Grade 7") if no exact match.
 * Returns the code itself only if nothing fits.
 */
export function getStandardLabel(
  code: string,
  system: StandardsSystem
): string {
  const table = system === "indiana" ? INDIANA_2023 : COMMON_CORE;
  if (table[code]) return table[code];
  // Strip trailing letter (e.g., "7.AF.4a" → "7.AF.4") before retrying.
  const stripped = code.replace(/[a-z]$/i, "");
  if (table[stripped]) return table[stripped];
  // Family fallback (e.g., "7.AF.1" → "7.AF" → "Algebra & Functions…").
  const family = code.split(".").slice(0, 2).join(".");
  if (FAMILY_LABELS[family]) return FAMILY_LABELS[family];
  // Bare-prefix fallback (e.g., "MP.1" → "MP").
  const head = code.split(".")[0];
  if (FAMILY_LABELS[head]) return FAMILY_LABELS[head];
  return "";
}
