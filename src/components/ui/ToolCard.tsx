import Link from "next/link";

const ICONS: Record<string, React.ReactNode> = {
  book: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
      <path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15z" />
    </svg>
  ),
  calculator: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="2" width="16" height="20" rx="2" />
      <line x1="8" y1="6" x2="16" y2="6" />
      <line x1="8" y1="10" x2="8" y2="10.01" />
      <line x1="12" y1="10" x2="12" y2="10.01" />
      <line x1="16" y1="10" x2="16" y2="10.01" />
      <line x1="8" y1="14" x2="8" y2="14.01" />
      <line x1="12" y1="14" x2="12" y2="14.01" />
      <line x1="16" y1="14" x2="16" y2="14.01" />
      <line x1="8" y1="18" x2="16" y2="18" />
    </svg>
  ),
  clipboard: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2" />
      <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
      <path d="M9 12h6M9 16h6" />
    </svg>
  ),
  layers: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 2 7 12 12 22 7 12 2" />
      <polyline points="2 17 12 22 22 17" />
      <polyline points="2 12 12 17 22 12" />
    </svg>
  ),
};

export default function ToolCard({
  title,
  description,
  href,
  active,
  icon,
}: {
  title: string;
  description: string;
  href: string;
  active: boolean;
  icon: string;
}) {
  const content = (
    <div
      className={`relative flex h-full flex-col rounded-2xl border p-6 transition-all ${
        active
          ? "border-pnp-gray-200 bg-white shadow-sm hover:shadow-md hover:border-pnp-yellow"
          : "border-pnp-gray-200 bg-pnp-gray-50"
      }`}
    >
      {!active && (
        <div className="absolute inset-0 z-10 flex items-center justify-center rounded-2xl bg-white/60 backdrop-blur-[1px]">
          <span className="rounded-full bg-pnp-gray-900 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-white">
            Coming Soon
          </span>
        </div>
      )}

      <div
        className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl ${
          active ? "bg-pnp-yellow/20 text-pnp-navy" : "bg-pnp-gray-200 text-pnp-gray-500"
        }`}
      >
        {ICONS[icon] ?? ICONS.book}
      </div>

      <h3 className="font-heading text-lg font-bold text-pnp-gray-900">
        {title}
      </h3>
      <p className="mt-2 flex-1 text-sm leading-relaxed text-pnp-gray-500">
        {description}
      </p>

      {active && (
        <span className="mt-4 inline-flex items-center text-sm font-semibold text-pnp-blue">
          Open
          <svg
            width="15"
            height="13"
            viewBox="0 0 15 13"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="ml-1.5"
          >
            <path d="M1 6.5h12M8.5 1l5.5 5.5-5.5 5.5" />
          </svg>
        </span>
      )}
    </div>
  );

  if (active) {
    return (
      <Link href={href} className="block">
        {content}
      </Link>
    );
  }

  return content;
}
