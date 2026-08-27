import type { TaskImage } from "@/lib/core/types";
import InteractiveImage from "./interactive/InteractiveImage";

interface Props {
  image: TaskImage;
  /** Sizing context. "detail" sits inside The Task box, "project" is the
   *  big classroom display, "card" is small thumbnail. */
  size?: "detail" | "project" | "card";
  className?: string;
  /** Theme for projection mode — flips inline SVG colors to look right on dark. */
  theme?: "light" | "dark";
}

/**
 * Renders either:
 *   1. Inline SVG (preferred). The SVG markup is sanitized at author time
 *      and authored by us, so we trust it. Container scales it responsively.
 *   2. An external URL with a credit caption.
 *
 * If neither is provided, renders nothing.
 */
export default function TaskImageView({
  image,
  size = "detail",
  className = "",
  theme = "light",
}: Props) {
  const isInteractive = image?.kind === "interactive" && image.component;
  if (!image || (!isInteractive && !image.svg && !image.url)) return null;

  // Each context defines BOTH the figure container's max-height and the
  // direct `max-h-*` we apply to the <img> itself. `max-h-full` on the img
  // doesn't clamp inside a flex container without an explicit height, so
  // the photo grows to its natural size and pushes the prompt off-screen.
  // Hard-pinning the img's max-h fixes it.
  const sizeClasses = {
    card: "max-h-32",
    detail: "max-h-56",          // shrunk so prompt text stays in view
    project: "max-h-[40vh]",
  }[size];
  const imgMaxHClass = {
    card: "max-h-32",
    detail: "max-h-56",
    project: "max-h-[40vh]",
  }[size];
  // The inline SVG needs a DEFINITE max-height (in px/vh), not `max-h-full`:
  // this figure's container only has a MAX height with an auto real height, so
  // a percentage cap resolves against nothing and the SVG balloons. A concrete
  // cap + h-auto scales the shape by its aspect ratio and never overflows.
  const svgMaxHClass = {
    card: "[&>svg]:max-h-32",
    detail: "[&>svg]:max-h-56",
    project: "[&>svg]:max-h-[40vh]",
  }[size];

  return (
    <figure className={`flex flex-col items-center ${className}`}>
      <div
        className={`flex w-full items-center justify-center ${sizeClasses}`}
        aria-label={image.alt}
        role="img"
      >
        {isInteractive && image.component ? (
          // Fill the available height while keeping square aspect, so the
          // 3D scene scales with whatever box the parent gave us.
          <div className="aspect-square h-full">
            <InteractiveImage component={image.component} />
          </div>
        ) : image.svg ? (
          <div
            data-task-image-svg
            data-theme={theme}
            className={`task-image-svg flex w-full items-center justify-center [&>svg]:h-auto [&>svg]:w-auto [&>svg]:max-w-full ${svgMaxHClass}`}
            // Inline SVG is authored by us in the task JSONs. We treat it as trusted.
            dangerouslySetInnerHTML={{ __html: image.svg }}
          />
        ) : image.url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={image.url}
            alt={image.alt}
            className={`${imgMaxHClass} w-auto max-w-full rounded-lg object-contain`}
          />
        ) : null}
      </div>
      {image.credit && (
        <figcaption className="mt-2 text-xs italic text-pnp-gray-500">
          {image.credit}
        </figcaption>
      )}
    </figure>
  );
}
