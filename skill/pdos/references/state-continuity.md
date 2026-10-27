# State continuity

Use `.pdos/STATE.md` as a concise handoff index between fresh contexts, not as a transcript or unquestioned source of truth.

## Hydrate at the start

1. Read `.pdos/STATE.md` before planning or changing code.
2. Extract the current phase, current slice, active workstreams, active review and remediation links, consequential open decisions, known risks, last verification, and next safe action.
3. Follow only the relevant links under `Read next`. If legacy state has no links, inspect the active plan plus specs and decisions relevant to the task.
4. Compare the handoff with explicit user instructions, repository status, recent changes, tests, and observable behavior.
5. Mark or repair stale claims before relying on them. Explicit current user direction wins; intended product decisions explain desired behavior; repository and test evidence explain actual behavior.

Do not read the entire `.pdos/` tree by default. Progressive loading prevents old reviews and completed plans from crowding out the current task.

## Persist before handoff

Keep `STATE.md` at or below 200 lines and 16 KiB so every substantial run can read it. Update:

- `Updated` and `State confidence`.
- State revision plus current branch and observed commit. Keep absolute worktree paths only under ignored `.pdos/local/`.
- Current phase, slice, and active workstreams.
- Consequential open decisions and blocking dependencies.
- What changed and what was verified, including anything not run.
- Residual risks and conflicts between intent and implementation.
- `Read next` pointers for the next context, including active policy, review, and remediation when applicable.
- One concrete `Next safe action`.

Move completed or detailed history into `.pdos/archive/`, plans, decisions, or reviews and link it. Never erase a still-relevant founder decision merely to shorten state. Do not load the archive unless the current state points to a specific archived item.

## Concurrency

Before editing shared state, re-read it and inspect repository changes. Follow [workstream-coordination.md](workstream-coordination.md) when more than one context may be active. When another workstream changed overlapping state, reconcile rather than overwrite. Escalate only when the conflict changes consequential product intent or cannot be safely merged.
