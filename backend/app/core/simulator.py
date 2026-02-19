"""
app/services/simulator.py

Core simulation engine for the Mission-System Security Architecture Simulator.

This file is the heart of the backend. It takes an ArchitectureSchema (a
validated JSON description of a mission system) and converts it into a
NetworkX directed graph, then runs attack scenarios against that graph to
produce scored results.

Supported scenarios in Increment 1:
    node_compromise: the target component is compromised and the attack
                     spreads downstream to all dependent components.

Increment 2 will add:
    link_degradation:   a communication link is degraded, affecting only
                        the target component (no downstream propagation).
    insider_tampering:  an insider corrupts a component; spreads downstream
                        with CIA-aware propagation rules.

Graph conventions used throughout this file:
    Nodes   represent architecture components (sensors, compute nodes, etc.)
    Edges   represent directed data flows (source sends data to target)
    Node attributes store the full component metadata (name, type, criticality)
    Edge attributes store flow metadata (cia_requirement, latency_sensitivity)

How to use this module:
    from app.services.simulator import MissionArchitectureSimulator
    from app.models.schemas import ArchitectureSchema

    arch   = ArchitectureSchema(...)
    sim    = MissionArchitectureSimulator(arch)
    result = sim.run_simulation("node_compromise", target_component_id="sensor-1")
"""

from __future__ import annotations

import logging
from typing import Any

# NetworkX is the graph library. We use DiGraph (directed graph) because data
# flows have a direction: data moves FROM source TO target, and attacks
# propagate in the same direction.
import networkx as nx

from app.models.schemas import (
    ArchitectureSchema,
    CriticalityRankEntry,
    SimulationResultSchema,
)

# Module-level logger. Messages appear in the uvicorn terminal output.
# DEBUG messages show detailed graph state; INFO messages show scenario runs.
logger = logging.getLogger(__name__)

# frozenset makes this constant immutable so no code can accidentally add
# or remove scenarios at runtime. Increment 2 will add "link_degradation"
# and "insider_tampering" to this set.
SUPPORTED_SCENARIOS: frozenset[str] = frozenset({"node_compromise"})


class SimulatorError(Exception):
    """
    Raised when a simulation cannot run due to invalid input.

    This is a known, expected error class (bad component IDs, unknown scenario
    names, empty architectures). The router catches it and returns HTTP 422.
    It is intentionally separate from Python's built-in exceptions so the
    router can distinguish "user made a mistake" from "something broke".
    """


class MissionArchitectureSimulator:
    """
    Converts an ArchitectureSchema into a NetworkX DiGraph and runs attack
    scenarios against it.

    The constructor builds the graph immediately on instantiation so that
    all subsequent method calls can assume a valid graph exists. Any
    structural problems with the architecture (missing components referenced
    in flows, empty component list) are caught here and raised as SimulatorError
    before any simulation logic runs.
    """

    def __init__(self, architecture: ArchitectureSchema) -> None:
        # Reject empty architectures immediately rather than letting them
        # cause confusing division-by-zero errors inside calculate_mission_score.
        if not architecture.components:
            raise SimulatorError("Architecture must contain at least one component.")

        # Store the original schema so methods can access metadata like
        # architecture.id when building the result object.
        self.architecture = architecture

        # Build the graph once. All scenario methods share this same graph
        # object rather than rebuilding it on each call.
        self.graph: nx.DiGraph = self._build_graph()

        logger.debug(
            "Graph built: %d nodes, %d edges",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )

    def _build_graph(self) -> nx.DiGraph:
        """
        Convert the ArchitectureSchema into a NetworkX DiGraph.

        Each component becomes a node with its full metadata stored as node
        attributes. Storing metadata on the node means scenario methods can
        look up a component's name, type, or criticality directly from the
        graph without maintaining a separate lookup dictionary.

        Each data flow becomes a directed edge from source to target. Flow
        metadata (cia_requirement, latency_sensitivity) is stored on the edge
        for use in Increment 2's CIA-aware propagation logic.

        Raises SimulatorError if any flow references a component ID that was
        not declared in the components list, because that would produce a
        dangling edge pointing to a nonexistent node.
        """
        graph: nx.DiGraph = nx.DiGraph()

        # Build a set of valid IDs first so edge validation below is O(1)
        # rather than scanning the components list for every flow.
        component_ids: set[str] = set()

        for component in self.architecture.components:
            # The component's id becomes the NetworkX node key. All other
            # fields are stored as attributes so we can retrieve them later
            # when building result objects (attack paths, criticality tables).
            graph.add_node(
                component.id,
                name=component.name,
                type=component.type,
                criticality=component.criticality,
                position=component.position,
            )
            component_ids.add(component.id)

        for flow in self.architecture.flows:
            # Validate both endpoints before adding the edge. NetworkX would
            # silently create new nodes for unknown IDs, which would corrupt
            # the graph by adding ghost nodes not present in the architecture.
            if flow.source not in component_ids:
                raise SimulatorError(
                    f"Data flow '{flow.id}' references unknown source component '{flow.source}'."
                )
            if flow.target not in component_ids:
                raise SimulatorError(
                    f"Data flow '{flow.id}' references unknown target component '{flow.target}'."
                )

            # Store flow metadata on the edge for future CIA-aware propagation.
            graph.add_edge(
                flow.source,
                flow.target,
                flow_id=flow.id,
                data_type=flow.data_type,
                cia_requirement=flow.cia_requirement,
                latency_sensitivity=flow.latency_sensitivity,
            )

        return graph

    def run_simulation(
        self,
        scenario_type: str,
        target_component_id: str,
    ) -> SimulationResultSchema:
        """
        Execute a named attack scenario and return fully scored results.

        This is the main public entry point called by the simulate router.
        It validates the inputs, dispatches to the correct scenario method,
        and returns a SimulationResultSchema that the router serializes to JSON.

        The scenario_type is lowercased and stripped before matching so that
        callers can pass "NODE_COMPROMISE" or "node_compromise" interchangeably.
        """
        # Normalize before matching so the check is case-insensitive.
        scenario_type = scenario_type.lower().strip()

        if scenario_type not in SUPPORTED_SCENARIOS:
            raise SimulatorError(
                f"Unknown scenario '{scenario_type}'. "
                f"Supported: {sorted(SUPPORTED_SCENARIOS)}"
            )

        # Check the target exists in the graph before dispatching to any
        # scenario method, so individual scenario methods don't each need
        # to repeat this guard.
        if target_component_id not in self.graph:
            raise SimulatorError(
                f"Component '{target_component_id}' not found in the architecture."
            )

        logger.info(
            "Running scenario '%s' on target '%s'",
            scenario_type,
            target_component_id,
        )

        if scenario_type == "node_compromise":
            return self._run_node_compromise(target_component_id)

        # This line is unreachable because the SUPPORTED_SCENARIOS guard above
        # would have already raised. It exists to satisfy static type-checkers
        # that require all code paths to return or raise.
        raise SimulatorError(f"Scenario '{scenario_type}' not implemented.")

    def _run_node_compromise(self, target_id: str) -> SimulationResultSchema:
        """
        Simulate a node compromise attack on a single component.

        The targeted component loses integrity and availability. The compromise
        then spreads downstream to every component that depends on the target,
        because they now receive corrupted or unavailable data.

        This method orchestrates the other public methods rather than
        implementing logic itself, so each piece (propagation, scoring,
        ranking) can be tested in isolation.
        """
        # Find every component affected by the compromise (target + descendants).
        affected_ids: set[str] = self.propagate_compromise(target_id)

        # Calculate scores before and after. Passing an empty set to
        # calculate_mission_score gives us the baseline (no compromised nodes).
        baseline_score = self.calculate_mission_score(set())
        compromised_score = self.calculate_mission_score(affected_ids)

        # score_delta will be negative when an attack degrades the mission,
        # which is the expected case. A positive delta would mean the attack
        # somehow improved the mission, which should never happen.
        score_delta = compromised_score - baseline_score

        attack_path = self._build_attack_path(target_id, affected_ids)
        explanation = self._build_explanation(
            scenario_type="node_compromise",
            target_id=target_id,
            affected_ids=affected_ids,
            baseline_score=baseline_score,
            compromised_score=compromised_score,
        )

        # Build human-readable names parallel to the affected_ids list so the
        # frontend doesn't have to do its own ID-to-name resolution.
        affected_names = [
            self.graph.nodes[nid].get("name", nid)
            for nid in affected_ids
            if nid in self.graph
        ]

        criticality_ranking = self.rank_criticality(affected_ids)

        return SimulationResultSchema(
            # Fall back to 0 if the architecture hasn't been saved to DB yet
            # (id would be None for an unsaved architecture).
            architecture_id=self.architecture.id or 0,
            scenario_type="node_compromise",
            target_component_id=target_id,
            baseline_score=baseline_score,
            compromised_score=compromised_score,
            score_delta=score_delta,
            affected_components=list(affected_ids),
            affected_component_names=affected_names,
            attack_path=attack_path,
            explanation=explanation,
            criticality_ranking=criticality_ranking,
        )

    def propagate_compromise(self, compromised_node_id: str) -> set[str]:
        """
        Return the full set of components affected by compromising one node.

        Uses nx.descendants() which performs a BFS/DFS traversal from the
        starting node and returns all reachable nodes. Because NetworkX tracks
        visited nodes internally, this handles cycles in the graph without
        entering an infinite loop.

        The compromised node itself is included in the return value because it
        is always affected (it was directly attacked).

        This method is public so tests can call it directly without going
        through run_simulation(), making it easy to verify propagation
        behavior in isolation.
        """
        if compromised_node_id not in self.graph:
            # Log a warning rather than raising so callers that don't need
            # strict validation can handle an empty result gracefully.
            logger.warning("propagate_compromise: node '%s' not in graph", compromised_node_id)
            return set()

        # nx.descendants returns only the reachable nodes, not the start node,
        # so we add the start node explicitly with set union.
        descendants: set[str] = nx.descendants(self.graph, compromised_node_id)
        affected = descendants | {compromised_node_id}

        logger.debug(
            "Node '%s' compromise affects %d component(s): %s",
            compromised_node_id,
            len(affected),
            affected,
        )
        return affected

    def calculate_mission_score(self, affected_ids: set[str]) -> float:
        """
        Return mission success as a percentage of healthy components.

        Formula:
            score = (healthy_components / total_components) * 100

        A score of 100.0 means all components are healthy (baseline state).
        A score of 0.0 means all components are compromised (mission failed).

        This method is public so tests can verify scoring math directly
        without constructing a full simulation result.
        """
        total = self.graph.number_of_nodes()

        # The __init__ guard prevents empty architectures from reaching here,
        # but we handle the zero case defensively to avoid ZeroDivisionError.
        if total == 0:
            return 0.0

        healthy = total - len(affected_ids)

        # Clamp healthy to [0, total] in case affected_ids contains IDs that
        # are not in the graph (e.g. stale IDs passed from an old result).
        healthy = max(0, min(healthy, total))

        score = (healthy / total) * 100.0
        logger.debug("Mission score: %d healthy / %d total = %.2f%%", healthy, total, score)

        # Round to 2 decimal places to avoid floating-point noise in responses
        # like 66.66666666667 instead of 66.67.
        return round(score, 2)

    def rank_criticality(
        self,
        affected_ids: set[str] | None = None,
        top_n: int = 10,
    ) -> list[CriticalityRankEntry]:
        """
        Rank all components by a composite criticality score and return the top N.

        Composite score formula:
            criticality_score = user_criticality + graph_in_degree

        Where:
            user_criticality  is the 1-10 value the planner assigned in the UI
            graph_in_degree   is how many other components send data INTO this one
                              (more dependencies = higher structural importance)

        Ties are broken by descendant count: a component that many others depend
        on downstream ranks higher than one with the same score but fewer dependents.

        This method is public so tests can verify ranking logic in isolation
        and so Increment 2 can call it from new scenario methods.
        """
        affected = affected_ids or set()

        # Each entry is (composite_score, descendant_count, node_id).
        # Storing all three lets us sort on multiple keys in one pass.
        entries: list[tuple[float, int, str]] = []

        for node_id, attrs in self.graph.nodes(data=True):
            user_crit: int = attrs.get("criticality", 5)
            in_deg: int = self.graph.in_degree(node_id)
            desc_count: int = len(nx.descendants(self.graph, node_id))
            composite = float(user_crit + in_deg)
            entries.append((composite, desc_count, node_id))

        # Sort descending on composite score first, then descendant count as
        # the tie-breaker. reverse=True makes the highest scores appear first.
        entries.sort(key=lambda t: (t[0], t[1]), reverse=True)

        result: list[CriticalityRankEntry] = []
        for composite, _desc, node_id in entries[:top_n]:
            attrs = self.graph.nodes[node_id]
            result.append(
                CriticalityRankEntry(
                    component_id=node_id,
                    component_name=attrs.get("name", node_id),
                    component_type=attrs.get("type", "Unknown"),
                    criticality_score=composite,
                    # The affected flag lets the frontend highlight compromised
                    # rows in red in the criticality ranking table.
                    affected=node_id in affected,
                )
            )

        return result

    def _build_attack_path(
        self,
        target_id: str,
        affected_ids: set[str],
    ) -> list[str]:
        """
        Generate an ordered list of strings describing how the compromise spread.

        Uses BFS (breadth-first search) from the target node so that steps
        appear in the order the compromise actually propagated: direct neighbors
        first, then their neighbors, and so on. This matches the intuitive
        reading order a mission planner would expect.

        Only nodes in affected_ids are included in the path. This matters for
        CIA-aware propagation in Increment 2, where not every successor of the
        target will necessarily be affected.
        """
        path: list[str] = []

        target_name = self.graph.nodes[target_id].get("name", target_id)
        target_type = self.graph.nodes[target_id].get("type", "Component")

        # Step 1 is always the directly compromised node.
        path.append(f"Step 1: {target_type} '{target_name}' directly compromised (integrity loss)")

        step = 2
        visited: set[str] = {target_id}
        queue: list[str] = [target_id]

        # Standard BFS: process each node in the queue, enqueue its unvisited
        # successors that are in the affected set.
        while queue:
            current = queue.pop(0)
            for successor in self.graph.successors(current):
                if successor not in visited and successor in affected_ids:
                    visited.add(successor)
                    queue.append(successor)

                    s_name = self.graph.nodes[successor].get("name", successor)
                    s_type = self.graph.nodes[successor].get("type", "Component")
                    current_name = self.graph.nodes[current].get("name", current)

                    path.append(
                        f"Step {step}: {s_type} '{s_name}' receives corrupted data "
                        f"from '{current_name}'"
                    )
                    step += 1

        # Add a final summary step when more than one component was affected,
        # so the mission planner sees the overall impact in the attack path list.
        if len(affected_ids) > 1:
            path.append(
                f"Step {step}: Mission objective degraded due to "
                f"{len(affected_ids)} compromised components"
            )

        return path

    def _build_explanation(
        self,
        scenario_type: str,
        target_id: str,
        affected_ids: set[str],
        baseline_score: float,
        compromised_score: float,
    ) -> str:
        """
        Build a single human-readable sentence summarizing the attack outcome.

        This string is shown at the top of the results panel in the frontend.
        It is intentionally brief: one sentence covering what was attacked,
        whether it spread, and the score impact. The attack_path list provides
        the detailed step-by-step breakdown.
        """
        target_name = self.graph.nodes[target_id].get("name", target_id)
        delta = abs(baseline_score - compromised_score)

        # others is the set of components affected beyond the target itself.
        others = affected_ids - {target_id}

        # Choose the propagation clause based on whether the compromise spread.
        propagation = (
            f" Compromise propagated to {len(others)} downstream component(s)."
            if others
            else " No downstream propagation (isolated node)."
        )

        return (
            f"Node compromise on '{target_name}'."
            f"{propagation}"
            f" Mission success score degraded from {baseline_score:.1f}% to "
            f"{compromised_score:.1f}% (\u2013{delta:.1f} percentage points)."
        )

    def get_component_metadata(self, component_id: str) -> dict[str, Any]:
        """
        Return a copy of the attribute dict for a single component node.

        Useful for debugging and for future endpoints that need to inspect
        individual component properties without running a full simulation.
        Returns a copy (not a reference) so callers cannot accidentally
        mutate the graph's internal state.
        """
        if component_id not in self.graph:
            raise SimulatorError(f"Component '{component_id}' not found.")
        return dict(self.graph.nodes[component_id])

    def node_count(self) -> int:
        """Return the total number of components in the graph."""
        return self.graph.number_of_nodes()

    def edge_count(self) -> int:
        """Return the total number of data flows in the graph."""
        return self.graph.number_of_edges()