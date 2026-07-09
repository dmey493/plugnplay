import fs from "fs";
import path from "path";
import type { ContentEnvelope } from "./types";

// Re-export pure helpers for any caller that already imports from tasks.ts.
// Server-only filesystem code lives below.
export { filterTasks, collectConcepts, collectStandards, durationBucketFor } from "./tasks-filter";

const TASKS_DIR = path.join(process.cwd(), "content", "tasks");
const SUBJECT_DIRS = ["math", "science"];

/**
 * Read all task JSONs from content/tasks/{subject}/. A "task" is a
 * ContentEnvelope where type === "task". Skips anything else.
 *
 * Server-only — uses Node's fs module. Do not import this from client components.
 */
export async function getAllTasks(): Promise<ContentEnvelope[]> {
  const tasks: ContentEnvelope[] = [];

  for (const subject of SUBJECT_DIRS) {
    const dir = path.join(TASKS_DIR, subject);
    if (!fs.existsSync(dir)) continue;

    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    for (const file of files) {
      const raw = fs.readFileSync(path.join(dir, file), "utf-8");
      const parsed = JSON.parse(raw) as ContentEnvelope;
      if (parsed.type === "task") {
        tasks.push(parsed);
      }
    }
  }

  return tasks.sort((a, b) => a.title.localeCompare(b.title));
}

export async function getTaskById(
  id: string
): Promise<ContentEnvelope | undefined> {
  const all = await getAllTasks();
  return all.find((t) => t.id === id);
}
