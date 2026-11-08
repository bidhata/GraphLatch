#!/usr/bin/env python3
"""Validate a GraphLatch task graph (JSON, Python standard library only)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

VALID_RISKS = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"pending", "ready", "in_progress", "verifying", "completed", "failed", "blocked"}
REQUIRED_CONTRACT_FIELDS = ("goal", "constraints", "done_when", "out_of_scope")
REQUIRED_NODE_FIELDS = ("id", "title", "goal", "inputs", "outputs", "depends_on", "write_scope", "acceptance", "risk", "status")


class GraphValidationError(Exception):
    pass


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_non_empty_string(item) for item in value)


def validate_graph(data: Any) -> tuple[list[list[str]], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        raise GraphValidationError("top-level JSON value must be an object")

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be the string '1.0'")
    if not _non_empty_string(data.get("project")):
        errors.append("project must be a non-empty string")

    contract = data.get("contract")
    if not isinstance(contract, dict):
        errors.append("contract must be an object")
    else:
        for field in REQUIRED_CONTRACT_FIELDS:
            value = contract.get(field)
            if field == "goal":
                if not _non_empty_string(value):
                    errors.append("contract.goal must be a non-empty string")
            elif not _string_list(value):
                errors.append(f"contract.{field} must be an array of non-empty strings")
            elif field == "done_when" and not value:
                errors.append("contract.done_when must contain at least one completion predicate")

    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes must be a non-empty array")
        return [], errors + warnings

    by_id: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes):
        prefix = f"nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in REQUIRED_NODE_FIELDS:
            if field not in node:
                errors.append(f"{prefix}.{field} is required")
        node_id = node.get("id")
        if not _non_empty_string(node_id):
            errors.append(f"{prefix}.id must be a non-empty string")
            continue
        if node_id in by_id:
            errors.append(f"duplicate node id: {node_id}")
        else:
            by_id[node_id] = node
        for field in ("title", "goal"):
            if not _non_empty_string(node.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        for field in ("inputs", "outputs", "write_scope", "acceptance"):
            if not _string_list(node.get(field)):
                errors.append(f"{prefix}.{field} must be an array of non-empty strings")
            elif field == "acceptance" and not node.get(field):
                errors.append(f"{prefix}.acceptance must contain at least one check")
        risk = node.get("risk")
        if not isinstance(risk, str) or risk not in VALID_RISKS:
            errors.append(f"{prefix}.risk must be one of: {', '.join(sorted(VALID_RISKS))}")
        status = node.get("status")
        if not isinstance(status, str) or status not in VALID_STATUSES:
            errors.append(f"{prefix}.status must be one of: {', '.join(sorted(VALID_STATUSES))}")
        deps = node.get("depends_on")
        if not isinstance(deps, list):
            errors.append(f"{prefix}.depends_on must be an array")
        else:
            seen_deps: set[str] = set()
            for dep_index, dep in enumerate(deps):
                dep_prefix = f"{prefix}.depends_on[{dep_index}]"
                if not isinstance(dep, dict):
                    errors.append(f"{dep_prefix} must be an object with node and because")
                    continue
                dep_id, reason = dep.get("node"), dep.get("because")
                if not _non_empty_string(dep_id):
                    errors.append(f"{dep_prefix}.node must be a non-empty string")
                    continue
                if dep_id == node_id:
                    errors.append(f"node {node_id} cannot depend on itself")
                if dep_id in seen_deps:
                    errors.append(f"node {node_id} has duplicate dependency {dep_id}")
                seen_deps.add(dep_id)
                if not _non_empty_string(reason):
                    errors.append(f"{dep_prefix}.because must explain why the dependency exists")

    # Check references only after collecting all node IDs.
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in by_id}
    indegree: dict[str, int] = {node_id: 0 for node_id in by_id}
    for node_id, node in by_id.items():
        deps = node.get("depends_on", [])
        if not isinstance(deps, list):
            continue
        for dep in deps:
            if not isinstance(dep, dict) or not _non_empty_string(dep.get("node")):
                continue
            dep_id = dep["node"]
            if dep_id not in by_id:
                errors.append(f"node {node_id} references unknown dependency {dep_id}")
                continue
            adjacency[dep_id].append(node_id)
            indegree[node_id] += 1

    if errors:
        return [], errors + warnings

    # Kahn's algorithm, returning deterministic execution levels.
    levels: list[list[str]] = []
    ready = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
    processed = 0
    while ready:
        current = ready
        levels.append(current)
        processed += len(current)
        next_ready: list[str] = []
        for node_id in current:
            for successor in sorted(adjacency[node_id]):
                indegree[successor] -= 1
                if indegree[successor] == 0:
                    next_ready.append(successor)
        ready = sorted(next_ready)

    if processed != len(by_id):
        cyclic = sorted(node_id for node_id, degree in indegree.items() if degree > 0)
        errors.append("dependency cycle detected; nodes involved or downstream: " + ", ".join(cyclic))
        return [], errors + warnings

    # Warn about exact path collisions; this is a prompt to inspect broader/shared resources.
    owners: dict[str, list[str]] = defaultdict(list)
    for node_id, node in by_id.items():
        for path in node.get("write_scope", []):
            if isinstance(path, str):
                owners[path].append(node_id)
    for path, node_ids in sorted(owners.items()):
        if len(node_ids) > 1:
            warnings.append(f"write_scope collision for '{path}' across nodes: {', '.join(sorted(node_ids))}; serialize or isolate deliberately")

    return levels, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="Path to a GraphLatch JSON task graph")
    args = parser.parse_args()
    try:
        with args.graph.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.graph}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}", file=sys.stderr)
        return 2
    try:
        levels, messages = validate_graph(data)
    except GraphValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = [message for message in messages if not message.startswith("write_scope collision")]
    warnings = [message for message in messages if message.startswith("write_scope collision")]
    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    for message in warnings:
        print(f"WARNING: {message}")
    print(f"Graph valid: {len(data['nodes'])} node(s), {len(levels)} execution level(s).")
    for index, level in enumerate(levels, start=1):
        print(f"  Level {index}: {', '.join(level)}")
    print("Note: execution levels are dependency-derived candidates; inspect write scopes and shared resources before parallelizing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
