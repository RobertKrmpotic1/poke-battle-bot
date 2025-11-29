# Pokemon Battle Bot - Makefile
# Windows-compatible commands using PowerShell
#
# Note: GNU Make is not installed by default on Windows.
# To use this Makefile, install GNU Make via Chocolatey:
#   choco install make
#
# Or use the PowerShell alternatives below each target.

.PHONY: help test demo tournament evolve install clean format lint docs

# Default target
help:
	@echo "Pokemon Battle Bot - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run all tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make test-cov-check - Run tests and enforce 85% coverage"
	@echo "  make view-cov    - View coverage report in browser"
	@echo "  make demo        - Run hexagonal architecture demo"
	@echo "  make format      - Format code with black"
	@echo "  make lint        - Run linting checks"
	@echo "  make clean       - Clean cache files"
	@echo ""
	@echo "Tournaments:"
	@echo "  make tournament  - Run a league tournament round"
	@echo "  make evolve      - Run genetic evolution cycle"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs        - Generate documentation"

# Install dependencies
install:
	uv sync
	uv pip install -e .
	# PowerShell alternative: uv sync; uv pip install -e .

# Run all tests
test:
	uv run pytest tests/ -v --tb=short
	# PowerShell alternative: uv run pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	uv run pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov-report=term-missing --cov-report=html -v
	@echo ""
	@echo "Coverage report saved to htmlcov/index.html"
	# PowerShell alternative: uv run pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov-report=term-missing --cov-report=html -v

# Run tests with coverage and enforce 85% threshold
test-cov-check:
	uv run pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov-report=term-missing --cov-report=html --cov-fail-under=85 -v
	@echo ""
	@echo "✅ Coverage meets 85% threshold!"
	# PowerShell alternative: uv run pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov-report=term-missing --cov-report=html --cov-fail-under=85 -v

# View coverage report in browser
view-cov:
	start htmlcov/index.html
	# PowerShell alternative: start htmlcov/index.html

# Run hexagonal architecture demo
demo:
	uv run python demo_hexagonal.py
	# PowerShell alternative: uv run python demo_hexagonal.py

# Run league evolution demo
league-demo:
	uv run python league_evolution_demo.py
	# PowerShell alternative: uv run python league_evolution_demo.py

# Run a tournament round
tournament:
	@echo "Running tournament round..."
	uv run python -c "
from infrastructure.di_container import Container
import asyncio

async def main():
    container = Container()
    agents = container.create_population(8, 'TournamentBot')
    print(f'Created {len(agents)} agents')

    # Register strategies
    for agent in agents:
        strategy = container.battle_executor.create_strategy_for_agent(agent)
        container.battle_executor.register_strategy(agent.agent_id, strategy)

    # Run tournament round
    round_result = await container.run_league_round.execute(
        agents=agents,
        pairing_method='round_robin',
        update_ratings=True
    )

    print(f'Tournament complete: {round_result[\"successful_battles\"]}/{round_result[\"total_battles\"]} battles')
    print(f'Average turns: {round_result[\"average_turns\"]:.1f}')
    print('Final standings:')
    for rank, agent in round_result['final_standings'][:5]:
        print(f'  {rank}. {agent.agent_id}: {agent.elo} ELO')

asyncio.run(main())
	"
	# PowerShell alternative:
	# Write-Host "Running tournament round..."
	# uv run python -c "
	# from infrastructure.di_container import Container
	# import asyncio
	# 
	# async def main():
	#     container = Container()
	#     agents = container.create_population(8, 'TournamentBot')
	#     Write-Host \"Created $($agents.Count) agents\"
	#     # ... (rest of the script with PowerShell Write-Host instead of print)
	# asyncio.run(main())
	# "

# Run genetic evolution cycle
evolve:
	@echo "Running genetic evolution..."
	uv run python -c "
from infrastructure.di_container import Container
import asyncio

async def main():
    container = Container()

    # Load or create initial population
    agents = container.load_population()
    if not agents:
        agents = container.create_population(10, 'EvolveBot')
        print(f'Created initial population of {len(agents)} agents')
    else:
        print(f'Loaded population of {len(agents)} agents')

    # Register strategies
    for agent in agents:
        strategy = container.battle_executor.create_strategy_for_agent(agent)
        container.battle_executor.register_strategy(agent.agent_id, strategy)

    # Run evolution tournament
    round_result = await container.run_league_round.execute(
        agents=agents,
        pairing_method='sorted',
        update_ratings=True
    )

    print(f'Evolution tournament: {round_result[\"successful_battles\"]}/{round_result[\"total_battles\"]} battles')

    # Evolve population
    evolution_result = container.mutate_population.execute(
        agents=agents,
        population_size=10,
        elite_count=2
    )

    new_population = evolution_result['new_population']
    stats = evolution_result['evolution_stats']

    print(f'Evolution complete:')
    print(f'  Elite kept: {stats[\"elite_count\"]}')
    print(f'  Offspring created: {stats[\"offspring_created\"]}')
    print(f'  Top ELO: {stats[\"top_elo_before\"]} -> {stats[\"top_elo_after\"]}')

    # Save new population
    container.save_population(new_population, generation=1)

asyncio.run(main())
	"
	# PowerShell alternative: Similar to tournament, replace @echo with Write-Host and print with Write-Host

# Format code
format:
	uv run black . --line-length 100
	uv run isort .
	# PowerShell alternative: uv run black . --line-length 100; uv run isort .

# Run linting
lint:
	uv run flake8 . --max-line-length 100 --extend-ignore=E203,W503
	uv run mypy . --ignore-missing-imports
	# PowerShell alternative: uv run flake8 . --max-line-length 100 --extend-ignore=E203,W503; uv run mypy . --ignore-missing-imports

# Clean cache files
clean:
	Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .pytest_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force .mypy_cache -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force *.pyc -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
	Remove-Item -Recurse -Force *.egg-info -ErrorAction SilentlyContinue
	# Already using PowerShell commands

# Generate documentation
docs:
	@echo "Generating documentation..."
	uv run sphinx-build docs/ docs/_build/
	# PowerShell alternative: Write-Host "Generating documentation..."; uv run sphinx-build docs/ docs/_build/

# Run specific test layers
test-domain:
	uv run pytest tests/ -k "TestDomain" -v
	# PowerShell alternative: uv run pytest tests/ -k "TestDomain" -v

test-application:
	uv run pytest tests/ -k "TestApplication" -v
	# PowerShell alternative: uv run pytest tests/ -k "TestApplication" -v

test-infrastructure:
	uv run pytest tests/ -k "TestInfrastructure" -v
	# PowerShell alternative: uv run pytest tests/ -k "TestInfrastructure" -v

# Quick test run (no verbose output)
test-quick:
	uv run pytest tests/ --tb=no -q
	# PowerShell alternative: uv run pytest tests/ --tb=no -q

# Development server (if implemented)
server:
	@echo "Starting development server..."
	# Add server startup command here
	# PowerShell alternative: Write-Host "Starting development server..."

# Database operations (if implemented)
db-init:
	@echo "Initializing database..."
	# Add database initialization here
	# PowerShell alternative: Write-Host "Initializing database..."

db-migrate:
	@echo "Running database migrations..."
	# Add migration commands here
	# PowerShell alternative: Write-Host "Running database migrations..."

# Performance benchmarking
benchmark:
	@echo "Running performance benchmarks..."
	uv run python -m pytest tests/ --benchmark-only
	# PowerShell alternative: Write-Host "Running performance benchmarks..."; uv run python -m pytest tests/ --benchmark-only

# CI/CD pipeline simulation
ci:
	make clean
	make install
	make lint
	make test-cov
	make docs
	# PowerShell alternative: make clean; make install; make lint; make test-cov; make docs