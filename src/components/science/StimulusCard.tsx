import type { Stimulus } from "@/lib/library/science";
import Figure from "./Figure";
import QuestionList from "./QuestionList";

/** One phenomenon cluster on screen: numbered header, phenomenon, figure,
 *  interactive items. (Printing is handled by StimulusPrintModal.) */
export default function StimulusCard({
  stimulus,
  index,
  accent,
}: {
  stimulus: Stimulus;
  index: number;
  accent: string;
}) {
  return (
    <article className="overflow-hidden rounded-2xl border-2 border-[var(--pnp-navy)] bg-white shadow-[4px_4px_0_var(--pnp-navy)]">
      <div className="h-1.5" style={{ background: accent }} aria-hidden />
      <header className="flex items-center gap-3 bg-[var(--pnp-navy)] px-6 py-3 sm:px-8">
        <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-white text-sm font-bold text-[var(--pnp-navy)]">
          {index}
        </span>
        <h3 className="font-heading text-lg font-extrabold text-white">
          {stimulus.title}
        </h3>
      </header>
      <div className="px-6 py-5 sm:px-8 sm:py-7">
        <p className="whitespace-pre-line text-[15px] leading-relaxed text-[var(--pnp-gray-800)]">
          {stimulus.phenomenon}
        </p>
        <Figure figure={stimulus.figure} />
        <QuestionList questions={stimulus.questions} />
      </div>
    </article>
  );
}
