---
name: graph-latch
description: Use for substantial multi-step engineering work that benefits from an explicit task contract, dependency-derived DAG, isolated parallel execution, bounded build-check-correct loops, deterministic validation, failure isolation, risk gates, and evidence-backed completion.
license: MIT
compatibility: Works with coding agents that can inspect files and run project commands. Parallel agents and worktrees are optional capabilities; serialize tasks when unavailable.
metadata:
  author: bidhata
  project: GraphLatch
  version: "1.0.0"
---

# GraphLatch

Use this protocol to orchestrate substantial multi-step engineering work. GraphLatch is an operating method, not an execution runtime: the active agent and its tools perform the work.

## When to use

Use for multi-file features, refactors, migrations, bug investigations with multiple workstreams, release preparation, or work delegated across multiple agents.

Do not invoke for trivial one-file edits, simple questions, or tasks where planning overhead is greater than the work. Do not use the graph as an excuse to parallelize work that is naturally sequential.

## 1. Read project context and establish the contract

Read the repository's native instructions (`AGENTS.md`, `CLAUDE.md`, relevant package instructions), current state, and nearby implementation before editing.

Write a concise task contract with:

- **Goal:** observable outcome.
- **Constraints:** scope, compatibility, security, performance, style, and operational limits.
- **Done when:** objective acceptance predicates.
- **Out of scope:** changes/actions that must not be performed.

Separate observed facts from assumptions. Resolve any material ambiguity about safety, authorization, scope, or correctness before acting.

Use `templates/TASK_CONTRACT.md` when helpful.

## 2. Build a dependency-derived task graph

Decompose the contract into small, independently verifiable nodes. Each node must define a goal, inputs, outputs, dependencies (with reasons), write scope, acceptance checks, risk, and status.

Create an edge `A -> B` only when B needs an artifact, decision, or state produced by A. Nodes with no dependency path between them are only candidates for parallel execution; check shared files, services, external resources, and write-scope overlap before dispatch.

Use `templates/task-graph.json` as the starting structure. If Python is available, validate a project graph with the bundled `scripts/validate_graph.py`:

```bash
python3 scripts/validate_graph.py path/to/task-graph.json
```

The validator checks graph structure and cycles; it does not assess whether the plan is wise or execute tasks.

## 3. Dispatch with isolation

For each assigned node, give the worker the overall contract, node goal, allowed write scope, interfaces, expected outputs, acceptance checks, and escalation rules.

Run independent implementation nodes concurrently only when their write scopes and shared resources do not conflict. Prefer one Git worktree or equivalent isolated workspace per concurrent implementation node. If isolation is unavailable or uncertain, serialize. Never have multiple workers edit the same files concurrently.

Do not let a worker expand scope or change shared interfaces without coordinating with dependent nodes.

## 4. Run a bounded build-check-correct loop

For each node:

1. Inspect relevant code, project conventions, and current diffs.
2. Implement the smallest change that meets the node goal.
3. Run the narrowest relevant deterministic check.
4. Inspect the actual output and the complete diff within the node's write scope.
5. Correct failures based on diagnostic evidence and rerun checks.

Allow at most **three total implementation/check cycles per node**. Stop earlier if the same failure reproduces twice without meaningful new evidence or a materially different approach. Do not repeat an identical failing action without a reason.

Use the target repository's `./check.sh` when it exists and is relevant. Otherwise identify the actual tests/build/type-check/lint or domain-specific commands. Never invent a check, claim a command ran when it did not, or weaken tests simply to get a pass.

## 5. Isolate failures

When a node fails, mark only that node failed and its dependants blocked. Continue unrelated ready nodes when doing so is safe. Preserve exact commands, relevant output, attempts, changes between attempts, a clearly labelled hypothesis, and evidence needed to proceed.

Do not silently discard partial work. A hypothesis is not a finding; an unrun check is not a pass.

## 6. Apply risk gates

- **ALLOW:** read-only inspection and low-risk, reversible actions within the contract.
- **ASK:** ambiguous scope, destructive or hard-to-reverse changes, external side effects, production-impacting actions, or actions requiring credentials/authorization.
- **DENY:** out-of-scope, unauthorized, or unacceptably harmful actions.

For active security testing, require explicit authorization and a clear target allowlist, approved methods, time window, rate limits, and stop conditions. Technical reachability is not authorization. Stop if scope or authorization becomes uncertain.

## 7. Integrate and verify the complete contract

Integrate completed nodes in dependency order. Review aggregate diffs, interfaces, assumptions, and unintended changes. Run the broadest relevant validation, then evaluate every `done when` predicate from the original contract.

Do not declare the overall task complete merely because every worker reports success. Completion requires evidence for every contract predicate. State what remains unverified.

## 8. Record state and durable lessons

Use `templates/STATE.md` (or the project's existing equivalent) for current-run decisions, node statuses, checks, failures, and blockers. Keep durable conventions in the project's native instruction file (`AGENTS.md`, `CLAUDE.md`, or equivalent).

Promote a lesson into permanent guidance only after the same failure pattern has occurred at least twice and the preventive rule is generalizable. Check for an existing equivalent rule first. Never store secrets, credentials, tokens, private keys, or sensitive target data in state or instruction files.

## 9. Final engineering report

Return:

- **Outcome:** completed, partially completed, or blocked.
- **Contract:** goal and completion predicates.
- **Graph:** nodes completed, failed, and blocked.
- **Validation:** exact commands and actual results.
- **Changes:** important files and behavioural impact.
- **Risks/follow-ups:** approvals, uncertainty, and unverified criteria.

Be precise. Do not imply tests, reviews, or approvals occurred unless they actually did.

## Supporting material

Read `references/protocol.md` for the normative protocol and `templates/` for starter files. All paths are relative to this skill directory.
