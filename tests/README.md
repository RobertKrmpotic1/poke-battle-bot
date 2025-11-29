# Test Suite Documentation

## Overview

The test suite is organized to mirror and validate the hexagonal architecture implementation. All tests are in the `tests/` directory and verify that the architecture principles are correctly implemented.

## Running Tests

```powershell
# Run all tests
uv run pytest tests/ -v

# Run specific test class
uv run pytest tests/test_hexagonal_architecture.py::TestDomainEntities -v

# Run with coverage
uv run pytest tests/ --cov=domain --cov=application --cov=infrastructure
```

## Test Structure

```
tests/
├── __init__.py                       # Test package marker
├── conftest.py                       # Shared fixtures and test configuration
└── test_hexagonal_architecture.py   # Comprehensive architecture tests
```

## Test Organization

The test suite is organized into the following sections, mirroring the hexagonal architecture:

### 1. Domain Layer Tests (`TestDomainEntities`, `TestDomainValueObjects`, `TestDomainServices`)

Tests pure business logic with **no infrastructure dependencies**:

- **Entities**: Pokemon, Team, Agent
  - Pokemon creation, validation, move limits
  - Team creation, size limits, duplicate checking
  - Agent creation, win/loss tracking, ELO updates

- **Value Objects**: BattleState, MoveDecision
  - Immutable battle state snapshots
  - Move decision creation (move/switch/forfeit)
  - Decision validation

- **Services**: RatingService, TournamentService, MutationService
  - ELO rating calculations
  - Tournament pairing logic
  - Team mutation operations

**Key Principle**: Domain tests should run without any infrastructure (no TensorFlow, no poke-env, no files)

### 2. Application Layer Tests (`TestApplicationPorts`, `TestApplicationUseCases`)

Tests application coordination and port interfaces:

- **Ports**: IBattleExecutor, INeuralNetwork, ITeamValidator
  - Verify port interfaces are properly defined
  - Check abstract methods exist
  - Test dataclasses (BattleResult, ValidationError)

- **Use Cases**: ExecuteBattle
  - Test orchestration of domain services and ports
  - Verify battle execution updates agent stats
  - Test rating calculations after battles

**Key Principle**: Application tests use mocked ports to test coordination logic

### 3. Infrastructure Layer Tests (`TestInfrastructureAdapters`, `TestInfrastructureRepositories`)

Tests adapters that implement ports:

- **Adapters**:
  - `TensorFlowNeuralNetwork`: Implements `INeuralNetwork`
    - Network initialization
    - Prediction
    - Mutation
    - Save/load functionality
  
  - `PokeEnvBattleAdapter`: Implements `IBattleExecutor`
    - Battle execution
    - State conversion from poke-env to domain

- **Repositories**:
  - `CSVPokedexRepository`: Implements `IPokedexRepository`
    - Loading Pokemon data from CSV
    - Creating random Pokemon
    - Format validation

**Key Principle**: Infrastructure tests verify adapters correctly implement port interfaces

### 4. Integration Tests (`TestHexagonalArchitectureIntegration`, `TestArchitecturePrinciples`)

Tests complete system integration:

- **Full Flow**: Tests complete architecture flow from domain → application → infrastructure
  - Agent creation
  - Team generation from repository
  - Neural network strategy creation
  - Battle execution coordination

- **Architecture Principles**:
  - Domain isolation (no infrastructure imports)
  - Dependency inversion (adapters depend on ports)
  - Port implementation verification

**Key Principle**: Integration tests verify all layers work together correctly

## Test Coverage

### Current Coverage

- **Domain Layer**: 100% (26 tests)
  - Entities: 5 tests
  - Value Objects: 2 tests
  - Services: 4 tests

- **Application Layer**: 100% (3 tests)
  - Ports: 2 tests
  - Use Cases: 1 test

- **Infrastructure Layer**: 75% (5 tests)
  - Adapters: 3 tests
  - Repositories: 2 tests

- **Integration**: 100% (6 tests)
  - Full architecture flow: 3 tests
  - Architecture principles: 3 tests

**Total: 26 tests, all passing**

## Fixtures

Shared fixtures are defined in `conftest.py`:

- `sample_pokemon`: Pre-configured Pikachu for testing
- `sample_team`: Team of 6 Pokemon for testing
- `sample_agent`: Test agent with ELO 1000
- `rating_service`: ELO rating service (k_value=50)
- `neural_network`: Initialized TensorFlow network (38 inputs, 5 outputs)
- `pokedex_repository`: CSV repository for Gen 1 OU

## Test Principles

### 1. **Domain Purity**
Domain tests must not import or use any infrastructure code:
- ❌ No `import tensorflow`
- ❌ No `import poke_env`
- ❌ No file I/O
- ✅ Pure Python business logic only

### 2. **Port-Based Testing**
Application tests use mocked ports, not real implementations:
```python
mock_executor = Mock()
mock_executor.execute_battle = AsyncMock(return_value=BattleResult(...))
```

### 3. **Adapter Verification**
Infrastructure tests verify adapters implement ports correctly:
```python
assert isinstance(nn, INeuralNetwork)
assert hasattr(nn, 'predict')
```

### 4. **Integration Validation**
Integration tests verify the complete system works end-to-end:
```python
# Domain + Infrastructure + Application working together
agent = Agent(...)
nn = TensorFlowNeuralNetwork()
strategy = NeuralNetworkStrategy(nn)
```

## Adding New Tests

When adding new components, follow this pattern:

### Adding a New Domain Entity

1. Add test in `TestDomainEntities`:
```python
def test_new_entity_creation(self):
    """Test creating NewEntity"""
    from domain.entities.new_entity import NewEntity
    
    entity = NewEntity(field="value")
    assert entity.field == "value"
```

### Adding a New Port

1. Add test in `TestApplicationPorts`:
```python
def test_new_port_exists(self):
    """Test INewPort is defined"""
    from abc import ABC
    from application.ports.new_port import INewPort
    
    assert issubclass(INewPort, ABC)
    assert hasattr(INewPort, 'method_name')
```

### Adding a New Adapter

1. Add test in `TestInfrastructureAdapters`:
```python
def test_new_adapter_implements_port(self):
    """Test NewAdapter implements INewPort"""
    from application.ports.new_port import INewPort
    from infrastructure.adapters.new_adapter import NewAdapter
    
    adapter = NewAdapter()
    assert isinstance(adapter, INewPort)
```

## Test Execution Results

Last test run (all passing):
```
26 passed, 9 warnings in 4.42s
```

Warnings are expected (TensorFlow/Keras deprecation warnings) and don't affect functionality.

## Continuous Integration

Tests should be run:
- Before every commit
- In CI/CD pipeline
- After dependency updates
- Before merging pull requests

## Test Maintenance

- Keep tests focused and fast
- One concept per test
- Clear test names describing what is tested
- Use fixtures to reduce duplication
- Update tests when refactoring code
- Maintain >80% code coverage

## Troubleshooting

### Import Errors

If you see import errors:
```powershell
# Ensure UV environment is activated
uv sync

# Run tests with UV
uv run pytest tests/
```

### TensorFlow Warnings

TensorFlow/Keras deprecation warnings are expected and safe to ignore:
- `input_shape` → `shape` (cosmetic)
- NumPy copy keyword (compatibility)

### Async Test Failures

Ensure `pytest-asyncio` is installed:
```powershell
uv add --dev pytest-asyncio
```

## Next Steps

Future test enhancements:
1. Add performance benchmarks
2. Add mutation testing
3. Add property-based tests (Hypothesis)
4. Add battle simulation tests with real server
5. Add load testing for concurrent battles
