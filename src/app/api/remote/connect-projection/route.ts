export const dynamic = "force-dynamic";

import type {
  ConnectProjectionResponse,
  ProjectionState,
  RemoteTaskBundle,
  TaskBody,
} from "@/lib/core/types";
import { getTaskById } from "@/lib/library/tasks";
import { parsePrompt } from "@/lib/generators/split-prompt";
import { createRoom } from "@/lib/classroom/remote-store";

/**
 * Projection-side handshake. Called once when the teacher clicks Connect
 * on the projection. Builds the task bundle (parsed prompt + reference
 * fields) and mints a fresh room, returning the public code + the
 * projection's secret token.
 *
 * Body: `{ taskId: string, initialState: ProjectionState }`
 * Returns: `{ code, projectionToken }`
 */
export async function POST(request: Request) {
  try {
    const body = (await request.json()) as {
      taskId?: unknown;
      initialState?: unknown;
    };

    const taskId = typeof body.taskId === "string" ? body.taskId : null;
    if (!taskId) {
      return Response.json({ error: "Missing taskId" }, { status: 400 });
    }

    const task = await getTaskById(taskId);
    if (!task) {
      return Response.json({ error: "Task not found" }, { status: 404 });
    }
    const taskBody = task.body as TaskBody;
    const parsed = parsePrompt(taskBody.studentPrompt);

    const taskBundle: RemoteTaskBundle = {
      taskId: task.id,
      title: task.title,
      intro: parsed.intro,
      questions: parsed.questions,
      discussionQuestions: taskBody.discussionQuestions,
      anticipatedApproaches: taskBody.anticipatedApproaches,
      commonMisconceptions: taskBody.commonMisconceptions,
      sampleSolutions: taskBody.sampleSolutions,
      extensions: taskBody.extensions,
    };

    // We trust the projection to supply its own current state — that way
    // a teacher who connects mid-session doesn't reset back to question 1.
    // If the body is malformed we synthesise a safe default.
    const initialState: ProjectionState =
      isProjectionState(body.initialState)
        ? body.initialState
        : {
            taskId: task.id,
            totalQuestions: parsed.questions.length,
            revealedCount: 1,
            windowSize: 2,
            themeId: "underwater",
            drawing: false,
            timer: {
              visible: false,
              durationSec: 300,
              remainingSec: 300,
              running: false,
            },
          };

    const { code, projectionToken } = createRoom(taskBundle, initialState);
    const response: ConnectProjectionResponse = { code, projectionToken };
    return Response.json(response);
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}

/** Lightweight shape check — `ProjectionState` is a JSON-serialisable
 *  record so we just confirm the required top-level keys are present
 *  and the right type. Anything more would be defensive overkill for
 *  data we ourselves emit. */
function isProjectionState(value: unknown): value is ProjectionState {
  if (!value || typeof value !== "object") return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.taskId === "string" &&
    typeof v.totalQuestions === "number" &&
    typeof v.revealedCount === "number" &&
    typeof v.themeId === "string"
  );
}
