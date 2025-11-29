"""
Benchmark Agent Use Case - Tests agent performance against baseline opponents.
Low-priority feature: Performance comparison against known strategies.
"""
from typing import List, Dict, Optional, Tuple
import asyncio
from dataclasses import dataclass
from domain.entities.agent import Agent
from application.ports.battle_executor import IBattleExecutor
from application.use_cases.execute_battle import ExecuteBattle
from domain.services.rating_service import RatingService


@dataclass
class BenchmarkResult:
    """Result of benchmarking an agent."""
    agent: Agent
    opponent_name: str
    battles_won: int
    total_battles: int
    win_rate: float
    average_turns: float
    elo_change: int
    final_elo: int


@dataclass
class BenchmarkReport:
    """Complete benchmark report for an agent."""
    agent: Agent
    results: List[BenchmarkResult]
    overall_win_rate: float
    best_performance: str  # Name of opponent with best performance
    worst_performance: str  # Name of opponent with worst performance
    average_elo_change: float


class BenchmarkAgent:
    """
    Use case for benchmarking agent performance against baseline opponents.
    Tests agent against known strategies to measure improvement over time.
    """

    def __init__(
        self,
        battle_executor: IBattleExecutor,
        execute_battle: ExecuteBattle,
        rating_service: RatingService
    ):
        """
        Initialize benchmark agent use case.

        Args:
            battle_executor: Battle execution port
            execute_battle: Battle execution use case
            rating_service: ELO rating calculations
        """
        self.battle_executor = battle_executor
        self.execute_battle = execute_battle
        self.rating_service = rating_service

    async def execute(
        self,
        agent: Agent,
        battles_per_opponent: int = 10,
        opponents: Optional[List[Tuple[str, str]]] = None
    ) -> BenchmarkReport:
        """
        Benchmark an agent against multiple opponents.

        Args:
            agent: Agent to benchmark
            battles_per_opponent: Number of battles against each opponent
            opponents: List of (opponent_name, strategy_type) tuples.
                      If None, uses default baseline opponents.

        Returns:
            Complete benchmark report
        """
        if opponents is None:
            opponents = self._get_default_opponents()

        results = []
        total_wins = 0
        total_battles = 0
        total_elo_change = 0
        initial_elo = agent.elo

        for opponent_name, strategy_type in opponents:
            result = await self._benchmark_against_opponent(
                agent, opponent_name, strategy_type, battles_per_opponent
            )
            results.append(result)
            total_wins += result.battles_won
            total_battles += result.total_battles
            total_elo_change += result.elo_change

        # Calculate overall statistics
        overall_win_rate = total_wins / total_battles if total_battles > 0 else 0

        # Find best and worst performances
        best_result = max(results, key=lambda r: r.win_rate)
        worst_result = min(results, key=lambda r: r.win_rate)

        # Reset agent ELO to initial value (benchmarking shouldn't affect real rating)
        agent.elo = initial_elo

        return BenchmarkReport(
            agent=agent,
            results=results,
            overall_win_rate=overall_win_rate,
            best_performance=best_result.opponent_name,
            worst_performance=worst_result.opponent_name,
            average_elo_change=total_elo_change / len(results) if results else 0
        )

    async def _benchmark_against_opponent(
        self,
        agent: Agent,
        opponent_name: str,
        strategy_type: str,
        num_battles: int
    ) -> BenchmarkResult:
        """
        Benchmark agent against a specific opponent.

        Args:
            agent: Agent to test
            opponent_name: Name of opponent
            strategy_type: Type of strategy opponent uses
            num_battles: Number of battles to run

        Returns:
            Benchmark result for this opponent
        """
        # Create baseline opponent
        baseline_agent = self._create_baseline_agent(opponent_name, strategy_type, agent.battle_format)

        # Register strategies
        agent_strategy = self.battle_executor.create_strategy_for_agent(agent)
        baseline_strategy = self._create_baseline_strategy(baseline_agent, strategy_type)

        self.battle_executor.register_strategy(agent.agent_id, agent_strategy)
        self.battle_executor.register_strategy(baseline_agent.agent_id, baseline_strategy)

        # Track initial ELO
        initial_elo = agent.elo

        # Run battles
        battles_won = 0
        total_turns = 0
        successful_battles = 0

        for _ in range(num_battles):
            try:
                result = await self.execute_battle.execute(
                    agent_a=agent,
                    agent_b=baseline_agent,
                    update_ratings=True
                )

                if result["success"]:
                    successful_battles += 1
                    total_turns += result["turns"]

                    # Check if our agent won
                    if result["winner"] == agent.agent_id:
                        battles_won += 1

            except Exception as e:
                # Log error but continue benchmarking
                print(f"Battle error against {opponent_name}: {e}")
                continue

        # Calculate statistics
        win_rate = battles_won / successful_battles if successful_battles > 0 else 0
        average_turns = total_turns / successful_battles if successful_battles > 0 else 0
        elo_change = agent.elo - initial_elo
        final_elo = agent.elo

        return BenchmarkResult(
            agent=agent,
            opponent_name=opponent_name,
            battles_won=battles_won,
            total_battles=successful_battles,
            win_rate=win_rate,
            average_turns=average_turns,
            elo_change=elo_change,
            final_elo=final_elo
        )

    def _get_default_opponents(self) -> List[Tuple[str, str]]:
        """
        Get default baseline opponents for benchmarking.

        Returns:
            List of (name, strategy_type) tuples
        """
        return [
            ("RandomBot", "random"),
            ("MaxDamageBot", "max_damage"),
            ("FirstMoveBot", "first_move"),
        ]

    def _create_baseline_agent(self, name: str, strategy_type: str, battle_format: str) -> Agent:
        """
        Create a baseline agent for benchmarking.

        Args:
            name: Agent name
            strategy_type: Type of strategy
            battle_format: Battle format

        Returns:
            Baseline agent
        """
        agent = Agent(agent_id=name, battle_format=battle_format)
        # Set baseline ELO (1500 is typical starting point)
        agent.elo = 1500
        return agent

    def _create_baseline_strategy(self, agent: Agent, strategy_type: str):
        """
        Create a baseline strategy for an agent.

        Args:
            agent: Agent to create strategy for
            strategy_type: Type of baseline strategy

        Returns:
            Strategy instance
        """
        from infrastructure.adapters.baseline_strategies import (
            RandomStrategy, MaxDamageStrategy, FirstMoveStrategy
        )

        if strategy_type == "random":
            return RandomStrategy()
        elif strategy_type == "max_damage":
            return MaxDamageStrategy()
        elif strategy_type == "first_move":
            return FirstMoveStrategy()
        else:
            raise ValueError(f"Unknown baseline strategy type: {strategy_type}")