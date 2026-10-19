---
name: create-plan
description: Draft a plan.md for the current feature branch following the SDD workflow. Requires an approved spec.md to exist first. Reads CLAUDE.md and the spec, then writes specs/<NNN>-<slug>/plan.md. Stops after plan.md for user review — does NOT create tasks.md or write code.
---

You are drafting a technical plan for the CURRENT feature branch.

## Preconditions (verify before writing)
1. Confirm the current git branch matches `feat/<NNN>-<slug>`.
2. Read `.claude/CLAUDE.md` to identify which feature (F1–F4) this branch is.
3. Confirm `specs/<NNN>-<slug>/spec.md` exists and its Status is "Approved"
   (or "Draft" with explicit user approval — ask if unclear).
4. If `specs/<NNN>-<slug>/plan.md` already exists, stop and ask — do not overwrite.

## Inputs to gather
Ask the user for anything missing:
- Technical constraints (language, framework, existing patterns to reuse)
- File paths or modules the plan must touch
- Deployment / runtime environment details
- Any decisions the user already has in mind

Do NOT invent architecture. If something is ambiguous, list it under Open Questions.

## Plan template — write the plan file using exactly this structure

    # Plan <NNN> — <Feature Name>

    **Status:** Draft
    **Feature ID:** F<N>
    **Branch:** feat/<NNN>-<slug>
    **Spec:** specs/<NNN>-<slug>/spec.md
    **Author:** <git user>
    **Created:** <YYYY-MM-DD>

    ## 1. Approach Summary
    2–5 sentences. How will this spec be satisfied? Name the technique
    (e.g., "add semantic HTML header/footer, style with CSS variables from Figma").

    ## 2. Files to Create
    - `path/to/new-file` — purpose
    - `path/to/another` — purpose

    ## 3. Files to Modify
    - `path/to/existing` — what changes and why
    (Respect the "Frozen — Do Not Modify" list in CLAUDE.md. If a frozen file
    must be touched, stop and flag it — do not plan around it silently.)

    ## 4. Architecture / Data Flow
    Describe how the pieces fit. ASCII diagram or bullet flow.

    ## 5. Step-by-Step Implementation
    Ordered, atomic steps. Each step should be independently committable
    where possible. Reference the acceptance criteria (AC#) each step satisfies.

    1. Step — satisfies AC#
    2. Step — satisfies AC#
    ...

    ## 6. Test Strategy
    - Manual validation steps (what to click, what to see)
    - Automated tests to add (if any), in which file
    - How each acceptance criterion will be verified

    ## 7. Rollout & Rollback
    - How the change is deployed (e.g., push to GH Pages, redeploy Lambda)
    - How to roll back if broken (e.g., git revert, redeploy previous image)

    ## 8. Risks & Mitigations
    - Risk — mitigation
    - Risk — mitigation

    ## 9. Open Questions
    Must be resolved before tasks.md is written. If none, write "None."

## Rules
- The plan describes HOW. No code blocks with actual implementation logic —
  pseudo-code or interface signatures only.
- Every acceptance criterion in spec.md must be traceable to at least one
  step in Section 5.
- Never plan to modify frozen files. If blocked, raise it as an Open Question.
- If the plan requires new dependencies (npm, pip, CDN), list them explicitly
  in Section 2 or 3 — never install implicitly.
- Reference the SDD step in any commit message you suggest (this skill ends at Step 3).

## After writing
1. Print the file path.
2. Print a short summary (3–5 lines) of the plan.
3. Ask the user to review and approve before Step 4 (commit Spec + Plan, PR, merge).
4. **Stop.** Do not create tasks.md. Do not write code. Do not commit.
   The user will trigger the next step.