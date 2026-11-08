# Contributing to GraphLatch

Thanks for helping make agentic engineering workflows more reliable.

## What makes a good contribution?

Prefer changes backed by a concrete failure mode, reproducible example, or meaningful reduction in operational risk. Avoid adding ceremony that does not improve scope control, coordination, verification, or recovery.

## Before opening a pull request

1. Explain the problem and the observable failure mode.
2. Keep protocol changes small and consistent across `skill/graph-latch/SKILL.md` and `docs/protocol.md`.
3. Update examples and tests when the graph format or validator changes.
4. Run `./check.sh` and include the actual output summary.
5. Call out platform-specific assumptions and compatibility limits.

## Durable rules

A proposed mandatory rule should identify the repeated failure it prevents, the evidence supporting it, and the trade-offs it introduces. GraphLatch prefers a small number of enforceable principles over a long list of brittle instructions.


## Project maintainer

GraphLatch is created and maintained by **Krish Paul** ([@bidhata](https://github.com/bidhata)).
For maintainer contact and project information, visit [krishnendu.com](https://krishnendu.com) or email [me@krishnendu.com](mailto:me@krishnendu.com).
