export const dynamic = "force-dynamic";
import { generateSpiralPdf } from "@/lib/generators/engine";

// The fit report (pages per week, problems to swap) rides along in a header so
// the body can stay a plain PDF the browser previews and downloads directly.
const MAX_REPORT_WARNINGS = 20;

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { pdf, report } = await generateSpiralPdf(body, { signal: request.signal });

    const warnings = Array.isArray(report.warnings) ? report.warnings : [];
    const header = encodeURIComponent(
      JSON.stringify({ ...report, warnings: warnings.slice(0, MAX_REPORT_WARNINGS) })
    );
    const weeks = (Array.isArray(body.weeks) ? body.weeks : []) as { week_number: number }[];
    const numbers = weeks.map((w) => Number(w.week_number)).filter(Number.isFinite);
    const range =
      numbers.length > 1
        ? `Weeks_${Math.min(...numbers)}-${Math.max(...numbers)}`
        : `Week_${numbers[0] ?? 1}`;
    const grade = Number(body.grade) || "";

    return new Response(pdf.buffer as ArrayBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `inline; filename="PlugNPlay_Spiral_Review_Grade${grade}_${range}.pdf"`,
        "X-Spiral-Report": header,
      },
    });
  } catch (e) {
    const status = (e as { status?: number }).status ?? 500;
    return Response.json(
      {
        error: status === 500 ? "engine_error" : "bad_request",
        message: e instanceof Error ? e.message : "Unknown error",
      },
      { status }
    );
  }
}
