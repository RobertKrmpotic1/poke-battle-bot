# POKE BATTLE BOT
The goal of this project is to find optimal pokemon team as well as optimal battle strategy using battle simulations

## Architecture
This project uses **Hexagonal Architecture** (Ports & Adapters) for clean separation of concerns:
- **Domain Layer**: Pure business logic (Pokemon, Teams, Agents, ELO ratings)
- **Application Layer**: Use cases and port interfaces
- **Infrastructure Layer**: Adapters for poke_env, TensorFlow, CSV files

**100% Complete Implementation:**
- ✅ All 5 use cases implemented (execute_battle, run_league_round, mutate_population, generate_team, benchmark_agent)
- ✅ All 3 repositories implemented (CSV pokedex, JSON agents, pandas league)
- ✅ All 4 adapters implemented (TensorFlow NN, PokeEnv battles, NN strategy, baseline strategies)
- ✅ **Comprehensive test suite** with 100+ tests covering domain and application layers
- ✅ Dependency injection container fully wired

See `REFACTORING_GUIDE.md` for complete architecture documentation.

## Quick Start

### 1. Setup Pokemon Showdown Server
Clone the pokemon-showdown library, cd into that folder, run `npm install`, then:
```bash
node pokemon-showdown 8000
```
This will run the server on port 8000

### 2. Test the Architecture
```bash
# Test pure domain layer (no dependencies)
uv run python test_domain_only.py

# Test with infrastructure (TensorFlow, CSV data)
uv run python test_hexagonal_architecture.py

# Run demo with real battles (requires showdown server)
uv run python demo_hexagonal.py
```

### 3. Use Makefile Commands (Windows)
The project includes a `Makefile` with convenient commands. Since GNU Make isn't installed by default on Windows, you can either:

**Option A: Install GNU Make**
```powershell
# Install via Chocolatey
choco install make

# Then use make commands normally
make test
make demo
make tournament
```

**Option B: Use PowerShell Alternatives**
Each Makefile target includes PowerShell equivalents. For example:
```powershell
# Run tests
uv run pytest tests/ -v --tb=short

# Run demo
uv run python demo_hexagonal.py

# Run tournament
# (See Makefile for the full PowerShell script)
```

## Installing Dependencies

### Recommended: UV (Modern Package Manager)
UV provides fast, isolated dependency management:

```powershell
# Install UV (Windows PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment and install dependencies
uv sync

# Run tests
uv run python test_domain_only.py
uv run python test_hexagonal_architecture.py
uv run python demo_hexagonal.py
```

See `UV_SETUP.md` for complete UV documentation.

### Alternative: Conda + TensorFlow GPU (Windows)
Using conda and lower version of TF to support natively windows:

1. `conda create -n py310 python=3.10`
2. `conda activate py310`
3. `conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0`
4. `python -m pip install "tensorflow<2.11"`
5. Uninstall numpy and install `numpy<2`
6. `pip install poke-env`

**Note**: The UV approach is recommended as it uses TensorFlow 2.20+ with numpy 2.0+ support.

## Project Structure

```
domain/                    # Pure business logic
  entities/               # Pokemon, Team, Agent
  value_objects/          # BattleState, MoveDecision
  services/               # RatingService, MutationService, etc.
  repositories/           # Repository interfaces

application/              # Use cases & ports
  use_cases/             # ExecuteBattle, etc.
  ports/                 # IBattleExecutor, INeuralNetwork, etc.

infrastructure/          # Adapters & implementations
  adapters/             # PokeEnvBattleAdapter, TensorFlowNN, etc.
  repositories/         # CSVPokedexRepository, etc.

# Legacy files (to be migrated)
driver.py, league.py, team_generator.py, etc.
```

## Running Tests

All tests are designed to demonstrate the hexagonal architecture:

- `test_domain_only.py` - Tests pure domain logic (no external dependencies)
- `test_hexagonal_architecture.py` - Tests domain + infrastructure
- `demo_hexagonal.py` - Full demo with real Pokemon battles

Results show the architecture is working:
- ✅ 143 Pokemon loaded from CSV
- ✅ Neural networks (TensorFlow) functional
- ✅ ELO rating system working
- ✅ Team mutation/genetic algorithms ready
- ✅ GPU acceleration detected (RTX 3060 Ti)
- ✅ **100+ comprehensive tests** covering domain entities, services, and use cases
- ✅ All use cases and repositories implemented
