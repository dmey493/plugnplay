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

export async function callPython(
  script: string,
  input: Record<string, unknown>
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = execFile(
      PYTHON_PATH,
      [script],
      { cwd: PROJECT_ROOT, timeout: 30000 },
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
