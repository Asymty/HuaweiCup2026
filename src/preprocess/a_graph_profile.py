"""Profile the official A-problem graphs without changing them."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


def profile_graph(path: Path) -> dict:
    graph = json.loads(path.read_text(encoding="utf-8"))
    ops, tensors, edges = graph["ops"], graph["tensors"], graph["edges"]
    op_ids = {op["id"] for op in ops}
    producers = defaultdict(set)
    consumers = defaultdict(set)
    successors = {op_id: set() for op_id in op_ids}
    incident = Counter()
    for edge in edges:
        source, target = edge["source"], edge["target"]
        incident[source] += 1
        incident[target] += 1
        if source in op_ids and target in op_ids:
            successors[source].add(target)
        elif source in op_ids:
            producers[target].add(source)
        elif target in op_ids:
            consumers[source].add(target)
    for tensor_id, sources in producers.items():
        for source in sources:
            successors[source].update(consumers.get(tensor_id, ()))
            successors[source].discard(source)
    indegree = {op_id: 0 for op_id in op_ids}
    for targets in successors.values():
        for target in targets:
            indegree[target] += 1
    roots = sum(value == 0 for value in indegree.values())
    queue = deque(op_id for op_id, value in indegree.items() if value == 0)
    depth = {op_id: 1 for op_id in queue}
    visited = 0
    while queue:
        source = queue.popleft()
        visited += 1
        for target in successors[source]:
            depth[target] = max(depth.get(target, 1), depth[source] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(ops):
        raise ValueError(f"op dependency cycle in {path}")
    eligible = [op for op in ops if op.get("op") not in {"COPY_IN", "COPY_OUT"}]
    tensor_bytes = sum(tensor["size"] for tensor in tensors)
    return {
        "case_id": path.stem,
        "input_path": str(path.resolve()),
        "input_bytes": path.stat().st_size,
        "op_count": len(ops),
        "eligible_op_count": len(eligible),
        "copy_op_count": len(ops) - len(eligible),
        "tensor_count": len(tensors),
        "edge_count": len(edges),
        "op_dependency_count": sum(map(len, successors.values())),
        "root_op_count": roots,
        "dag_depth": max(depth.values(), default=0),
        "max_out_degree": max(map(len, successors.values()), default=0),
        "max_node_edge_degree": max(incident.values(), default=0),
        "tensor_bytes": tensor_bytes,
        "max_tensor_bytes": max((tensor["size"] for tensor in tensors), default=0),
        "op_cycles": sum(op.get("cycles", 0) for op in ops),
    }


def profile_directory(graph_dir: Path, output_dir: Path) -> list[dict]:
    paths = sorted(graph_dir.glob("case_*.json"))
    if len(paths) != 100:
        raise ValueError(f"expected 100 graphs in {graph_dir}; found {len(paths)}")
    rows = [profile_graph(path) for path in paths]
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "profile.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (output_dir / "profile.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("result/a_graph_profile"))
    args = parser.parse_args()
    rows = profile_directory(args.graph_dir, args.output_dir)
    print(f"profiled {len(rows)} graphs: {args.output_dir / 'profile.csv'}")


if __name__ == "__main__":
    main()
