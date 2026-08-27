export interface Standard {
  code: string;
  domain: string;
  domainName: string;
  text: string;
}

export const MATH_STANDARDS: Record<number, Standard[]> = {
  6: [
    { code: "6.AF.1", domain: "AF", domainName: "Algebra & Functions", text: "Define and use variables in expressions; evaluate for given values." },
    { code: "6.AF.2", domain: "AF", domainName: "Algebra & Functions", text: "Determine which values make an equation or inequality true using substitution." },
    { code: "6.AF.3", domain: "AF", domainName: "Algebra & Functions", text: "Solve equations of the form x+p=q, px=q fluently with nonneg. rationals." },
    { code: "6.AF.4", domain: "AF", domainName: "Algebra & Functions", text: "Write inequalities (x>c, x<c, etc.) for real-world constraints." },
    { code: "6.AF.5", domain: "AF", domainName: "Algebra & Functions", text: "Plot points in all four quadrants; find distances between points." },
    { code: "6.RP.1", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Convert between fractions, decimals, and percents." },
    { code: "6.RP.2", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Understand unit rates and use rate terminology." },
    { code: "6.RP.3", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Make tables of equivalent ratios; find missing values; plot pairs." },
    { code: "6.RP.4", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Solve real-world problems involving rates and ratios." },
    { code: "6.RP.5", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Use variables to represent proportional relationships; write equations." },
    { code: "6.NS.1", domain: "NS", domainName: "Number Sense", text: "Understand positive/negative numbers for opposite directions/values." },
    { code: "6.NS.2", domain: "NS", domainName: "Number Sense", text: "Use positive/negative numbers in real-world contexts; concept of opposites." },
    { code: "6.NS.3", domain: "NS", domainName: "Number Sense", text: "Compare, order, and plot rational numbers on a number line." },
    { code: "6.NS.4", domain: "NS", domainName: "Number Sense", text: "Solve real-world problems with fractions and decimals (1-2 operations)." },
    { code: "6.NS.5", domain: "NS", domainName: "Number Sense", text: "Use order of operations with non-negative rational numbers." },
    { code: "6.NS.6", domain: "NS", domainName: "Number Sense", text: "Find GCF and LCM; use distributive property with common factors." },
    { code: "6.NS.7", domain: "NS", domainName: "Number Sense", text: "Apply properties of operations to generate equivalent expressions." },
    { code: "6.NS.8", domain: "NS", domainName: "Number Sense", text: "Evaluate expressions with positive rational bases and whole-number exponents." },
    { code: "6.GM.1", domain: "GM", domainName: "Geometry & Measurement", text: "Convert between customary and metric measurement systems." },
    { code: "6.GM.2", domain: "GM", domainName: "Geometry & Measurement", text: "Apply sums of interior angles of triangles and quadrilaterals." },
    { code: "6.GM.3", domain: "GM", domainName: "Geometry & Measurement", text: "Find area of complex shapes by composing/decomposing polygons." },
    { code: "6.GM.4", domain: "GM", domainName: "Geometry & Measurement", text: "Find volume of right rectangular prisms with fractional edges." },
    { code: "6.DS.1", domain: "DS", domainName: "Data Analysis & Statistics", text: "Represent data with dot plots, histograms, and box plots." },
    { code: "6.DS.2", domain: "DS", domainName: "Data Analysis & Statistics", text: "Formulate statistical questions; collect and organize data." },
    { code: "6.DS.3", domain: "DS", domainName: "Data Analysis & Statistics", text: "Determine measures of center and variability; describe patterns." },
  ],
  7: [
    { code: "7.AF.1", domain: "AF", domainName: "Algebra & Functions", text: "Create equivalent linear expressions using properties; factor." },
    { code: "7.AF.2", domain: "AF", domainName: "Algebra & Functions", text: "Solve real-world problems with rational numbers (1-2 operations)." },
    { code: "7.AF.3", domain: "AF", domainName: "Algebra & Functions", text: "Solve equations px+q=r and p(x+q)=r fluently." },
    { code: "7.AF.4", domain: "AF", domainName: "Algebra & Functions", text: "Solve inequalities px+q>r or px+q<r; graph solution sets." },
    { code: "7.AF.5", domain: "AF", domainName: "Algebra & Functions", text: "Define slope; identify constant or varying rates of change." },
    { code: "7.AF.6", domain: "AF", domainName: "Algebra & Functions", text: "Graph a line from slope and point; find slope from a graph." },
    { code: "7.RP.1", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Compute unit rates with fractions; identify constant of proportionality." },
    { code: "7.RP.2", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Solve percent problems: discounts, markups, interest, tax, tips." },
    { code: "7.RP.3", domain: "RP", domainName: "Ratios & Proportional Reasoning", text: "Recognize proportional relationships; write y=mx equations." },
    { code: "7.NS.1", domain: "NS", domainName: "Number Sense", text: "Find sums of rational numbers; interpret in real-world contexts." },
    { code: "7.NS.2", domain: "NS", domainName: "Number Sense", text: "Find differences of rational numbers; represent on number lines." },
    { code: "7.NS.3", domain: "NS", domainName: "Number Sense", text: "Find products of rational numbers; rules for multiplying signed numbers." },
    { code: "7.NS.4", domain: "NS", domainName: "Number Sense", text: "Find quotients of rational numbers; understand -(p/q) = (-p)/q." },
    { code: "7.NS.5", domain: "NS", domainName: "Number Sense", text: "Find prime factorizations; write using exponents." },
    { code: "7.NS.6", domain: "NS", domainName: "Number Sense", text: "Understand irrational numbers; evaluate square roots of perfect squares." },
    { code: "7.NS.7", domain: "NS", domainName: "Number Sense", text: "Compute fluently with rational numbers using order of operations." },
    { code: "7.GM.1", domain: "GM", domainName: "Geometry & Measurement", text: "Solve problems with scale drawings; compute actual lengths and areas." },
    { code: "7.GM.2", domain: "GM", domainName: "Geometry & Measurement", text: "Use formulas for area and circumference of circles." },
    { code: "7.GM.3", domain: "GM", domainName: "Geometry & Measurement", text: "Use volume formulas for cylinders and composite rectangular prisms." },
    { code: "7.DSP.1", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Use representative samples to gain information about a population." },
    { code: "7.DSP.2", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Draw informal comparative inferences about two populations." },
    { code: "7.DSP.3", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Assess overlap between two data distributions with similar variability." },
    { code: "7.DSP.4", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Understand probability 0-1; classify events by likelihood." },
    { code: "7.DSP.5", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Develop probability models; compare model to observed frequencies." },
  ],
  8: [
    { code: "8.AF.1", domain: "AF", domainName: "Algebra & Functions", text: "Solve linear equations/inequalities with rational coefficients fluently." },
    { code: "8.AF.2", domain: "AF", domainName: "Algebra & Functions", text: "Generate linear equations with one, infinite, or no solutions." },
    { code: "8.AF.3", domain: "AF", domainName: "Algebra & Functions", text: "Understand functions: each x maps to exactly one y. Determine if a relation is a function." },
    { code: "8.AF.4", domain: "AF", domainName: "Algebra & Functions", text: "Describe functional relationships qualitatively from graphs." },
    { code: "8.AF.5", domain: "AF", domainName: "Algebra & Functions", text: "Interpret y=mx+b as a linear function; compare to nonlinear functions." },
    { code: "8.AF.6", domain: "AF", domainName: "Algebra & Functions", text: "Construct linear functions; describe meaning of m and b in y=mx+b." },
    { code: "8.AF.7", domain: "AF", domainName: "Algebra & Functions", text: "Compare two linear functions in different representations." },
    { code: "8.AF.8", domain: "AF", domainName: "Algebra & Functions", text: "Approximate solutions of systems of equations by graphing." },
    { code: "8.NS.1", domain: "NS", domainName: "Number Sense", text: "Distinguish rational vs irrational numbers; understand decimal expansions." },
    { code: "8.NS.2", domain: "NS", domainName: "Number Sense", text: "Use rational approximations of irrational numbers; locate on number line." },
    { code: "8.NS.3", domain: "NS", domainName: "Number Sense", text: "Apply properties of integer exponents to generate equivalent expressions." },
    { code: "8.NS.4", domain: "NS", domainName: "Number Sense", text: "Solve real-world problems with rational numbers using multiple operations." },
    { code: "8.GM.1", domain: "GM", domainName: "Geometry & Measurement", text: "Identify and perform transformations on a coordinate plane." },
    { code: "8.GM.2", domain: "GM", domainName: "Geometry & Measurement", text: "Use volume formulas for cones, spheres, pyramids; surface area of spheres." },
    { code: "8.GM.3", domain: "GM", domainName: "Geometry & Measurement", text: "Apply Pythagorean Theorem to find unknown side lengths." },
    { code: "8.DSP.1", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Construct and interpret scatter plots; describe clustering, outliers, and association." },
    { code: "8.DSP.2", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Write and use linear-model equations to make predictions; interpret slope and y-intercept." },
    { code: "8.DSP.3", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Represent sample spaces and find probabilities of compound events (lists, tables, tree diagrams)." },
    { code: "8.DSP.4", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Find probabilities of compound events; classify independent, dependent, complementary, and mutually exclusive events." },
    { code: "8.DSP.5", domain: "DSP", domainName: "Data, Statistics & Probability", text: "Apply the multiplication counting principle to situations with many outcomes." },
  ],
};

export function getStandardsForGrade(grade: number): Standard[] {
  return MATH_STANDARDS[grade] ?? [];
}

export function getDomainsForGrade(grade: number): string[] {
  const standards = getStandardsForGrade(grade);
  return [...new Set(standards.map((s) => s.domainName))];
}

export function getStandardsByDomain(grade: number): Record<string, Standard[]> {
  const standards = getStandardsForGrade(grade);
  const grouped: Record<string, Standard[]> = {};
  for (const s of standards) {
    if (!grouped[s.domainName]) grouped[s.domainName] = [];
    grouped[s.domainName].push(s);
  }
  return grouped;
}

export const STRUGGLE_BUS_URL = "https://strugglebus-1096205389759.us-central1.run.app";
