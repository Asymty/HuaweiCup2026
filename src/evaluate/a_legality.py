"""Independent structural legality checks for Huawei Cup 2026 problem A.

The checker deliberately does not import the official evaluator.  It mirrors the
public JSON contract and produces a small, serialisable report that can be
compared with the official verdict in tests.  Problem 1's Task-order cycle is
checked exactly at subgraph level.  Problems 2 and 3 can acquire additional
operation-level FIFO/memory edges inside the official scheduler; those final
execution-graph cycles remain an official-evaluator gate and are reported as a
warning when the conservative subgraph-order graph is cyclic.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, Mapping, Sequence


EXCLUDED_COPY_TYPES = frozenset({"COPY_IN", "COPY_OUT"})
VALID_PIPES = frozenset({"PIPE_MTE2", "PIPE_MTE3", "PIPE_M", "PIPE_V"})
VALID_MEMORY_POSITIONS = frozenset({"DDR", "L1", "UB"})


@dataclass(frozen=True)
class LegalityIssue:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass
class LegalityReport:
    legal: bool = True
    errors: list[LegalityIssue] = field(default_factory=list)
    warnings: list[LegalityIssue] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def add_error(self, code: str, message: str) -> None:
        self.legal = False
        self.errors.append(LegalityIssue(code, message))

    def add_warning(self, code: str, message: str) -> None:
        self.warnings.append(LegalityIssue(code, message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "legal": self.legal,
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
            "details": self.details,
        }


class _LegalityFailure(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _require_integer(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise _LegalityFailure("invalid_integer", f"{name} must be an integer >= 0")
    return value


def _find_cycle(
    nodes: Iterable[Hashable],
    edges: Iterable[tuple[Hashable, Hashable]],
) -> list[Hashable] | None:
    """Return one directed cycle, including its repeated first node."""

    adjacency: dict[Hashable, set[Hashable]] = {node: set() for node in nodes}
    indegree = dict.fromkeys(adjacency, 0)
    for source, target in edges:
        if source not in adjacency or target not in adjacency:
            raise _LegalityFailure(
                "unknown_edge_endpoint", f"unknown edge endpoint: {source!r} -> {target!r}"
            )
        if target not in adjacency[source]:
            adjacency[source].add(target)
            indegree[target] += 1

    ready = deque(node for node, count in indegree.items() if count == 0)
    visited = 0
    while ready:
        node = ready.popleft()
        visited += 1
        for target in adjacency[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    if visited == len(adjacency):
        return None

    color: dict[Hashable, int] = {}
    parent: dict[Hashable, Hashable] = {}
    for root in adjacency:
        if indegree[root] == 0 or root in color:
            continue
        color[root] = 1
        stack: list[tuple[Hashable, Any]] = [(root, iter(adjacency[root]))]
        while stack:
            node, children = stack[-1]
            target = next(children, None)
            if target is None:
                color[node] = 2
                stack.pop()
                continue
            if color.get(target) == 1:
                chain = [node]
                while chain[-1] != target:
                    chain.append(parent[chain[-1]])
                chain.reverse()
                chain.append(target)
                return chain
            if target not in color:
                color[target] = 1
                parent[target] = node
                stack.append((target, iter(adjacency[target])))
    return None


def _validate_graph(graph: Any) -> tuple[set[int], dict[int, set[int]]]:
    if not isinstance(graph, Mapping):
        raise _LegalityFailure("invalid_graph", "graph must be an object")
    for field_name in ("ops", "tensors", "edges"):
        if not isinstance(graph.get(field_name), list):
            raise _LegalityFailure("invalid_graph", f"graph.{field_name} must be a list")

    all_ids: set[int] = set()
    op_ids: set[int] = set()
    op_type: dict[int, str] = {}
    for op in graph["ops"]:
        if not isinstance(op, Mapping):
            raise _LegalityFailure("invalid_graph", "each op must be an object")
        op_id = _require_integer(op.get("id"), "op.id")
        if op_id in all_ids:
            raise _LegalityFailure("duplicate_node_id", f"duplicate op/tensor id: {op_id}")
        all_ids.add(op_id)
        op_ids.add(op_id)
        op_type[op_id] = op.get("op")
        if op.get("pipe") not in VALID_PIPES:
            raise _LegalityFailure("invalid_pipe", f"op {op_id} has unsupported pipe")
        _require_integer(op.get("cycles"), f"op {op_id}.cycles")

    for tensor in graph["tensors"]:
        if not isinstance(tensor, Mapping):
            raise _LegalityFailure("invalid_graph", "each tensor must be an object")
        tensor_id = _require_integer(tensor.get("id"), "tensor.id")
        if tensor_id in all_ids:
            raise _LegalityFailure("duplicate_node_id", f"duplicate op/tensor id: {tensor_id}")
        all_ids.add(tensor_id)
        _require_integer(tensor.get("size"), f"tensor {tensor_id}.size")
        if tensor.get("pos") not in VALID_MEMORY_POSITIONS:
            raise _LegalityFailure(
                "invalid_memory_position", f"tensor {tensor_id} has unsupported pos"
            )

    producers: dict[int, set[int]] = defaultdict(set)
    consumers: dict[int, set[int]] = defaultdict(set)
    successors: dict[int, set[int]] = {op_id: set() for op_id in op_ids}
    seen_edges: set[tuple[int, int]] = set()
    full_edges: list[tuple[int, int]] = []
    for edge in graph["edges"]:
        if not isinstance(edge, Mapping):
            raise _LegalityFailure("invalid_graph", "each edge must be an object")
        source = _require_integer(edge.get("source"), "edge.source")
        target = _require_integer(edge.get("target"), "edge.target")
        if source not in all_ids or target not in all_ids:
            raise _LegalityFailure(
                "unknown_edge_endpoint", f"edge references unknown id: {source} -> {target}"
            )
        if source not in op_ids and target not in op_ids:
            raise _LegalityFailure(
                "tensor_to_tensor", f"tensor-to-tensor edge is unsupported: {source} -> {target}"
            )
        if (source, target) in seen_edges:
            raise _LegalityFailure("duplicate_edge", f"duplicate edge: {source} -> {target}")
        seen_edges.add((source, target))
        full_edges.append((source, target))
        if source in op_ids and target in op_ids and source != target:
            successors[source].add(target)
        elif source in op_ids and target not in op_ids:
            producers[target].add(source)
        elif source not in op_ids and target in op_ids:
            consumers[source].add(target)

    full_cycle = _find_cycle(all_ids, full_edges)
    if full_cycle:
        raise _LegalityFailure("input_cycle", f"input graph contains a cycle: {full_cycle}")

    for tensor_id, source_ops in producers.items():
        for source in source_ops:
            successors[source].update(
                target for target in consumers.get(tensor_id, ()) if target != source
            )

    eligible = {op_id for op_id in op_ids if op_type[op_id] not in EXCLUDED_COPY_TYPES}
    contracted: dict[int, set[int]] = {op_id: set() for op_id in eligible}
    for source in eligible:
        stack = list(successors[source])
        visited_excluded: set[int] = set()
        while stack:
            target = stack.pop()
            if target in eligible:
                if target != source:
                    contracted[source].add(target)
                continue
            if target in visited_excluded:
                continue
            visited_excluded.add(target)
            stack.extend(successors.get(target, ()))
    return eligible, contracted


def _normalise_mapping(raw_mapping: Any) -> dict[int, int]:
    if not isinstance(raw_mapping, Mapping):
        raise _LegalityFailure("invalid_mapping", "node_to_subgraph must be an object")
    mapping: dict[int, int] = {}
    for raw_id, subgraph_id in raw_mapping.items():
        if type(raw_id) is int:
            op_id = raw_id
        elif isinstance(raw_id, str) and raw_id.isascii() and raw_id.isdecimal():
            op_id = int(raw_id)
        else:
            raise _LegalityFailure(
                "invalid_mapping_key", "node_to_subgraph keys must be integer op ids"
            )
        if op_id in mapping:
            raise _LegalityFailure(
                "duplicate_mapping", f"duplicate integer op id after parsing: {op_id}"
            )
        if type(subgraph_id) is not int:
            raise _LegalityFailure(
                "invalid_subgraph_id", f"subgraph id for op {op_id} must be an integer"
            )
        if subgraph_id < 0:
            raise _LegalityFailure(
                "invalid_subgraph_id", f"subgraph id for op {op_id} must be non-negative"
            )
        mapping[op_id] = subgraph_id
    return mapping


def _normalise_schedules(raw_schedules: Any) -> list[list[int]]:
    if not isinstance(raw_schedules, list) or not raw_schedules:
        raise _LegalityFailure("invalid_schedule", "core_schedules must be a non-empty list")
    schedules: list[list[int]] = []
    for core_id, order in enumerate(raw_schedules):
        if not isinstance(order, list):
            raise _LegalityFailure(
                "invalid_schedule", f"core_schedules[{core_id}] must be a list"
            )
        if any(type(subgraph_id) is not int for subgraph_id in order):
            raise _LegalityFailure(
                "invalid_schedule", f"core_schedules[{core_id}] must contain integers"
            )
        schedules.append(list(order))
    return schedules


def check_plan_legality(graph: Any, plan: Any, problem: int = 1) -> LegalityReport:
    """Check a plan independently and return all derived structural evidence.

    ``problem`` controls Task composition: problem 1 makes every subgraph a
    separate Task; problems 2/3 merge all subgraphs on the same core.
    """

    report = LegalityReport(details={"problem": problem})
    if problem not in (1, 2, 3):
        report.add_error("invalid_problem", "problem must be 1, 2, or 3")
        return report
    try:
        eligible, contracted = _validate_graph(graph)
        if not isinstance(plan, Mapping) or set(plan) != {
            "node_to_subgraph",
            "core_schedules",
        }:
            raise _LegalityFailure(
                "invalid_plan_fields",
                "plan must contain exactly node_to_subgraph and core_schedules",
            )
        mapping = _normalise_mapping(plan["node_to_subgraph"])
        schedules = _normalise_schedules(plan["core_schedules"])

        missing = sorted(eligible - set(mapping))
        extra = sorted(set(mapping) - eligible)
        if missing or extra:
            raise _LegalityFailure(
                "mapping_coverage",
                f"node_to_subgraph must exactly cover non-COPY ops; missing={missing} extra={extra}",
            )

        subgraphs = set(mapping.values())
        scheduled = [subgraph_id for order in schedules for subgraph_id in order]
        duplicate_sgids = sorted(
            {subgraph_id for subgraph_id in scheduled if scheduled.count(subgraph_id) > 1}
        )
        missing_sgids = sorted(subgraphs - set(scheduled))
        extra_sgids = sorted(set(scheduled) - subgraphs)
        if duplicate_sgids or missing_sgids or extra_sgids:
            raise _LegalityFailure(
                "schedule_coverage",
                "each subgraph must be scheduled exactly once; "
                f"duplicate={duplicate_sgids} missing={missing_sgids} extra={extra_sgids}",
            )

        core_by_subgraph = {
            subgraph_id: core_id
            for core_id, order in enumerate(schedules)
            for subgraph_id in order
        }
        dependency_pairs = sorted(
            {
                (mapping[source], mapping[target])
                for source in eligible
                for target in contracted[source]
                if mapping[source] != mapping[target]
            }
        )
        subgraph_cycle = _find_cycle(subgraphs, dependency_pairs)
        if subgraph_cycle:
            raise _LegalityFailure(
                "subgraph_cycle", f"contracted subgraph graph contains a cycle: {subgraph_cycle}"
            )

        position = {
            subgraph_id: index
            for order in schedules
            for index, subgraph_id in enumerate(order)
        }
        for source, target in dependency_pairs:
            if (
                core_by_subgraph[source] == core_by_subgraph[target]
                and position[source] >= position[target]
            ):
                raise _LegalityFailure(
                    "dependency_order",
                    f"same-core dependency order violation: {source} -> {target}",
                )

        order_edges = [
            (source, target)
            for order in schedules
            for source, target in zip(order, order[1:])
        ]
        combined_cycle = _find_cycle(subgraphs, [*dependency_pairs, *order_edges])
        if combined_cycle:
            if problem == 1:
                raise _LegalityFailure(
                    "task_schedule_cycle",
                    f"dependency plus Task order contains a cycle: {combined_cycle}",
                )
            report.add_warning(
                "potential_execution_cycle",
                "subgraph dependency plus displayed core order is cyclic; Q2/Q3 exact "
                "legality must be decided after official Step3 FIFO/memory edges are built",
            )

        report.details.update(
            {
                "eligible_op_count": len(eligible),
                "subgraph_count": len(subgraphs),
                "num_cores": len(schedules),
                "dependency_pairs": [list(pair) for pair in dependency_pairs],
                "task_count": len(subgraphs) if problem == 1 else len(schedules),
                "task_composition": (
                    "one_subgraph_per_task" if problem == 1 else "one_merged_task_per_core"
                ),
                "combined_order_cycle": combined_cycle,
            }
        )
    except _LegalityFailure as error:
        report.add_error(error.code, str(error))
    return report


def check_execution_graph(
    nodes: Sequence[Hashable],
    dependency_edges: Sequence[tuple[Hashable, Hashable]],
    fifo_edges: Sequence[tuple[Hashable, Hashable]] = (),
    cross_core_edges: Sequence[tuple[Hashable, Hashable]] = (),
) -> LegalityReport:
    """Independently check an already expanded Q2/Q3 execution graph."""

    report = LegalityReport(
        details={
            "node_count": len(nodes),
            "dependency_edge_count": len(dependency_edges),
            "fifo_edge_count": len(fifo_edges),
            "cross_core_edge_count": len(cross_core_edges),
        }
    )
    try:
        cycle = _find_cycle(
            nodes, [*dependency_edges, *fifo_edges, *cross_core_edges]
        )
        report.details["cycle"] = cycle
        if cycle:
            report.add_error("execution_cycle", f"expanded execution graph contains a cycle: {cycle}")
    except _LegalityFailure as error:
        report.add_error(error.code, str(error))
    return report


__all__ = [
    "EXCLUDED_COPY_TYPES",
    "LegalityIssue",
    "LegalityReport",
    "check_execution_graph",
    "check_plan_legality",
]
