# GraphLatch protocol

This document is the normative operating protocol. The agent skill at `skill/graph-latch/SKILL.md` is the operational entry point.

## A. Contract

Create a contract before implementation:

- Goal: observable result.
- Constraints: required compatibility, security, performance, scope, style, and operational boundaries.
- Done when: explicit and testable acceptance predicates.
- Out of scope: prohibited or unnecessary work.

Resolve material ambiguity before acting. Record assumptions separately from observed facts.

## B. Graph

Each node must have a unique ID, a bounded goal, inputs, outputs, dependency reasons, write scope, acceptance checks, risk, and status. Every dependency must be justified by an output or decision that the successor consumes. Reject self-dependencies, missing dependency IDs, and cycles.

A valid topological level identifies nodes whose graph dependencies are complete. It does not guarantee safe concurrency: the executor must also inspect shared files, external systems, and tool/environment limits.

## C. Dispatch

Provide each worker with:

- The overall contract and its assigned node.
- Allowed files/resources and forbidden scope expansion.
- Relevant interfaces and assumptions.
- Expected outputs and evidence.
- Required checks and escalation conditions.

Parallel implementation requires write isolation. Use a separate Git worktree or equivalent workspace for each concurrent implementation node. If safe isolation is unavailable, serialize the work.

## D. Execution and retry

For each node, inspect, implement, check, review, and correct. There are at most three total build/check cycles. Stop earlier after the same failure recurs twice without meaningful new evidence. A retry must change something based on diagnostics.

Do not weaken a test simply to obtain a pass. Change a test only when it is demonstrably incorrect, and record the reasoning.

## E. Failure record

Record:

- Node ID and state.
- Exact command/check and relevant output.
- Attempts and changes made between attempts.
- Current hypothesis (labelled as a hypothesis).
- Evidence needed to proceed.
- Dependants blocked by the failure.

Keep unrelated nodes moving when safe. Never conceal partial work or report an unrun check as passing.

## F. Risk gates

- ALLOW: read-only inspection and low-risk reversible actions within contract.
- ASK: ambiguous scope, destructive/hard-to-reverse operations, external side effects, production changes, or actions needing authorization/credentials.
- DENY: out-of-scope, unauthorized, or unacceptably harmful actions.

Active security testing requires explicit authorization, target allowlists, approved methods, time windows, rate limits, and stop conditions. Access or reachability alone does not establish authorization.

## G. Integration

Integrate in dependency order. Review aggregate diffs and interfaces. Run broad validation. Re-evaluate all contract completion predicates. Overall completion requires evidence for every predicate.

## H. Learning

Use `STATE.md` for current-run facts. Put durable guidance in the project's native instruction file. Promote a rule only after a repeated failure pattern (at least twice) demonstrates a generalizable preventive action. Never persist secrets, tokens, passwords, private keys, or sensitive target details.

## I. Final report

Report outcome; contract; node states; exact validations and results; changed files/behaviour; risks; approvals; and unverified criteria. Be precise about partial completion.
