import { execFile } from "child_process";
import { readFile, unlink } from "fs/promises";
import path from "path";

const PYTHON_PATH =
  process.env.PYTHON_PATH ??
  "C:/Users/meyedl01/AppData/Local/Python/pythoncore-3.14-64/python.exe";

// The Python engine ships in the repo at ./engine, so it deploys with the app.
// process.cwd() is the app root in dev (`next dev` from web/) and in production
// (`next start` / the Docker image's WORKDIR).
const PROJECT_ROOT = process.cwd();
const REVIEW_SCRIPT = path.join(PROJECT_ROOT, "engine", "review_api.py");
const GENERATE_SCRIPT = path.join(PROJECT_ROOT, "engine", "generate_pdf_api.py");
const SPIRAL_SCRIPT = path.join(PROJECT_ROOT, "engine", "spiral_api.py");

// Python salts str hashes per process, and several stems (and the distractor
// engine) build sets of strings. Without a fixed seed the same (standard, seed)
// comes back with different choices in the next process, so a preview stops
// matching its PDF.
const PYTHON_ENV = {
  ...process.env,
  PYTHONHASHSEED: "0",
  PYTHONIOENCODING: "utf-8",
};

export interface PythonCallOptions {
  timeoutMs?: number;
  signal?: AbortSignal;
}

export async function callPython(
  script: string,
  input: Record<string, unknown>,
  opts: PythonCallOptions = {}
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = execFile(
      PYTHON_PATH,
      [script],
      {
        cwd: PROJECT_ROOT,
        timeout: opts.timeoutMs ?? 30000,
        maxBuffer: 10 * 1024 * 1024,
        env: PYTHON_ENV,
        signal: opts.signal,
      },
      (error, stdout, stderr) => {
        if (error) {
          reject(new Error(stderr || error.message));
          return;
        }
        resolve(stdout.trim());
      }
    );
    child.stdin?.write(JSON.stringify(input));
    child.stdin?.end();
  });
}

export async function callReviewApi(
  params: Record<string, unknown>
): Promise<Record<string, unknown>> {
  const result = await callPython(REVIEW_SCRIPT, params);
  return JSON.parse(result);
}

export async function generatePdf(
  params: Record<string, unknown>
): Promise<Uint8Array> {
  const result = await callPython(GENERATE_SCRIPT, params);
  const parsed = JSON.parse(result);
  if (parsed.error) throw new Error(parsed.error);
  const buffer = await readFile(parsed.path);
  unlink(parsed.path).catch(() => {});
  return new Uint8Array(buffer);
}

export async function generateReviewPdf(
  params: Record<string, unknown>
): Promise<Uint8Array> {
  const result = await callReviewApi({ ...params, action: "review-pdf" });
  if ("error" in result) throw new Error(result.error as string);
  const pdfPath = result.path as string;
  const buffer = await readFile(pdfPath);
  unlink(pdfPath).catch(() => {});
  return new Uint8Array(buffer);
}

// Spiral review mixes several standards on one sheet, so it has its own script
// (engine/spiral_api.py). A multi-week build measures every problem before it
// draws, which takes longer than the single-standard review calls.

// The engine answers {error, message}: "bad_request" and "no_candidates" are
// things the teacher can fix, "engine_error" is ours.
export function spiralErrorStatus(error: unknown): number {
  return error === "engine_error" ? 500 : 400;
}

export async function callSpiralApi(
  params: Record<string, unknown>,
  opts: PythonCallOptions = {}
): Promise<Record<string, unknown>> {
  const result = await callPython(SPIRAL_SCRIPT, params, {
    timeoutMs: 60000,
    ...opts,
  });
  return JSON.parse(result);
}

export async function generateSpiralPdf(
  params: Record<string, unknown>,
  opts: PythonCallOptions = {}
): Promise<{ pdf: Uint8Array; report: Record<string, unknown> }> {
  const result = await callSpiralApi(
    { ...params, action: "spiral-pdf" },
    { timeoutMs: 90000, ...opts }
  );
  if ("error" in result) {
    throw Object.assign(new Error(String(result.message ?? result.error)), {
      status: spiralErrorStatus(result.error),
    });
  }
  const pdfPath = result.path as string;
  const buffer = await readFile(pdfPath);
  unlink(pdfPath).catch(() => {});
  return {
    pdf: new Uint8Array(buffer),
    report: (result.report as Record<string, unknown>) ?? {},
  };
}
