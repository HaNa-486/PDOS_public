# PDOS lifecycle

## 1. Orient

- Inspect the repository, current behavior, constraints, data, and deployment context.
- Identify the primary user, job, success signal, non-goals, and critical journey.
- Reconstruct intent from evidence when inheriting an existing product.

## 2. Specify

- Write product behavior as observable outcomes, not implementation wishes.
- Define happy paths, edge cases, states, permissions, failure behavior, and acceptance evidence.
- Maintain a trace from requirements to tests or demonstrations.

## 3. Attack assumptions

- Classify facts as explicit, inferred, assumed, or open.
- Prefer safe reversible defaults for low-impact uncertainty.
- Escalate consequential uncertainty as a compact decision with a recommendation.

## 4. Plan

- Slice work vertically so each increment produces testable user value.
- Put risks and unknowns early. Include migration, observability, rollout, and rollback work.

## 5. Implement

- Preserve unrelated work. Validate each slice before expanding scope.
- Update product state when evidence changes an assumption or decision.

## 6. Verify

- Run static, unit, integration, contract, end-to-end, experience, and production-readiness checks as applicable.
- Exercise the product as a real user, including recovery paths.

## 7. Release and learn

- Apply the release gate, document residual risk, and confirm rollback and monitoring.
- Feed incidents, feedback, and eval failures into the next iteration.
