# CLAUDE.md — Diabetes Risk Predictor

## Project
End-to-end ML deployment: diabetes classifier on AWS Lambda (FastAPI + Docker,
Lambda Web Adapter) with static HTML frontend on GitHub Pages. Being extended
with a Bedrock RAG chatbot for portfolio demo.

- Frontend: https://ralagiya2053.github.io/diabetes-prediction/frontend/index.html
- API: Lambda Function URL → FastAPI (`/predict`, `/health`)
- Region: us-east-1

## Layout

app/ FastAPI service (main.py, schema.py)
frontend/ Static HTML UI (index.html, assets/ — styles.css + SVG icons)
tests/ Pytest suite (test_predict.py — currently empty)
train/ diabetes.csv (training dataset only)
specs/ SDD specs (created per feature)
.claude/ Claude Code config + skills


## Frozen — Do Not Modify
The existing prediction service is deployed and working. Do NOT change:
- `app/` (FastAPI service)
- `Dockerfile`
- Model artifacts (.pkl files, baked into the container image — not in repo)
- `train/diabetes.csv` (training dataset, do not alter)

F1–F4 are **additive only**. New code goes in new files/folders.

## SDD Workflow (mandatory, every feature)
1. Branch → 2. Spec → 3. Plan → 4. Commit Spec+Plan → 5. PR (Spec Review)
→ 6. Merge → 7. Tasks → 8. Build → 9. Validate → 10. Commit Code
→ 11. PR (Code Review) → 12. Merge

**Gates:**
- Gate 1 (4–6): Spec + Plan merged to main BEFORE any code.
- Gate 2 (10–12): Code merged AFTER validating against approved spec.

**Invariants:**
1. Spec before plan.
2. Plan merged before tasks.
3. Validate before PR.

Branch: `feat/<NNN>-<slug>`
Specs: `specs/<NNN>-<slug>/{spec.md, plan.md, tasks.md}`

## Roadmap
| ID | Feature | Branch |
|----|---------|--------|
| F1 | Website UI: full page redesign per Figma | `feat/01-website-ui-links` |
| F2 | Policy documents | `feat/02-policy-documents` |
| F3 | RAG backend (Lambda + Bedrock + S3 Vectors) | `feat/03-rag-backend` |
| F4 | Chatbot widget | `feat/04-chatbot-widget` |

## Conventions
- Python 3.11, FastAPI, Pydantic, pytest
- Commits: `feat:`, `fix:`, `docs:`, `spec:`, `plan:`, `chore:`
- Never commit `model/*`, `.env`, credentials
- Never skip Gate 1 or Gate 2
- Read active spec before writing code

## Skills
- `/create-spec` — draft spec.md for current branch (stops for review)
- `/create-plan` — draft plan.md after spec approval (stops for review)
- `/github-commit` — stage, commit (conventional), push current branch

## Cost Guardrails
- us-east-1 only. No OpenSearch Serverless. S3 Vectors for embeddings.
- $20 billing alarm set.