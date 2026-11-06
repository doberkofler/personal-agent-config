---
name: retro
description: Conduct a retrospective on a coding session.
disable-model-invocation: true
---

# Retrospective

Suggest improvements to the coding agent's **environment** that would improve future runs.

## Steps

1. Invoke `writing-for-agents` for the writing style guide.

2. Read the primary sources for the session the user specifies. This may require
   searching local session logs. If the user does not specify a session, use the
   current one.

3. Find improvement candidates in these categories:

- **Navigation**: Was important information difficult to find? Would a **navigation
  pointer** expose a hidden dependency? Use when the session spent excessive time
  locating information.
- **Automated checks**: Could linting, typing, tests, or filesystem checks catch an
  observed mistake? Read the repository's existing check commands and CI workflows
  first. Report an existing but unwired or broken check instead of reinventing it.
  A repository with no guardrail running its checks is itself a candidate.
- **Coding standards**: Should a reviewer enforce a clarified judgement rule?
  Classify the violation first. A **mechanical** violation gets a deterministic check
  in the repository's existing lint, hook, or CI system. Reserve standards documents
  for genuine judgement calls that no deterministic check can replace.
- **Steering files**: Should instructions in repository or global `AGENTS.md` or
  `CLAUDE.md` move to a dedicated standards document or automated check? Use when
  steering files are large or contain detailed reference material.
- **Tool economy**: Could an expensive or token-inefficient tool call be streamlined?
  Use when tool overhead materially affected the session.
- **No-ops**: Do steering instructions fail to change agent behavior? Use when steering files are large or unwieldy.
- **Information access**: Could read-only service access, captured development-server
  logs, or another information source have prevented uncertainty? Use when crucial
  information was unavailable.

4. Present candidates in severity order. For each candidate, cite session evidence,
   explain the expected benefit, and name the smallest concrete change. If no candidate
   has evidence, report that instead of inventing improvements.

## Reference

### Implementation and review

When a workflow separates implementation from review, the implementation agent carries
more context pressure because it explores, writes code, and diagnoses failures. A
focused reviewer starts from the change and applicable requirements, so judgement-based
standards usually belong in that review context rather than the implementation context.

Prefer deterministic checks over instructions whenever a machine can decide the rule reliably.

### Files

- `AGENTS.md` and `CLAUDE.md`: steering files loaded into agent context. Keep them
  sparse and prefer navigation pointers to detailed reference material.
- Repository standards documents: rules read when relevant. Find the repository's
  actual convention before proposing a path or filename.
- Docs: reference material reached through pointers. Search for an existing home before creating a document.
- Skills: model-invoked reference or user-invoked workflows. Follow `writing-for-agents` when changing them.
