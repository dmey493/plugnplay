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

## PDF engine

Two API routes — the skill-intervention **packet** and the math **diagnostic** —
generate PDFs with a small Python engine in [`engine/`](engine) (`fpdf2` +
`drawsvg`, no secrets, no network calls). Everything else in the app is pure
Node/React. The routes call Python via the `PYTHON_PATH` environment variable
(defaults to a local Windows path for development; set it to `python3` on Linux).

Run the engine locally:

```bash
pip install -r requirements.txt   # fpdf2, drawsvg
```

## Deploying

Because of the Python PDF engine, deploy on a host that runs **both Node and
Python**. A [`Dockerfile`](Dockerfile) is included that installs both, builds the
app, and serves it — deploy it on any container host (**Render**, **Railway**,
**Fly.io**, or a VPS):

1. Push this repo to GitHub.
2. Create a new **Web Service** on your host and point it at the repo.
3. Choose the **Docker** environment (it auto-detects the `Dockerfile`). No build
   command needed.
4. Deploy — the host builds the image and gives you a public URL.

> Vercel's default runtime is Node-only and can't run the Python engine, so the
> two PDF routes won't work there. If you deploy to Vercel, the rest of the site
> (lesson activities, Graph of the Week, WODB, Number Talks, fluency, browsing)
> still works — only the packet/diagnostic PDF downloads need the container host.

## License

All rights reserved unless stated otherwise.
