# Pre-existing components (declared)

This repository extends **Assisted Vessel AI**, an independent prototype built before the Open Agent Hackathon 2026.
All code at git tag `pre-hackathon-baseline` (commit 84b68f2) is pre-existing and is **not** submitted as hackathon work.

## Pre-existing (before 22 Oct 2026, 00:00 UTC)
- `packages/app` – browser UI (Vite/TypeScript)
- `packages/core-domain` – domain types
- `packages/decision-engine` – deterministic decision logic
- `packages/safety-engine` – Safety/ODD engine and L0–L4 assistance levels
- `packages/simulator` – synthetic vessel telemetry
- `packages/assurance` – assurance checks
- `docs/`, `.github/workflows/`, `.claude/agents/` – documentation, CI and dev tooling

## New hackathon work (after the tag)
Everything committed after `pre-hackathon-baseline`, including the Zetaris data layer, the multi-agent service, the Meterless engine integrations and the new investigation UI. See the git history: `git log pre-hackathon-baseline..HEAD`.