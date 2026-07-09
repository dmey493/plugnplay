# Plug N Play

A ready-to-teach toolkit for middle-school teachers. Pick a subject or a tool and
jump straight into standards-aligned lesson activities, exit tickets, warm-up
routines, and teaching strategies for grades 6–8 — browse, project to the board,
or print in one click. Everything maps to Indiana Academic Standards.

## What's inside

**Math**
- **Lesson activities** — rich tasks and thin slices for thinking classrooms, browsable by unit, standard, or concept.
- **Exit tickets** — a standards-aligned problem generator (exit tickets, tiered Mild/Medium/Spicy sets, proficiency checks).
- **Fluency practice** — printable fluency worksheets across the core 6–8 skills.
- **Skill intervention** — Tier 2 learning progressions per standard, with diagnostics and printable packets.
- **Warm-up routines** — Which One Doesn't Belong? and Number Talks.
- **Classroom tools** — full-screen whiteboard and voice-powered flash cards.

**Science**
- **Graph of the Week** — a weekly graph-analysis routine for grades 6–8; pick a grade and standard, then a phenomenon graph students analyze and write a claim–evidence–reasoning response about. Print-ready front and back.
- **Stimulus generator** — ILEARN End-of-Course–style biology (HS-LS) phenomenon stimuli with charts/data tables and auto-scorable items.

**Strategies library** — teaching strategies filterable by subject, purpose, and MTSS tier.

## Tech stack

- [Next.js 16](https://nextjs.org) (App Router, React Server Components)
- React 19
- Tailwind CSS v4
- TypeScript

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Other scripts:

```bash
npm run build   # production build
npm run start   # serve the production build
npm run lint    # eslint
```

## Deploying

The site deploys to any Next.js host. The easiest path is [Vercel](https://vercel.com):
import this repository and it builds and hosts automatically on every push.

> Note: a few PDF-generation API routes shell out to a local Python engine (via a
> `PYTHON_PATH` environment variable). The full site — lesson activities, the
> Graph of the Week, WODB, number talks, fluency, and browsing — runs without it;
> only those specific server-side PDF generators require the Python backend.

## License

All rights reserved unless stated otherwise.
