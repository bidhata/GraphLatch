# GraphLatch architecture

GraphLatch separates **intent**, **planning**, **execution**, **verification**, and **learning**. This keeps the workflow inspectable and prevents implementation activity from silently redefining what success means.

## Components

### Task contract

The task contract is the source of truth for the run. It defines the outcome, limits, completion predicates, and excluded work. Nodes may refine the contract, but must not silently broaden it.

### Task graph

The graph is a directed acyclic graph (DAG). Each node is a unit of work with bounded write scope and an independent acceptance check. Each dependency edge includes a reason, so dependencies are explainable rather than decorative.

The validator derives execution levels using topological ordering. Nodes in the same level are candidates for parallel execution, not an instruction to parallelize. The agent must still check write conflicts, shared state, environmental constraints, and tool capabilities.

### Executor

The executor is the coding agent (or human/agent team) carrying out a node. GraphLatch does not own processes, sessions, credentials, sandboxes, or worktrees. The executor chooses the safest supported mechanism.

### Verifier

A verifier is a deterministic project check: tests, build, type-check, lint, static analysis, a reproducible CLI command, or a domain-specific assertion. Prefer checks that can be rerun and have unambiguous pass/fail outcomes.

The implementation agent may run the verifier, but its claim that a check passed is not evidence. Record the command and observed result. Where assurance matters, use independent review or a separate verifier.

### State and durable learning

`STATE.md` captures the current run: node state, decisions, checks, failures, and blockers. Project instruction files hold durable conventions. Only repeated, generalizable lessons should be promoted into long-lived instructions.

## Node lifecycle

```text
pending -> ready -> in_progress -> verifying -> completed
                       |                |
                       v                v
                     failed <------------
                       |
                       v
                    blocked (dependants only)
```

A node becomes `ready` when all dependencies are complete. A failed dependency blocks its dependants. Unrelated nodes can continue if doing so remains safe and useful.

## Parallelism rules

- Parallelism is based on graph independence, not on the number of available agents.
- A graph level is only a candidate batch; shared resources or overlapping write scopes can force serialization.
- Give each concurrently executing implementation node an isolated worktree or equivalent workspace.
- Establish interfaces and file ownership before dispatching workers.
- Integrate in dependency order and inspect every diff.

## Bounded correction policy

A node gets at most three total implementation/check cycles. Stop earlier when the same failure appears twice without a meaningful change in evidence or approach. Escalate with a failure record rather than burning cycles.

## Completion policy

The overall run is complete only when every `done_when` predicate in the contract is supported by evidence. A node status of `completed` means its own acceptance checks passed; it does not by itself prove the whole project is complete.
