import { notFound } from "next/navigation";
import type { Metadata } from "next";
import path from "path";
import fs from "fs/promises";
import { execFile } from "child_process";
import SkillProjectionRunner from "@/components/intervention/SkillProjectionRunner";

interface SkillJSON {
  standard_code: string;
  skills: Array<{
    skill_id: string;
    name: string;
    column: string;
    sample_items: Array<{ stem: string; answer: string; choices?: string[] }>;
    printable_artifact?: {
      title?: string;
      kind?: string;
      categories?: string[];
      items?: string[];
      instructions?: string;
    };
    // Teacher-facing lesson content forwarded to the projection's
    // presenter panel (never rendered on the student-facing stage).
    i_do_script?: string;
    worked_example_script?: Array<{ kind: string; text: string }>;
    canonical_error?: { pattern: string; example: string; why?: string };
    redirect_script?: { stop: string; prompt: string; praise: string };
    sentence_starters?: string[];
  }>;
}

const PYTHON_PATH =
  process.env.PYTHON_PATH ??
  "C:/Users/meyedl01/AppData/Local/Python/pythoncore-3.14-64/python.exe";

async function loadAllSkills() {
  const root = path.join(process.cwd(), "..", "Cooties", "data", "skills");
  let entries: string[] = [];
  try {
    entries = await fs.readdir(root);
  } catch {
    return [];
  }
  const out: Array<{
    skill_id: string;
    standard_code: string;
    skill: SkillJSON["skills"][number];
  }> = [];
  for (const file of entries) {
    if (!file.endsWith(".json")) continue;
    try {
      const data = JSON.parse(await fs.readFile(path.join(root, file), "utf-8")) as SkillJSON;
      for (const s of data.skills ?? []) {
        out.push({ skill_id: s.skill_id, standard_code: data.standard_code, skill: s });
      }
    } catch {
      // Bad JSON files are skipped silently — no need to crash the build.
    }
  }
  return out;
}

// render_data shapes the Python engine emits. The projection runner
// dispatches on `type` and renders an SVG diagram inline with the stem.
export interface RenderData {
  type?: string;
  // number_line
  value?: number;
  circle_type?: "open" | "closed";
  direction?: "left" | "right";
  // coordinate_grid
  x_range?: [number, number];
  y_range?: [number, number];
  points?: Array<{ x: number; y: number; label?: string }>;
  // svg_html
  svg_html?: string;
}

export interface ResolvedItem {
  stem: string;
  answer: string;
  choices?: string[];
  section: string;
  render_data?: RenderData | null;
  choices_render?: Array<RenderData | null> | null;
  parts?: Array<{ label: string; prompt: string; answer: string; item_type?: string }> | null;
  type?: string | null;
  shown_work?: string[] | null;
}

interface SolutionStepJSON {
  math?: string | null;
  annotation?: string;
  given?: boolean;
}
interface WorkedSolutionJSON {
  stem: string;
  answer: string;
  steps: SolutionStepJSON[];
  render_data?: RenderData | null;
}

interface ResolvedItems {
  items: ResolvedItem[];
  session: number;
  // Session-sheet extras (v3 skills) so the projection mirrors the paper.
  fluency?: { title?: string; items: Array<{ stem: string; answer: string }> } | null;
  worked_solution?: WorkedSolutionJSON | null;
  faded_example?: WorkedSolutionJSON | null;
  sentence_starters?: string[] | null;
}

/**
 * Spawn the Python generator in `mode: "items"` to get the same problem
 * set the printed packet would use for this (skill, session). Keeps the
 * projection in lockstep with the packet so a teacher can hand out a
 * printout and project the same problems on the board.
 */
async function resolveItems(standard: string, skillId: string, session: 1 | 2): Promise<ResolvedItems | null> {
  const scriptPath = path.join(process.cwd(), "..", "engine", "generate_skill_packet.py");
  const projectRoot = path.join(process.cwd(), "..");
  const payload = JSON.stringify({ standard, skill_id: skillId, session, mode: "items" });
  return new Promise<ResolvedItems | null>((resolve) => {
    const child = execFile(
      PYTHON_PATH,
      [scriptPath],
      { cwd: projectRoot, timeout: 20_000 },
      (err, stdout) => {
        if (err) {
          resolve(null);
          return;
        }
        try {
          resolve(JSON.parse(stdout.trim()) as ResolvedItems);
        } catch {
          resolve(null);
        }
      }
    );
    child.stdin?.write(payload);
    child.stdin?.end();
  });
}

export async function generateStaticParams() {
  // Skip prerendering — the projection runs the Python generator at request
  // time so items always match what the packet would print right now. Static
  // params would freeze the items at build time.
  return [];
}

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ skill_id: string }>;
}): Promise<Metadata> {
  const { skill_id } = await params;
  const all = await loadAllSkills();
  const found = all.find((s) => s.skill_id === skill_id);
  if (!found) return { title: "Skill Not Found | Plug N Play" };
  return {
    title: `${found.skill.name} (Project) | Plug N Play`,
    description: `Project ${found.skill.name} for ${found.standard_code}`,
  };
}

export default async function SkillProjectPage({
  params,
  searchParams,
}: {
  params: Promise<{ skill_id: string }>;
  searchParams: Promise<{ session?: string }>;
}) {
  const { skill_id } = await params;
  const sp = await searchParams;
  const session: 1 | 2 = sp.session === "2" ? 2 : 1;

  const all = await loadAllSkills();
  const found = all.find((s) => s.skill_id === skill_id);
  if (!found) notFound();
  const { skill, standard_code } = found;

  // Pull the same items the packet generator would print. Forward the
  // diagram metadata (render_data, choices_render, parts) so the runner
  // can render real number lines / coordinate grids instead of text.
  const resolved = await resolveItems(standard_code, skill_id, session);
  const items = (resolved?.items ?? []).map((it) => ({
    stem: it.stem,
    answer: it.answer,
    choices: it.choices,
    section: it.section,
    render_data: it.render_data ?? undefined,
    choices_render: it.choices_render ?? undefined,
    parts: it.parts ?? undefined,
    type: it.type ?? undefined,
    shown_work: it.shown_work ?? undefined,
  }));

  return (
    <SkillProjectionRunner
      skillId={skill.skill_id}
      skillName={skill.name}
      standardCode={standard_code}
      session={session}
      items={items}
      artifact={skill.printable_artifact}
      fluency={resolved?.fluency ?? undefined}
      workedSolution={resolved?.worked_solution ?? undefined}
      fadedExample={resolved?.faded_example ?? undefined}
      sentenceStarters={resolved?.sentence_starters ?? undefined}
      teacherGuide={{
        i_do_script: skill.i_do_script,
        worked_example_script: skill.worked_example_script,
        canonical_error: skill.canonical_error,
        redirect_script: skill.redirect_script,
        sentence_starters: skill.sentence_starters,
      }}
    />
  );
}
