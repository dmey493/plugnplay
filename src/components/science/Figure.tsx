import type { Figure as FigureData } from "@/lib/science";
import Chart from "./Chart";

/** Renders a cluster figure: a rendered chart, a data table, or the one
 *  bundled image. `kind: "none"` renders nothing. */
export default function Figure({ figure }: { figure?: FigureData }) {
  if (!figure || figure.kind === "none") return null;

  if (figure.kind === "chart") return <Chart figure={figure} />;

  if (figure.kind === "table") {
    const cols = figure.columns ?? [];
    const rows = figure.rows ?? [];
    return (
      <figure className="my-4">
        <div className="overflow-x-auto rounded-lg border border-[var(--pnp-gray-200)]">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-[var(--pnp-gray-50)] text-left">
                {cols.map((c, i) => (
                  <th key={i} className="border-b border-[var(--pnp-gray-200)] px-3 py-2 font-semibold text-[var(--pnp-navy)]">
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, ri) => (
                <tr key={ri} className="odd:bg-white even:bg-[var(--pnp-gray-50)]/50">
                  {r.map((cell, ci) => (
                    <td key={ci} className="border-b border-[var(--pnp-gray-100)] px-3 py-2 text-[var(--pnp-gray-800)]">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {(figure.caption || figure.source) && (
          <figcaption className="mt-1.5 text-xs text-[var(--pnp-gray-500)]">
            {figure.caption}
            {figure.source ? ` ${figure.source}` : ""}
          </figcaption>
        )}
      </figure>
    );
  }

  if (figure.kind === "image" && figure.file) {
    return (
      <figure className="my-4 text-center">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={`/science/${figure.file}`}
          alt={figure.caption ?? "Figure"}
          className="mx-auto h-auto max-h-80 w-auto max-w-full rounded-lg border border-[var(--pnp-gray-200)]"
        />
        {figure.caption && (
          <figcaption className="mt-1.5 text-xs text-[var(--pnp-gray-500)]">
            {figure.caption}
          </figcaption>
        )}
      </figure>
    );
  }

  return null;
}
