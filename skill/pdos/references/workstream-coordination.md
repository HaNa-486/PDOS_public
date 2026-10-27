# Workstream coordination

Use one file per substantial context under `.pdos/workstreams/`. This isolates handoffs while allowing parallel contexts to detect overlap.

## Start

1. Read `STATE.md` and list active workstream files other than `_template.md`.
2. Run `scripts/start_workstream.py <project-root> <slug> --scope "..." --areas "..."`.
3. Record the branch, base commit, scope, and files or product areas at risk. Store absolute worktree identity only in ignored `.pdos/local/` metadata.
4. Compare scope with other active workstreams. Partition non-overlapping work autonomously. Pause overlapping edits until the scopes can be reconciled.

## Work

- Update only this run's workstream file for detailed progress.
- Re-read repository status and overlapping workstreams before editing shared code, plans, decisions, or `STATE.md`.
- Never assume separate contexts serialize their writes. Merge new facts rather than replacing a state file based on an earlier read.
- Treat different worktrees or branches as different actual states even when product intent is shared.

## Finish

1. Re-read `STATE.md` and overlapping workstreams.
2. Merge durable outcomes into specs, decisions, plans, and the concise state index.
3. Mark the workstream `completed`, `paused`, or `blocked`; include verification and the next safe action.
4. Use `scripts/update_workstream.py` to record a terminal status and archive completed detail when it no longer helps current coordination.

Escalate only when concurrent work creates a consequential product conflict or an unsafe code/data merge that cannot be resolved from evidence.
