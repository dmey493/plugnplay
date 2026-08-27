export const dynamic = "force-dynamic";

import { getAllStrategies } from "@/lib/library/strategies";

export async function GET() {
  try {
    const all = await getAllStrategies();
    const interventionStrategies = all
      .filter(
        (s) =>
          s.subjects.includes("math") &&
          s.tags.includes("intervention-strategy")
      )
      .map((s) => ({
        id: s.id,
        title: s.title,
        summary: s.preview,
      }));

    return Response.json({ strategies: interventionStrategies });
  } catch (e) {
    return Response.json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      { status: 500 }
    );
  }
}
