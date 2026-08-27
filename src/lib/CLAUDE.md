# src/lib

Data layer, grouped by domain. Import across groups with `@/lib/<group>/<module>`.

| Folder | Contains | Reads from |
|---|---|---|
| `core/` | `types.ts`, `constants.ts` | nothing |
| `standards/` | `standards.ts`, `standards-labels.ts`, `checkpoints.ts` | `content/checkpoints/` |
| `intervention/` | `skills.ts` | `content/skills/` (69 JSONs) |
| `generators/` | `fluency-gen.ts`, `wodb-render.ts`, `split-prompt.ts`, `engine.ts` | nothing, builds on demand |
| `library/` | tasks, units, lessons, thin-slices, wodb, number-talks, approach, gotw, science, strategies | `content/` |
| `classroom/` | classes, lesson-plans, activity-types, remote-*, projection-themes | `localStorage` |

Rule of thumb: `library/` loads pre-built content off disk, `classroom/` holds
per-teacher browser state, `generators/` produces problems from nothing,
`intervention/` is the Tier 2 skill spine.

## Notes

- `core/types.ts` is imported by ~29 modules. Changing it is wide-reaching.
- `generators/engine.ts` spawns Python from `web/engine/`. Server-only.
- `intervention/skills.ts` `require()`s all 69 skill JSONs with relative paths
  (`../../../content/skills/...`). `tsc` will not catch a broken path here if
  `tsconfig.tsbuildinfo` is stale. Run `npx next build` after moving this file.
- `library/strategies.ts` was named `content.ts`; it loads teaching strategies.
