import Button from "@/components/ui/Button";

export default function EmptyState({ onReset }: { onReset: () => void }) {
  return (
    <div className="flex flex-col items-center py-20 text-center">
      <svg
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="mb-4 text-pnp-gray-300"
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
        <line x1="8" y1="11" x2="14" y2="11" />
      </svg>
      <h3 className="font-heading text-xl font-bold text-pnp-navy">
        No strategies match those filters
      </h3>
      <p className="mt-2 max-w-sm text-sm text-pnp-gray-600">
        Loosen a filter or clear them all to see every strategy again.
      </p>
      <div className="mt-6">
        <Button tier="secondary" onClick={onReset}>
          Clear all filters
        </Button>
      </div>
    </div>
  );
}
