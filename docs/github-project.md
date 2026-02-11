# GitHub Project Design

## Board Model
Phase-based execution with milestones:
- `v0.1-alpha`
- `v0.2-beta`
- `v1.0-ga`

## Recommended Fields
- Status: Backlog, Ready, In Progress, In Review, Done
- Phase: 0..10
- Area: backend, worker, frontend, deploy, docs
- Priority: p0..p3
- Risk: low/medium/high
- Milestone: alpha/beta/ga
- BlockedBy
- SecurityImpact

## Labels
- `area/backend`, `area/frontend`, `area/worker`, `area/deploy`, `area/docs`
- `type/feature`, `type/bug`, `type/chore`, `type/security`
- `legacy-kafka`, `ai-cost`, `breaking-change`
