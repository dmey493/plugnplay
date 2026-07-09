export const dynamic = "force-dynamic";

import { execFile } from "child_process";
import { readFile, unlink } from "fs/promises";
import path from "path";

const PYTHON_PATH =
  process.env.PYTHON_PATH ??
  "C:/Users/meyedl01/AppData/Local/Python/pythoncore-3.14-64/python.exe";

const SCRIPT_PATH = path.join(process.cwd(), "..", "engine", "generate_skill_packet.py");
const PROJECT_ROOT = path.join(process.cwd(), "..");

/**
 * Generates a skill intervention packet PDF.
 *
 * The Python generator takes: standard, skill_id, student_copies,
 * include_teacher_companion. Pedagogical guidance now comes from a single
 * optional `coaching_note` field on the skill JSON itself — no per-question
 * Strategy Tip injection from the API. (A previous version forwarded
 * `strategy_ids` and resolved them server-side; that's gone.)
 */
export async function POST(request: Request) {
  try {
    const body = await request.json();

    const result = await new Promise<string>((resolve, reject) => {
      const child = execFile(
        PYTHON_PATH,
        [SCRIPT_PATH],
        { cwd: PROJECT_ROOT, timeout: 30000 },
        (error, stdout, stderr) => {
          if (error) {
            reject(new Error(stderr || error.message));
            return;
          }
          resolve(stdout.trim());
        }
      );
      child.stdin?.write(JSON.stringify(body));
      child.stdin?.end();
    });

    const parsed = JSON.parse(result);
    if (parsed.error) {
      return Response.json({ error: parsed.error }, { status: 400 });
    }

    const pdfBuffer = await readFile(parsed.path);
    unlink(parsed.path).catch(() => {});

    const skillId = (body.skill_id as string) ?? "skill";
    return new Response(new Uint8Array(pdfBuffer).buffer as ArrayBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `inline; filename="PlugNPlay_${skillId}.pdf"`,
      },
    });
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
