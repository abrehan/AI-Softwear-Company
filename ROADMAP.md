# Product Roadmap

## Foundation — delivered

- Studio workspace UI and responsive office dashboard
- Project intake, delivery board, AI role directory, and marketing workspace
- Core FastAPI health, projects, and tasks endpoints
- Product documentation and local startup instructions

## Next: real operating data

- Replace the SQLite store with PostgreSQL and migrations for multi-user production use.
- Add organization-scoped project access and role-based approvals (account, organization, and session foundations are delivered).
- Persist project briefs and synchronize dashboard data through the API.
- Add activity events, audit logs, and file attachments.

## Agent operations

- Normalize the existing agent modules behind a stable job interface.
- Add a queue, job status, retries, cost limits, and human approval gates.
- Feed approved project context to specialist agents and retain traceable outputs.
- Connect source-control, deployment, and test runners through scoped credentials.

## Client delivery and growth

- Client portal for briefs, updates, approvals, and release notes.
- Proposal, estimate, contract, and invoicing flow.
- Marketing generator for positioning, case studies, launch pages, email, and social content.
- Analytics for pipeline, delivery predictability, quality, and campaign results.
