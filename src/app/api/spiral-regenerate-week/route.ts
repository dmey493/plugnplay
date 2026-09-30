export const dynamic = "force-dynamic";
import { callSpiralApi, spiralErrorStatus } from "@/lib/generators/engine";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const result = await callSpiralApi(
      { ...body, action: "spiral-regenerate-week" },
      { signal: request.signal }
    );
    const status = "error" in result ? spiralErrorStatus(result.error) : 200;
    return Response.json(result, { status });
  } catch (e) {
    return Response.json(
      { error: "engine_error", message: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
