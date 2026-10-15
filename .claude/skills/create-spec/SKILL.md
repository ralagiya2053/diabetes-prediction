---
name: create-spec
description: Draft a spec.md for the current feature branch following the SDD workflow. Reads CLAUDE.md for roadmap and conventions, pulls context from the repo, and writes specs/<NNN>-<slug>/spec.md. Stops after spec.md for user review — does NOT create plan.md or tasks.md.
---

You are drafting a specification for the CURRENT feature branch.

## Preconditions (verify before writing)
1. Confirm the current git branch matches `feat/<NNN>-<slug>`.
2. Read `.claude/CLAUDE.md` to identify which feature (F1–F4) this branch is.
3. If the branch does not match a roadmap feature, stop and ask.
4. If `specs/<NNN>-<slug>/spec.md` already exists, stop and ask — do not overwrite.

## Inputs to gather
Ask the user for anything missing:
- Figma link, existing files, external references relevant to THIS feature
- Constraints, deadlines, or non-obvious requirements
- Any open questions the user already has

Do NOT invent requirements. If something is ambiguous, list it under Open Questions.

## Spec template (write exactly this structure)

```markdown
# Spec <NNN> — <Feature Name>

**Status:** Draft
**Feature ID:** F<N>
**Branch:** feat/<NNN>-<slug>
**Author:** <git user>
**Created:** <YYYY-MM-DD>

## 1. Problem Statement
Why does this feature exist? What gap does it close? 2–4 sentences.

## 2. Scope
**In scope:**
- bullet list

**Out of scope:**
- bullet list

## 3. User-Facing Behavior
Describe what the user sees / experiences. Before vs after if helpful.
No implementation details.

## 4. Acceptance Criteria
Numbered, testable, atomic. Each one must be verifiable by a human or a test.
1. ...
2. ...

## 5. Non-Goals
Explicitly excluded from this feature (even if related).

## 6. Dependencies
- Other features (e.g., F2 depends on F1)
- External services (AWS, Bedrock, Figma, etc.)
- Files or modules this feature will touch

## 7. Risks & Unknowns
Anything that could block or change the design.

## 8. Open Questions
Must be resolved before plan.md is written. If none, write "None."

## 9. References
- Figma / docs / prior art links

## Rules
- Keep the spec user- and behavior-focused. No code, no file paths, no implementation.
- Acceptance criteria must be testable. Reject vague wording ("looks nice").
- Respect the "Frozen — Do Not Modify" list in CLAUDE.md. If the feature seems to require touching frozen files, flag it under Open Questions — do not plan around it silently.
- Reference the SDD step in any commit message you suggest (this skill ends at Step 2).

## After writing

- Print the file path.
- Print a short summary (3–5 lines) of what the spec covers.
- Ask the user to review and approve before proceeding to Step 3 (Plan).
- Stop. Do not create plan.md. Do not commit. Do not run /github-commit.
- The user will trigger the next step.