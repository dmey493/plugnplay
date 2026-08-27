import fs from "fs";
import path from "path";
import type { ContentEnvelope } from "@/lib/core/types";

const THIN_SLICE_DIR = path.join(process.cwd(), "content", "thin-slices");
const SUBJECT_DIRS = ["math", "science"];

/**
 * Read all thin-slice JSONs from content/thin-slices/{subject}/. A "thin slice"
 * is a ContentEnvelope where type === "thin-slice".
 *
 * Server-only — uses Node's fs module. Do not import this from client components.
 */
export async function getAllThinSlices(): Promise<ContentEnvelope[]> {
  const out: ContentEnvelope[] = [];

  for (const subject of SUBJECT_DIRS) {
    const dir = path.join(THIN_SLICE_DIR, subject);
    if (!fs.existsSync(dir)) continue;

    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    for (const file of files) {
      const raw = fs.readFileSync(path.join(dir, file), "utf-8");
      const parsed = JSON.parse(raw) as ContentEnvelope;
      if (parsed.type === "thin-slice") {
        out.push(parsed);
      }
    }
  }

  return out.sort((a, b) => a.title.localeCompare(b.title));
}

export async function getThinSliceById(
  id: string
): Promise<ContentEnvelope | undefined> {
  const all = await getAllThinSlices();
  return all.find((t) => t.id === id);
}
