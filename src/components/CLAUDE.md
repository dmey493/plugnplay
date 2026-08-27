# src/components

One folder per feature, named for the feature. There is no `math/` bucket; math
features are top level (`intervention/`, `generator/`, `wodb/`, `number-talks/`,
`thin-slices/`, `units/`, `tasks/`).

## Shared across features

- `standards/StandardPicker.tsx` is used by BOTH `intervention/` and
  `generator/`. That is why it is not inside either.
- `projection/` (`DrawingOverlay`, `InlineMath`) is used by `intervention/`,
  `tasks/ProjectionView`, and `thin-slices/ThinSliceRunner`.
- `ui/`, `layout/`, `sections/` are generic building blocks.

## Currently unwired

`intervention/SkillDetail.tsx` and `intervention/SkillProjectionRunner.tsx` have
no importers. The intervention card was simplified to a single action (click
prints a worksheet), which took the detail and projection routes offline. The
components were left in place, not deleted.
