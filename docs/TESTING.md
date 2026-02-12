# Testing Guide

## Overview

This project uses:
- **pytest** for Python backend testing
- **Jest** for JavaScript/TypeScript frontend testing

## Running Tests

### Backend Tests

```bash
cd backend
pytest
```

With coverage report:
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

Run specific test file:
```bash
pytest tests/test_simulator.py -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

Watch mode:
```bash
npm test -- --watch
```

## Writing Tests

### Backend Test Example

```python
# tests/test_simulator.py
import pytest
from app.services.simulator import propagate_compromise

def test_node_compromise_propagation():
    # Test that compromise propagates downstream
    graph = create_test_graph()
    affected = propagate_compromise(graph, node_id=1)
    assert len(affected) == 3  # Node 1 and its 2 descendants
```

### Frontend Test Example

```typescript
// __tests__/DiagramEditor.test.tsx
import { render, screen } from '@testing-library/react';
import DiagramEditor from '@/components/DiagramEditor';

test('renders diagram editor', () => {
  render(<DiagramEditor />);
  expect(screen.getByText('Add Component')).toBeInTheDocument();
});
```

## Coverage Goals

- **Increment 1**: 60%+ coverage
- **Increment 2**: 70%+ coverage
- **Increment 3**: 85%+ coverage

## CI/CD Testing

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request

View results in GitHub Actions.

## Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_api.py          # API endpoint tests
│   ├── test_simulator.py    # Simulation logic tests
│   └── test_database.py     # Database tests

frontend/
├── __tests__/
│   ├── components/
│   └── pages/
```

## Best Practices

1. Write tests before or alongside code (TDD)
2. Test edge cases and error conditions
3. Use descriptive test names
4. Keep tests independent and isolated
5. Mock external dependencies
6. Aim for fast test execution
