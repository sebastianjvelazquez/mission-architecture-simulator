"""
app/core/mitigations.py

"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class MitigationSuggestion:
    """A single rule-based mitigation recommendation."""

    # Machine-readable type, used by the frontend to icon-code the suggestion.
    type: str  # "redundancy" | "segmentation" | "validation_gate" | "segmentation_cascade"

    # The component the mitigation should be applied to or near.
    affected_component_id: str
    affected_component_name: str

    # Human-readable explanation shown in the results panel.
    description: str

    # Conservative estimate of mission-score improvement (0-100 %).
    expected_score_improvement: float

    # Extra structured metadata the frontend can use for rendering.
    details: dict[str, Any] = field(default_factory=dict)


def suggest_mitigations(
    graph: nx.DiGraph,
    components: dict[str, dict[str, Any]],
) -> list[MitigationSuggestion]:
    """
    Run all mitigation rules against the architecture graph.
    """
    suggestions: list[MitigationSuggestion] = []
    total_nodes = len(graph.nodes)

    if total_nodes == 0:
        return suggestions

    for node_id in graph.nodes:
        comp = components.get(node_id, {})
        name = comp.get("name", node_id)
        crit = comp.get("criticality", 5)
        comp_type = comp.get("type", "")
        predecessors = list(graph.predecessors(node_id))
        successors = list(graph.successors(node_id))
        descendants = set(nx.descendants(graph, node_id))

        # RULE-1: Single point of failure
        if len(predecessors) == 0 and len(descendants) >= 1:
            cascade_fraction = len(descendants) / total_nodes
            improvement = round(min(cascade_fraction * 80, 40), 1)
            suggestions.append(
                MitigationSuggestion(
                    type="redundancy",
                    affected_component_id=node_id,
                    affected_component_name=name,
                    description=(
                        f"'{name}' is a single point of failure with no redundant input path. "
                        f"Compromise propagates to {len(descendants)} downstream component(s). "
                        "Recommendation: add a parallel redundant component or path."
                    ),
                    expected_score_improvement=improvement,
                    details={
                        "downstream_count": len(descendants),
                        "cascade_fraction": round(cascade_fraction, 2),
                    },
                )
            )

        # RULE-2: Critical node directly exposed to external input
        external_predecessors = [
            p for p in predecessors
            if components.get(p, {}).get("type", "") == "External"
        ]
        if (len(predecessors) == 0 or external_predecessors) and crit >= 7:
            suggestions.append(
                MitigationSuggestion(
                    type="segmentation",
                    affected_component_id=node_id,
                    affected_component_name=name,
                    description=(
                        f"High-criticality component '{name}' (criticality={crit}) "
                        "is directly reachable from an external boundary. "
                        "Recommendation: insert a network segmentation boundary or "
                        "firewall between external inputs and this component."
                    ),
                    expected_score_improvement=15.0,
                    details={
                        "criticality": crit,
                        "external_predecessors": external_predecessors,
                    },
                )
            )

        # RULE-3: Integrity flow without validation gate
        for predecessor in predecessors:
            edge_data = graph.get_edge_data(predecessor, node_id) or {}
            if edge_data.get("cia_requirement") == "integrity":
                # Check if any predecessor is already a validation type
                has_validation = any(
                    components.get(p, {}).get("type", "") in {"Validation", "ValidationGate"}
                    for p in predecessors
                )
                if not has_validation:
                    suggestions.append(
                        MitigationSuggestion(
                            type="validation_gate",
                            affected_component_id=node_id,
                            affected_component_name=name,
                            description=(
                                f"Data flow into '{name}' requires integrity but has no "
                                "validation gate. Tampered data will reach this component "
                                "undetected. "
                                "Recommendation: add an input validation gate upstream of "
                                f"'{name}'."
                            ),
                            expected_score_improvement=20.0,
                            details={
                                "upstream_component_id": predecessor,
                                "cia_requirement": "integrity",
                            },
                        )
                    )
                    break  # One suggestion per target is enough

        # RULE-4: Cascade hub (large blast radius)
        if len(descendants) > total_nodes / 2 and total_nodes > 2:
            suggestions.append(
                MitigationSuggestion(
                    type="segmentation_cascade",
                    affected_component_id=node_id,
                    affected_component_name=name,
                    description=(
                        f"Compromising '{name}' cascades to {len(descendants)} of "
                        f"{total_nodes} components ({round(len(descendants)/total_nodes*100)}%). "
                        "Recommendation: introduce network segmentation to limit the "
                        "blast radius and contain potential compromise."
                    ),
                    expected_score_improvement=round(len(descendants) / total_nodes * 50, 1),
                    details={
                        "descendant_count": len(descendants),
                        "total_components": total_nodes,
                    },
                )
            )

        # RULE-5: High-criticality node with single upstream path
        if crit >= 8 and len(predecessors) == 1:
            suggestions.append(
                MitigationSuggestion(
                    type="redundancy",
                    affected_component_id=node_id,
                    affected_component_name=name,
                    description=(
                        f"High-criticality component '{name}' (criticality={crit}) "
                        "has only one upstream data source. Any failure in that source "
                        "immediately degrades this component. "
                        "Recommendation: add a redundant upstream data source."
                    ),
                    expected_score_improvement=10.0,
                    details={
                        "criticality": crit,
                        "upstream_count": len(predecessors),
                    },
                )
            )

    # De-duplicate and sort: highest expected improvement first
    seen: set[tuple[str, str]] = set()
    unique: list[MitigationSuggestion] = []
    for s in sorted(suggestions, key=lambda x: -x.expected_score_improvement):
        key = (s.type, s.affected_component_id)
        if key not in seen:
            seen.add(key)
            unique.append(s)

    logger.debug("Mitigation suggester fired %d rule(s) for %d component(s)", len(unique), total_nodes)
    return unique