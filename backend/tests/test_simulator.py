"""
tests/test_simulator.py

Unit and integration tests for app/services/simulator.py.

These tests call the simulator directly without going through HTTP, which
makes them faster and more focused than the API tests in test_api.py.
When a test fails here, you know the problem is in the simulation logic
itself, not in routing, serialization, or middleware.

Covers:
    - Graph construction (nodes, edges, attributes)
    - propagate_compromise() including edge cases
    - calculate_mission_score()
    - rank_criticality()
    - run_simulation() full scenario execution
    - SimulatorError raised on invalid inputs
    - Attack path and explanation generation
    - Large-graph performance benchmark
"""

from __future__ import annotations

import time

import pytest

from app.models.schemas import ArchitectureSchema, ComponentSchema, DataFlowSchema
from app.services.simulator import (
    MissionArchitectureSimulator,
    SimulatorError,
    SUPPORTED_SCENARIOS,
)


# Helper functions used by multiple tests and fixtures.
# These live at module level rather than inside a class so any fixture
# or test can call them without instantiating anything first.

def make_component(
    id: str,
    name: str | None = None,
    type: str = "Sensor",
    criticality: int = 5,
) -> ComponentSchema:
    """
    Create a ComponentSchema with sensible defaults.

    Using a helper instead of constructing ComponentSchema inline in every
    test keeps tests short and makes the important values (id, criticality)
    stand out clearly.
    """
    return ComponentSchema(
        id=id,
        name=name or id,   # Fall back to using the ID as the name if none given
        type=type,
        criticality=criticality,
        position={"x": 0.0, "y": 0.0},
    )


def make_flow(
    source: str,
    target: str,
    id: str | None = None,
    cia: str | None = None,
) -> DataFlowSchema:
    """
    Create a DataFlowSchema with an auto-generated ID if none is provided.

    The auto-generated ID format (flow-source-target) makes test output
    easier to read when a flow is referenced in an error message.
    """
    return DataFlowSchema(
        id=id or f"flow-{source}-{target}",
        source=source,
        target=target,
        cia_requirement=cia,
    )


def make_arch(
    components,
    flows=None,
    arch_id: int = 1,
) -> ArchitectureSchema:
    """
    Create an ArchitectureSchema from component and flow lists.

    arch_id defaults to 1 so result objects have a non-zero architecture_id
    without needing to specify it in every test.
    """
    return ArchitectureSchema(
        id=arch_id,
        name="Test Architecture",
        components=components,
        flows=flows or [],
    )


# Pytest fixtures define reusable architecture objects shared across test classes.
# Each fixture is recreated fresh for every test that uses it, so one test
# cannot corrupt the graph state seen by another test.

@pytest.fixture
def linear_arch():
    """
    A simple three-node chain: A -> B -> C.

    This is the most common fixture. Compromising A should affect all three
    nodes. Compromising B should affect B and C but not A. Compromising C
    should affect only C (leaf node).
    """
    return make_arch(
        components=[
            make_component("A", "Node-A", "Sensor", criticality=7),
            make_component("B", "Node-B", "Compute", criticality=8),
            make_component("C", "Node-C", "Control", criticality=9),
        ],
        flows=[
            make_flow("A", "B"),
            make_flow("B", "C"),
        ],
    )


@pytest.fixture
def branching_arch():
    """
    A branching graph: root -> branch1, root -> branch2, branch1 -> leaf.

    Useful for testing that compromise follows all branches from a split
    point, and that compromising one branch does not affect the other.

        root
        /  \\
    branch1  branch2
       |
      leaf
    """
    return make_arch(
        components=[
            make_component("root", "Root", "Sensor"),
            make_component("branch1", "Branch1", "Compute"),
            make_component("branch2", "Branch2", "Compute"),
            make_component("leaf", "Leaf", "Control"),
        ],
        flows=[
            make_flow("root", "branch1"),
            make_flow("root", "branch2"),
            make_flow("branch1", "leaf"),
        ],
    )


@pytest.fixture
def single_node_arch():
    """
    An architecture with exactly one component and no data flows.

    Tests the edge case where the compromised node has no descendants,
    so the affected set should contain only the node itself.
    """
    return make_arch(components=[make_component("solo", "Solo", "Storage")])


@pytest.fixture
def disconnected_arch():
    """
    Two independent subgraphs with no connection between them: a1->a2 and b1->b2.

    Tests that a compromise in one subgraph does not propagate across to the
    other, which would happen if the traversal incorrectly explored the whole graph.
    """
    return make_arch(
        components=[
            make_component("a1", "A1"),
            make_component("a2", "A2"),
            make_component("b1", "B1"),
            make_component("b2", "B2"),
        ],
        flows=[
            make_flow("a1", "a2"),
            make_flow("b1", "b2"),
        ],
    )


class TestGraphConstruction:
    """
    Tests that _build_graph() correctly converts ArchitectureSchema into a
    NetworkX DiGraph with the right nodes, edges, and attributes.

    These tests inspect the graph object directly (sim.graph) rather than
    going through the simulation methods, so they can catch graph-building
    bugs without any simulation logic getting in the way.
    """

    def test_node_count_matches_components(self, linear_arch):
        # The graph must have exactly one node per component, no more, no less.
        sim = MissionArchitectureSimulator(linear_arch)
        assert sim.node_count() == 3

    def test_edge_count_matches_flows(self, linear_arch):
        # The graph must have exactly one edge per data flow.
        sim = MissionArchitectureSimulator(linear_arch)
        assert sim.edge_count() == 2

    def test_node_attributes_stored(self, linear_arch):
        # Component metadata must survive the conversion into a graph node so
        # result-building methods can look it up without a separate data structure.
        sim = MissionArchitectureSimulator(linear_arch)
        attrs = sim.graph.nodes["A"]
        assert attrs["name"] == "Node-A"
        assert attrs["type"] == "Sensor"
        assert attrs["criticality"] == 7

    def test_edge_direction_preserved(self, linear_arch):
        # Edges must be directed: A->B exists but B->A must not, because
        # attack propagation only travels in the data-flow direction.
        sim = MissionArchitectureSimulator(linear_arch)
        assert sim.graph.has_edge("A", "B")
        assert sim.graph.has_edge("B", "C")
        assert not sim.graph.has_edge("C", "A")

    def test_single_node_graph(self, single_node_arch):
        # A one-component architecture with no flows should produce a graph
        # with one node and zero edges.
        sim = MissionArchitectureSimulator(single_node_arch)
        assert sim.node_count() == 1
        assert sim.edge_count() == 0

    def test_edge_attributes_stored(self):
        # Flow metadata (cia_requirement, etc.) must be stored on the edge
        # so CIA-aware propagation in Increment 2 can read it.
        arch = make_arch(
            components=[make_component("x"), make_component("y")],
            flows=[make_flow("x", "y", cia="integrity")],
        )
        sim = MissionArchitectureSimulator(arch)
        edge = sim.graph.edges["x", "y"]
        assert edge["cia_requirement"] == "integrity"

    def test_branching_graph_two_edges_from_root(self, branching_arch):
        # The root node should have exactly two outgoing edges (to branch1 and branch2).
        sim = MissionArchitectureSimulator(branching_arch)
        successors = list(sim.graph.successors("root"))
        assert set(successors) == {"branch1", "branch2"}

    def test_raises_on_empty_components(self):
        # An architecture with no components is invalid. The error should be
        # caught at construction time, not later during simulation.
        with pytest.raises(SimulatorError, match="at least one component"):
            MissionArchitectureSimulator(make_arch(components=[]))

    def test_raises_on_unknown_source_in_flow(self):
        # A flow whose source doesn't exist in the component list must be
        # rejected. Without this check, NetworkX would silently create a ghost node.
        arch = make_arch(
            components=[make_component("x")],
            flows=[make_flow("GHOST", "x")],
        )
        with pytest.raises(SimulatorError, match="unknown source"):
            MissionArchitectureSimulator(arch)

    def test_raises_on_unknown_target_in_flow(self):
        # Same guard for the target endpoint of a flow.
        arch = make_arch(
            components=[make_component("x")],
            flows=[make_flow("x", "GHOST")],
        )
        with pytest.raises(SimulatorError, match="unknown target"):
            MissionArchitectureSimulator(arch)

    def test_get_component_metadata(self, linear_arch):
        # get_component_metadata should return the stored attribute dict for a
        # valid component ID.
        sim = MissionArchitectureSimulator(linear_arch)
        meta = sim.get_component_metadata("B")
        assert meta["name"] == "Node-B"
        assert meta["criticality"] == 8

    def test_get_component_metadata_unknown_raises(self, linear_arch):
        # Requesting metadata for a nonexistent ID should raise SimulatorError,
        # not a KeyError from NetworkX internals.
        sim = MissionArchitectureSimulator(linear_arch)
        with pytest.raises(SimulatorError):
            sim.get_component_metadata("UNKNOWN")


class TestPropagateCompromise:
    """
    Tests for propagate_compromise(), the core graph traversal algorithm.

    Each test focuses on one structural property of the graph to verify that
    propagation follows directed edges correctly and handles edge cases cleanly.
    """

    def test_linear_full_chain_from_root(self, linear_arch):
        # Compromising the root of A->B->C should affect all three nodes
        # because B and C are both reachable downstream from A.
        sim = MissionArchitectureSimulator(linear_arch)
        affected = sim.propagate_compromise("A")
        assert affected == {"A", "B", "C"}

    def test_linear_middle_node_propagates_downstream_only(self, linear_arch):
        # Compromising B in A->B->C should affect B and C but NOT A,
        # because edges are directed and A is upstream of B, not downstream.
        sim = MissionArchitectureSimulator(linear_arch)
        affected = sim.propagate_compromise("B")
        assert affected == {"B", "C"}
        assert "A" not in affected

    def test_linear_leaf_node_only_itself(self, linear_arch):
        # C has no outgoing edges so compromising it affects only itself.
        sim = MissionArchitectureSimulator(linear_arch)
        affected = sim.propagate_compromise("C")
        assert affected == {"C"}

    def test_isolated_node_only_itself(self, single_node_arch):
        # An isolated node with no edges in or out affects only itself.
        sim = MissionArchitectureSimulator(single_node_arch)
        affected = sim.propagate_compromise("solo")
        assert affected == {"solo"}

    def test_branching_root_affects_all(self, branching_arch):
        # Compromising the root reaches both branches and the leaf
        # because all four nodes are reachable downstream.
        sim = MissionArchitectureSimulator(branching_arch)
        affected = sim.propagate_compromise("root")
        assert affected == {"root", "branch1", "branch2", "leaf"}

    def test_branching_branch1_affects_leaf(self, branching_arch):
        # branch1 feeds into leaf, so both are affected.
        # root and branch2 are upstream or on a separate path, so neither is affected.
        sim = MissionArchitectureSimulator(branching_arch)
        affected = sim.propagate_compromise("branch1")
        assert affected == {"branch1", "leaf"}
        assert "root" not in affected
        assert "branch2" not in affected

    def test_branching_branch2_affects_only_itself(self, branching_arch):
        # branch2 has no outgoing edges so it only affects itself.
        sim = MissionArchitectureSimulator(branching_arch)
        affected = sim.propagate_compromise("branch2")
        assert affected == {"branch2"}

    def test_disconnected_graph_contains_attack_within_subgraph(self, disconnected_arch):
        # Compromising a1 should spread to a2 but must not cross into the
        # b1->b2 subgraph, which has no connection to the a subgraph.
        sim = MissionArchitectureSimulator(disconnected_arch)
        affected = sim.propagate_compromise("a1")
        assert affected == {"a1", "a2"}
        assert "b1" not in affected

    def test_returns_set_not_list(self, linear_arch):
        # The return type must be a set, not a list, because set membership
        # checks (node in affected) are O(1) vs O(n) for lists.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.propagate_compromise("A")
        assert isinstance(result, set)

    def test_always_includes_compromised_node(self, linear_arch):
        # The directly attacked node must always appear in the result,
        # even if it has no downstream descendants.
        sim = MissionArchitectureSimulator(linear_arch)
        for node in ["A", "B", "C"]:
            affected = sim.propagate_compromise(node)
            assert node in affected

    def test_unknown_node_returns_empty_set(self, linear_arch):
        # An unknown node ID should return an empty set and log a warning,
        # not raise an exception, so callers can handle it gracefully.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.propagate_compromise("DOES_NOT_EXIST")
        assert result == set()

    def test_cycle_handled_gracefully(self):
        # NetworkX descendants() tracks visited nodes internally, so cycles
        # are traversed without entering an infinite loop.
        # Graph: x -> y -> z -> x (full cycle)
        arch = make_arch(
            components=[
                make_component("x"),
                make_component("y"),
                make_component("z"),
            ],
            flows=[
                make_flow("x", "y"),
                make_flow("y", "z"),
                make_flow("z", "x"),   # closes the cycle back to x
            ],
        )
        sim = MissionArchitectureSimulator(arch)
        affected = sim.propagate_compromise("x")
        # All three nodes are reachable from x via the cycle.
        assert affected == {"x", "y", "z"}


class TestCalculateMissionScore:
    """
    Tests for calculate_mission_score(), which converts a set of compromised
    component IDs into a 0-100 percentage score.

    Formula: (healthy / total) * 100
    """

    def test_baseline_is_100(self, linear_arch):
        # Passing an empty set means no compromised nodes, so all three are
        # healthy and the score should be 100%.
        sim = MissionArchitectureSimulator(linear_arch)
        score = sim.calculate_mission_score(set())
        assert score == 100.0

    def test_all_compromised_is_zero(self, linear_arch):
        # All three components compromised means zero healthy, so score is 0%.
        sim = MissionArchitectureSimulator(linear_arch)
        score = sim.calculate_mission_score({"A", "B", "C"})
        assert score == 0.0

    def test_one_of_three_affected(self, linear_arch):
        # 2 healthy out of 3 total = 66.67%
        sim = MissionArchitectureSimulator(linear_arch)
        score = sim.calculate_mission_score({"A"})
        assert abs(score - 66.67) < 0.1

    def test_two_of_three_affected(self, linear_arch):
        # 1 healthy out of 3 total = 33.33%
        sim = MissionArchitectureSimulator(linear_arch)
        score = sim.calculate_mission_score({"A", "B"})
        assert abs(score - 33.33) < 0.1

    def test_score_returns_float(self, linear_arch):
        # The return type must be float (not int) for consistent JSON serialization.
        sim = MissionArchitectureSimulator(linear_arch)
        score = sim.calculate_mission_score(set())
        assert isinstance(score, float)

    def test_score_range_always_0_to_100(self, branching_arch):
        # Scores must always stay within [0, 100] regardless of the input set.
        sim = MissionArchitectureSimulator(branching_arch)
        all_ids = set(sim.graph.nodes())
        assert 0.0 <= sim.calculate_mission_score(all_ids) <= 100.0
        assert 0.0 <= sim.calculate_mission_score(set()) <= 100.0

    def test_single_node_baseline_is_100(self, single_node_arch):
        # A single healthy node should score 100%.
        sim = MissionArchitectureSimulator(single_node_arch)
        assert sim.calculate_mission_score(set()) == 100.0

    def test_single_node_compromised_is_zero(self, single_node_arch):
        # A single compromised node means zero healthy components, so score is 0%.
        sim = MissionArchitectureSimulator(single_node_arch)
        assert sim.calculate_mission_score({"solo"}) == 0.0

    def test_four_nodes_half_affected(self, disconnected_arch):
        # 2 compromised out of 4 total = exactly 50%.
        sim = MissionArchitectureSimulator(disconnected_arch)
        score = sim.calculate_mission_score({"a1", "a2"})
        assert score == 50.0


class TestRankCriticality:
    """
    Tests for rank_criticality(), which scores and sorts components by their
    structural importance to the mission.

    Composite score = user_criticality + graph_in_degree.
    Ties broken by descendant count.
    """

    def test_returns_list(self, linear_arch):
        # Return type must be a list so the frontend can iterate it in order.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.rank_criticality()
        assert isinstance(result, list)

    def test_length_equals_node_count_when_fewer_than_top_n(self, linear_arch):
        # With 3 nodes and a default top_n of 10, all 3 nodes should be returned.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.rank_criticality()
        assert len(result) == 3

    def test_affected_flag_set_correctly(self, linear_arch):
        # Components in the affected_ids set should have affected=True.
        # Components not in the set should have affected=False.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.rank_criticality(affected_ids={"A", "B"})
        flags = {e.component_id: e.affected for e in result}
        assert flags["A"] is True
        assert flags["B"] is True
        assert flags["C"] is False

    def test_sorted_descending_by_criticality_score(self, linear_arch):
        # The list must be sorted from highest to lowest criticality score
        # so the frontend can display the most critical components first.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.rank_criticality()
        scores = [e.criticality_score for e in result]
        assert scores == sorted(scores, reverse=True)

    def test_criticality_entry_has_required_fields(self, linear_arch):
        # Each entry must have all five fields that the frontend table expects.
        sim = MissionArchitectureSimulator(linear_arch)
        entry = sim.rank_criticality()[0]
        assert hasattr(entry, "component_id")
        assert hasattr(entry, "component_name")
        assert hasattr(entry, "component_type")
        assert hasattr(entry, "criticality_score")
        assert hasattr(entry, "affected")

    def test_top_n_limits_results(self, linear_arch):
        # Passing top_n=1 should return exactly one entry even though there
        # are 3 nodes in the graph.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.rank_criticality(top_n=1)
        assert len(result) == 1

    def test_no_affected_ids_all_false(self, linear_arch):
        # When affected_ids is None (baseline, no attack run yet), all
        # entries should have affected=False.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.rank_criticality(affected_ids=None)
        assert all(not e.affected for e in result)

    def test_high_criticality_component_ranks_first(self):
        # The component with the highest user-assigned criticality should
        # appear first in the ranking when all other factors are equal.
        arch = make_arch(
            components=[
                make_component("low", criticality=1),
                make_component("high", criticality=10),
                make_component("mid", criticality=5),
            ],
        )
        sim = MissionArchitectureSimulator(arch)
        result = sim.rank_criticality()
        assert result[0].component_id == "high"


class TestRunSimulation:
    """
    Integration tests for run_simulation(), which orchestrates the full
    simulation pipeline from architecture input to SimulationResultSchema output.

    These tests treat run_simulation() as a black box and verify that the
    output satisfies the contracts expected by the router and the frontend.
    """

    def test_node_compromise_returns_result_schema(self, linear_arch):
        # The return value must be a SimulationResultSchema instance so FastAPI
        # can serialize it to JSON correctly.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        from app.models.schemas import SimulationResultSchema
        assert isinstance(result, SimulationResultSchema)

    def test_baseline_score_is_100(self, linear_arch):
        # Baseline score must always be 100 because we pass an empty affected
        # set to calculate_mission_score() before any compromise is applied.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "C")
        assert result.baseline_score == 100.0

    def test_score_decreases_after_attack(self, linear_arch):
        # Any attack that affects at least one component must lower the score.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert result.compromised_score < result.baseline_score

    def test_score_delta_negative(self, linear_arch):
        # score_delta = compromised - baseline, which must be negative when
        # the attack degrades the mission (the expected case).
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert result.score_delta < 0

    def test_affected_components_not_empty(self, linear_arch):
        # The affected list must contain at least the directly attacked node.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert len(result.affected_components) > 0

    def test_target_always_in_affected_components(self, linear_arch):
        # The directly attacked component must always be in the affected set,
        # even if it is an isolated leaf with no downstream nodes.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "B")
        assert "B" in result.affected_components

    def test_attack_path_is_list_of_strings(self, linear_arch):
        # attack_path must be a list of strings that the frontend can render
        # as ordered steps in the results panel.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert isinstance(result.attack_path, list)
        assert all(isinstance(s, str) for s in result.attack_path)

    def test_attack_path_not_empty(self, linear_arch):
        # There must always be at least one step (the initial compromise).
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert len(result.attack_path) >= 1

    def test_explanation_is_non_empty_string(self, linear_arch):
        # The explanation field must be a non-empty string for the results panel.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert isinstance(result.explanation, str)
        assert len(result.explanation) > 0

    def test_criticality_ranking_included(self, linear_arch):
        # The criticality ranking must be present and non-empty so the
        # frontend table always has data to display.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert isinstance(result.criticality_ranking, list)
        assert len(result.criticality_ranking) > 0

    def test_isolated_leaf_score_drops_by_one_third(self, linear_arch):
        # Compromising C (a leaf with no descendants) in a 3-node graph
        # means 1 of 3 nodes is compromised: score = 2/3 * 100 = 66.67%
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "C")
        assert abs(result.compromised_score - 66.67) < 0.1

    def test_full_chain_compromise_score_zero(self, linear_arch):
        # Compromising A propagates to B and C, so all 3 nodes are affected.
        # 0 healthy / 3 total = 0% mission success.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert result.compromised_score == 0.0

    def test_architecture_id_in_result(self, linear_arch):
        # The result must echo back the architecture ID so the frontend
        # can verify the response belongs to the architecture it requested.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert result.architecture_id == 1

    def test_scenario_type_in_result(self, linear_arch):
        # The result must echo back the normalized scenario type string.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert result.scenario_type == "node_compromise"

    def test_unknown_scenario_raises(self, linear_arch):
        # An unrecognized scenario type must raise SimulatorError with a
        # message containing "Unknown scenario" so the router can convert
        # it to a 422 response.
        sim = MissionArchitectureSimulator(linear_arch)
        with pytest.raises(SimulatorError, match="Unknown scenario"):
            sim.run_simulation("nuclear_launch", "A")

    def test_unknown_target_raises(self, linear_arch):
        # A target component ID that doesn't exist in the graph must raise
        # SimulatorError so the router returns 422 instead of 500.
        sim = MissionArchitectureSimulator(linear_arch)
        with pytest.raises(SimulatorError, match="not found"):
            sim.run_simulation("node_compromise", "GHOST")

    def test_case_insensitive_scenario_type(self, linear_arch):
        # The simulator normalizes scenario_type to lowercase before matching,
        # so NODE_COMPROMISE and node_compromise must behave identically.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("NODE_COMPROMISE", "A")
        assert result.scenario_type == "node_compromise"

    def test_affected_component_names_matches_affected_ids(self, linear_arch):
        # affected_component_names must be parallel to affected_components
        # (same length, same order) so the frontend can zip them together.
        sim = MissionArchitectureSimulator(linear_arch)
        result = sim.run_simulation("node_compromise", "A")
        assert len(result.affected_component_names) == len(result.affected_components)


class TestSupportedScenarios:
    """
    Tests for the SUPPORTED_SCENARIOS module-level constant.

    These tests ensure the constant is the right type and contains the
    scenarios that Increment 1 is required to support.
    """

    def test_node_compromise_in_supported(self):
        # node_compromise is the only required Increment 1 scenario.
        assert "node_compromise" in SUPPORTED_SCENARIOS

    def test_supported_scenarios_is_frozenset(self):
        # frozenset is required to prevent runtime mutation of the constant.
        assert isinstance(SUPPORTED_SCENARIOS, frozenset)


class TestPerformance:
    """
    Performance benchmarks to verify the simulator stays within acceptable
    time limits as graph size grows.

    The project spec requires simulations on 50-node graphs to complete in
    under 500ms. We test with 100 nodes at a 1-second limit to give headroom
    and catch algorithmic regressions early.
    """

    def test_large_linear_chain_under_1_second(self):
        # Build a 100-node linear chain (worst case for linear traversal)
        # and verify the full simulation completes in under 1 second.
        n = 100
        components = [make_component(str(i), f"Node-{i}") for i in range(n)]
        flows = [make_flow(str(i), str(i + 1)) for i in range(n - 1)]
        arch = make_arch(components, flows)

        sim = MissionArchitectureSimulator(arch)

        # time.perf_counter() gives higher resolution than time.time()
        # and is not affected by system clock adjustments.
        start = time.perf_counter()
        sim.run_simulation("node_compromise", "0")
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"Simulation took {elapsed:.3f}s (limit 1.0s)"

    def test_large_graph_node_count(self):
        # Sanity check that building a 100-node graph produces exactly 100 nodes,
        # confirming no nodes were silently dropped or duplicated during construction.
        n = 100
        components = [make_component(str(i)) for i in range(n)]
        arch = make_arch(components)
        sim = MissionArchitectureSimulator(arch)
        assert sim.node_count() == n
