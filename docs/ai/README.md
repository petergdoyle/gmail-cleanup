---
title: AI-IDE Working Model — Reusable Template
---

# Working With an AI Agent — The Model (Reusable Template)

This is a **portable, project-agnostic description of how to build software with
an agentic AI IDE.** It is written to be **copied wholesale into any new
agentic-AI-supported project** — drop this folder in, adjust the few
tooling-specific lines it calls out, and it becomes that project's canonical
working model.

It makes **no assumptions about language, framework, or domain.** Wherever a
specific tool or platform would normally appear (an issue tracker, a docs
publisher, a git host, a CI system), this template refers to it by *role* and
tells you where to substitute your own.

It rests on two convictions that hold regardless of stack:

- **Human agency is the point.** Humans conceive, verify, and decide; the AI does
  the work under human guidance. The agent never plans, implements, and verifies
  in a closed loop and calls it done — it works in the open and hands back at
  every checkpoint.
- **Durability.** What the work produces must outlive the AI entirely — plain
  documents anyone can read and plain code anyone can run, with no AI, agent, or
  particular IDE required to use, understand, run, or edit it. AI is an authoring
  accelerant, never a dependency.

Everything below is the practice that keeps both true.

## Relationship to a working agreement

This template is the **detailed model**. An organization may also keep a short,
signable working agreement (the contract in a page or two) that points into it. The
agreement is the contract; this folder is the full operating manual behind it. A team
can adopt a short agreement alone, or copy this whole tree for the complete model.

## How an agent should use this

Read this tree at the start of a working session and treat it as binding:

1. **[00 — Working Relationship](./00-working-relationship.md)** — the contract.
   The principles that govern everything: who proposes, who disposes, and where
   the review gates are. Read this first.
2. **[workflow/](./workflow/README.md)** — the repeatable process for doing a unit
   of work (an "effort"): the docs structure, the effort model, the backlog and
   logs (with the exact log formats), scaffolding rules, the review/publish flow,
   the UI-mockup step, and the weekly stakeholder update built from the logs.
3. **[decisions/](./decisions/README.md)** — where and how design decisions are
   captured (considerations, alternatives, chosen path).
4. **[directives/](./directives/README.md)** — short, imperative do/don't rules
   the agent must obey. When a directive and a general preference conflict, the
   directive wins.
5. **[use-raven](./directives/use-raven.md)** — raven is installed to do certain jobs the same way
   every time. When one of its commands matches the task, run it; do not rebuild it. If raven is
   missing or has no command for the task, say so.

## Adopting this in a new project

1. Copy this folder into the project's docs tree (e.g. `docs/ai/`).
2. Do a pass for the **substitution points** — each is flagged inline as
   `SUBSTITUTE:` and summarized here:
   - **Issue tracker** — the backlog format targets a generic Epic → Feature →
     Story shape; keep it or map it to your tracker's import format.
   - **Docs publisher** — docs-as-source-of-truth assumes *some* publisher renders
     the `docs/` tree to a wiki/space; name yours (or drop the publish step if the
     repo docs are the only surface). With DPS **markdown-tools**, commit its
     `markdown-to-*.toml` settings and `.md2conf/` / `.md2jira/` state and keep
     them current (see the publishing directive); never commit `.env`.
   - **Git host + review tooling** — the GitLab/merge-request directive is written
     for a protected-`main` + MR flow; swap `glab`/GitLab for your host's
     equivalent (GitHub PRs, etc.).
   - **CI system** — the review/publish flow assumes a CI gate on the change; name
     yours.
   - **Network/VPN** — the connectivity directive is only relevant if your hosts
     are behind a VPN; keep it, generalize it, or delete it.
3. Optionally place a copy as **IDE steering** (a user- or repo-level steering
   file) so the agent loads it automatically — but keep this published tree the
   human-readable source of truth, and have the steering copy *point here* rather
   than duplicate it.

## Authority and precedence

This tree is the **source of truth** for the working model in a project that
adopts it. Other mechanisms that carry process guidance to an agent — persistent
memories, IDE steering files, per-agent configs — should **point at this tree, not
duplicate it**. When they disagree, this tree wins and the other should be
corrected to match. A human instruction given live in-session overrides any
document for that session; if it's a durable change, fold it back into the
relevant doc here.

## What this is not

- Not a style guide for a specific language or framework — that belongs in the
  project's own `architecture/` or steering.
- Not a substitute for the project's product docs — this describes *how* we work,
  not *what* the product is.

## Contents

| Area | What's in it |
|------|--------------|
| [00 — Working Relationship](./00-working-relationship.md) | The contract: agent proposes, human disposes; the review gates; trust and autonomy |
| [workflow/](./workflow/README.md) | The repeatable effort process — docs structure, effort model, backlog/logs (with the log formats), scaffolding, review/publish, UI mockups, weekly updates, the deep scan |
| [decisions/](./decisions/README.md) | How design decisions are captured (ADRs vs. the lightweight log) |
| [directives/](./directives/README.md) | Hard do/don't rules — use raven, docs presence & structure, deep scan, git host & reviews, connectivity, secrets & env, publishing config & state, UI mockup format |
