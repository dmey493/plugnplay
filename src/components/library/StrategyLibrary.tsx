"use client";

import { useState, useCallback } from "react";
import type { ContentEnvelope, FilterState } from "@/lib/types";
import { filterStrategies } from "@/lib/content-filter";
import FilterBar from "./FilterBar";
import StrategyCard from "./StrategyCard";
import EmptyState from "./EmptyState";

const INITIAL_FILTERS: FilterState = {
  subjects: [],
  grades: [],
  purposes: [],
  mtssTiers: [],
  search: "",
};

export default function StrategyLibrary({
  strategies,
}: {
  strategies: ContentEnvelope[];
}) {
  const [filters, setFilters] = useState<FilterState>(INITIAL_FILTERS);

  const filtered = filterStrategies(strategies, filters);

  const handleReset = useCallback(() => {
    setFilters(INITIAL_FILTERS);
  }, []);

  return (
    <div>
      <FilterBar
        filters={filters}
        onChange={setFilters}
        resultCount={filtered.length}
      />

      {filtered.length === 0 ? (
        <EmptyState onReset={handleReset} />
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((strategy) => (
            <StrategyCard key={strategy.id} strategy={strategy} />
          ))}
        </div>
      )}
    </div>
  );
}
