"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app
    """
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_architecture():
    """
    Sample architecture for testing
    """
    return {
        "name": "Test Architecture",
        "description": "A simple test architecture",
        "components": [
            {
                "id": "1",
                "name": "Sensor A",
                "type": "Sensor",
                "criticality": 8,
                "position": {"x": 0, "y": 0}
            },
            {
                "id": "2",
                "name": "Processor B",
                "type": "Compute",
                "criticality": 9,
                "position": {"x": 100, "y": 0}
            },
            {
                "id": "3",
                "name": "Control C",
                "type": "Control",
                "criticality": 10,
                "position": {"x": 200, "y": 0}
            }
        ],
        "flows": [
            {
                "id": "f1",
                "source": "1",
                "target": "2"
            },
            {
                "id": "f2",
                "source": "2",
                "target": "3"
            }
        ]
    }


@pytest.fixture
def sample_graph():
    """
    Create a sample NetworkX graph for testing
    """
    import networkx as nx
    G = nx.DiGraph()
    G.add_edge("1", "2")
    G.add_edge("2", "3")
    return G
