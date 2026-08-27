export const dynamic = "force-dynamic";
import { callReviewApi } from "@/lib/generators/engine";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const result = await callReviewApi({ ...body, action: "review-generate" });
    return Response.json(result);
  } catch (e) {
    return Response.json({ error: e instanceof Error ? e.message : "Unknown error" }, { status: 500 });
  }
}
