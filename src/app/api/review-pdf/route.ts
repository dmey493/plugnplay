export const dynamic = "force-dynamic";
import { generateReviewPdf } from "@/lib/engine";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const pdfBuffer = await generateReviewPdf(body);
    const standard = ((body.standard as string) ?? "worksheet").replace(/\./g, "_");
    const fmt = (body.format as string) ?? "exit_ticket";
    return new Response(pdfBuffer.buffer as ArrayBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `inline; filename="PlugNPlay_${standard}_${fmt}.pdf"`,
      },
    });
  } catch (e) {
    return Response.json({ error: e instanceof Error ? e.message : "Unknown error" }, { status: 500 });
  }
}
