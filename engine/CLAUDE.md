# web/engine

The Python PDF engine. This is the **only** live engine. It ships inside the app
image, so `process.cwd()` is `web/` at runtime and paths resolve from there.

Stale forks exist in `authoring/execution/` and
`_archive/engine-standalone-stale/`. Do not edit those.

## Two entry points, two pipelines

**Intervention** (renders pre-authored content):
- `generate_skill_packet.py` printable Tier 2 packet
- `generate_diagnostic.py` diagnostic sheet
- `generate_placement_sheet.py` placement sheet
- all read `content/skills/<STD>.json`

**Generators** (builds problems on demand):
- `generate_pdf_api.py` API entry, called by `src/lib/generators/engine.ts`
- `generate_worksheet.py` worksheet assembly
- `number_generators.py` the numbers
- `context_pools.py` word-problem contexts
- `stems/stem_<STD>.py` per-standard problem templates
- `distractor_engine.py` plausible wrong answers
- `answer_validator.py` answer checking

**Shared:** `pdf_generator.py` (layout, 233 KB) and `svg_helpers.py` (diagrams,
95 KB) are used by both.

## Authoring and validation

- `agents/author_skill.py` drives the 5-gate skill authoring pipeline against
  `authoring/data/skills/`. Run it from the project root.
- `validate_content.py` gates the content and enforces that
  `authoring/data/skills/` and `web/content/skills/` stay byte-identical.
- `check_representations.py` checks concrete representations per skill.

Both locate the project root by walking up from `__file__` looking for
`authoring/data/skills`. A fixed parent count breaks here; do not reintroduce one.
