export const dynamic = "force-dynamic";

import { execFile } from "child_process";
import { readFile, unlink } from "fs/promises";
import path from "path";

const PYTHON_PATH =
  process.env.PYTHON_PATH ??
  "C:/Users/meyedl01/AppData/Local/Python/pythoncore-3.14-64/python.exe";

// The Python PDF engine ships in the repo at ./engine, so it deploys with
// the app. process.cwd() is the app root in dev (`next dev` from web/) and in
// production (`next start` / the Docker image's WORKDIR).
const SCRIPT_PATH = path.join(process.cwd(), "engine", "generate_diagnostic.py");
const PROJECT_ROOT = process.cwd();

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

    const standard = ((body.standard as string) ?? "diagnostic").replace(/\./g, "_");
    const mode = (body.mode as string) ?? "diagnostic";
    return new Response(new Uint8Array(pdfBuffer).buffer as ArrayBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `inline; filename="PlugNPlay_${standard}_${mode}.pdf"`,
      },
    });
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
