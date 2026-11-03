"""Frozen relation-component allocation for the Gate-0 synthetic protocol."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping
from gate0.contracts.types import record_digest
from gate0.identity import opaque_id


def relation_components(revision_ids: Iterable[str], edges: Iterable[tuple[str, str]]) -> tuple[tuple[str, ...], ...]:
    nodes = set(revision_ids)
    parent = {node: node for node in nodes}
    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    def union(left, right):
        if left not in nodes or right not in nodes:
            raise ValueError("relation references unknown revision")
        a, b = find(left), find(right)
        if a != b: parent[max(a, b)] = min(a, b)
    for left, right in edges: union(str(left), str(right))
    groups = defaultdict(list)
    for node in sorted(nodes): groups[find(node)].append(node)
    return tuple(sorted((tuple(group) for group in groups.values())))


def freeze_relation_split(revision_ids: Iterable[str], edges: Iterable[tuple[str, str]], inventory_digest: str,
                          *, evaluation_components: Iterable[str], development_components: Iterable[str],
                          split_version: str = "split-v1", frozen_at: str = "1970-01-01T00:00:00Z") -> tuple[dict, ...]:
    revisions = tuple(sorted(set(map(str, revision_ids))))
    components = relation_components(revisions, edges)
    by_revision = {revision: component for component in components for revision in component}
    requested = {"EVALUATION": set(evaluation_components), "DEVELOPMENT": set(development_components)}
    assigned = {}
    for allocation, seeds in requested.items():
        for seed in seeds:
            if seed not in by_revision: raise ValueError("unknown component seed")
            component = by_revision[seed]
            previous = assigned.get(component)
            if previous and previous != allocation: raise ValueError("LEAKAGE_DETECTED: component crosses split")
            assigned[component] = allocation
    if set(assigned) != set(components): raise ValueError("every relation component must be allocated")
    rows = []
    for component in components:
        allocation = assigned[component]
        payload = {"split_version": split_version, "relation_component_id": opaque_id("component", component), "allocation": allocation,
                   "frozen_at": frozen_at, "relation_inventory_digest": inventory_digest, "leakage_status": "VALID"}
        row = {"record_id": opaque_id("split", payload), "record_type": "split_allocation", "record_schema_version": "gate0.v1", "record_digest": "", "payload": payload}
        row["record_digest"] = record_digest(row)
        rows.append(row)
    return tuple(rows)


def validate_split(rows: Iterable[dict]) -> bool:
    rows = tuple(rows)
    components = [row["payload"]["relation_component_id"] for row in rows]
    allocations = [row["payload"]["allocation"] for row in rows]
    if len(set(components)) != len(components) or any(item not in {"DEVELOPMENT", "EVALUATION"} for item in allocations):
        raise ValueError("INVALID_SPLIT")
    if any(row["payload"]["leakage_status"] != "VALID" for row in rows): raise ValueError("LEAKAGE_DETECTED")
    return True


@dataclass(frozen=True)
class PostFreezeValidation:
    valid: bool
    requires_new_version: bool
    split_version: str
    reason: str | None = None

def validate_post_freeze_relations(frozen_rows: Iterable[Mapping], component_members: Mapping[str, Iterable[str]], later_edges: Iterable[tuple[str, str]]) -> PostFreezeValidation:
    rows = tuple(frozen_rows)
    version = rows[0]["payload"]["split_version"] if rows else ""
    allocation = {}
    for row in rows:
        component_id = row["payload"]["relation_component_id"]
        for revision in component_members.get(component_id, ()):
            allocation[str(revision)] = row["payload"]["allocation"]
    for left, right in later_edges:
        if left not in allocation or right not in allocation:
            return PostFreezeValidation(False, True, version, "POST_FREEZE_UNKNOWN_REVISION")
        if allocation[left] != allocation[right]:
            return PostFreezeValidation(False, True, version, "POST_FREEZE_CROSS_SPLIT_RELATION")
    return PostFreezeValidation(True, False, version, None)
