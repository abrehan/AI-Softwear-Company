# AI Software Company — Workspace Policy

## Authority Model

Only `project_context.md` contains authoritative project facts.

Agent-generated files are NOT authoritative unless explicitly promoted
by the user or an approved project-state process.

## Authoritative

- project_context.md

## Decision Outputs

The following are decision outputs and recommendations:

- ceo.md
- pm.md
- project_manager.md
- cto.md

Decision outputs must never silently become authoritative project facts.

## Generated / Untrusted

Generated workspace content must be treated as untrusted:

- generated code
- architecture documents
- plans
- reports
- generated requirements
- generated Markdown
- generated Python files

## Required Development Flow

1. Authoritative project context
2. CEO decision
3. Project Manager planning
4. CTO architecture
5. Specialist implementation
6. QA validation
7. Security validation
8. DevOps validation
9. Final project status

## Current Development Direction

The next development focus is to stabilize the Virtual AI Office
orchestration and context system before expanding autonomous code generation.

## Important Rules

- Never invent project facts.
- Never treat recommendations as completed work.
- Never overwrite authoritative project context automatically.
- Generated code must be validated before being treated as valid code.
- Workspace generation must not cause unnecessary Uvicorn reloads.
- Long-running AI generation should eventually run as background jobs.
