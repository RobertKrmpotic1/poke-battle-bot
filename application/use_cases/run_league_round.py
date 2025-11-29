"""
Run League Round Use Case - orchestrates a tournament round.
Application layer: coordinates tournament pairing with battle execution.
"""
from typing import List, Tuple, Dict, Any
from application.ports.battle_executor import IBattleExecutor, BattleResult
from application.use_cases.execute_battle import ExecuteBattle
from domain.entities.agent import Agent
from domain.services.tournament_service import TournamentService
from loguru import logger


class RunLeagueRound:
    """
    Use case for running a complete tournament round.
    Pairs agents, executes battles, and tracks results.
    """

    def __init__(
        self,
        battle_executor: IBattleExecutor,
        execute_battle: ExecuteBattle,
        tournament_service: TournamentService
    ):
        """
        Initialize use case with dependencies.

        Args:
            battle_executor: Port for executing battles
            execute_battle: Use case for individual battles
            tournament_service: Domain service for tournament logic
        """
        self.battle_executor = battle_executor
        self.execute_battle = execute_battle
        self.tournament_service = tournament_service

    async def execute(
        self,
        agents: List[Agent],
        pairing_method: str = "sorted",
        update_ratings: bool = True,
        save_replays: bool = False,
        matches_per_agent: int = 1
    ) -> Dict[str, Any]:
        """
        Execute a complete tournament round.

        Args:
            agents: List of agents to compete
            pairing_method: How to pair agents ("sorted", "random", "round_robin")
            update_ratings: Whether to update ELO ratings
            save_replays: Whether to save battle replays
            matches_per_agent: For random pairing, how many matches each agent plays

        Returns:
            Round results with pairings, results, and statistics
        """
        logger.info(f"Starting league round with {len(agents)} agents using {pairing_method} pairing")

        # Create pairings based on method
        if pairing_method == "sorted":
            pairings = self.tournament_service.create_sorted_pairings(agents)
        elif pairing_method == "random":
            pairings = self.tournament_service.create_random_pairings(agents, matches_per_agent)
        elif pairing_method == "round_robin":
            pairings = self.tournament_service.create_round_robin_pairings(agents)
        else:
            raise ValueError(f"Unknown pairing method: {pairing_method}")

        logger.info(f"Created {len(pairings)} pairings")

        # Execute all battles
        battle_results = []
        for i, (agent_id_a, agent_id_b) in enumerate(pairings):
            logger.info(f"Executing battle {i+1}/{len(pairings)}: {agent_id_a} vs {agent_id_b}")

            # Find agents by ID
            agent_a = next(a for a in agents if a.agent_id == agent_id_a)
            agent_b = next(a for a in agents if a.agent_id == agent_id_b)

            # Execute battle
            try:
                result = await self.execute_battle.execute(
                    agent_a,
                    agent_b,
                    update_ratings=update_ratings,
                    save_replay=save_replays
                )
                battle_results.append({
                    "pairing": (agent_id_a, agent_id_b),
                    "result": result,
                    "success": True
                })
                logger.info(f"Battle result: {result.winner} won ({result.turns} turns)")

            except Exception as e:
                logger.error(f"Battle failed: {agent_id_a} vs {agent_id_b} - {e}")
                battle_results.append({
                    "pairing": (agent_id_a, agent_id_b),
                    "result": None,
                    "success": False,
                    "error": str(e)
                })

        # Calculate round statistics
        successful_battles = [r for r in battle_results if r["success"]]
        failed_battles = [r for r in battle_results if not r["success"]]

        total_turns = sum(r["result"].turns for r in successful_battles if r["result"])
        avg_turns = total_turns / len(successful_battles) if successful_battles else 0

        # Count wins by agent
        wins_by_agent = {}
        for agent in agents:
            wins_by_agent[agent.agent_id] = 0

        for result in successful_battles:
            if result["result"] and result["result"].winner:
                winner_id = result["pairing"][0] if result["result"].winner == "a" else result["pairing"][1]
                wins_by_agent[winner_id] += 1

        # Get final standings
        final_standings = self.tournament_service.calculate_league_standings(agents)

        round_summary = {
            "total_battles": len(battle_results),
            "successful_battles": len(successful_battles),
            "failed_battles": len(failed_battles),
            "average_turns": round(avg_turns, 1),
            "pairings": pairings,
            "battle_results": battle_results,
            "wins_by_agent": wins_by_agent,
            "final_standings": final_standings,
            "pairing_method": pairing_method
        }

        logger.info(f"Round complete: {len(successful_battles)}/{len(battle_results)} battles successful")
        logger.info(f"Average battle length: {avg_turns:.1f} turns")

        return round_summary