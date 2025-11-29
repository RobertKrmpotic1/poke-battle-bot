"""
Execute Battle Use Case - orchestrates a battle between two agents.
Application layer: coordinates domain services with infrastructure ports.
"""
from application.ports.battle_executor import IBattleExecutor, BattleResult
from domain.entities.agent import Agent
from domain.services.rating_service import RatingService


class ExecuteBattle:
    """
    Use case for executing a battle between two agents and updating their ratings.
    Coordinates domain logic with infrastructure without mixing layers.
    """
    
    def __init__(
        self,
        battle_executor: IBattleExecutor,
        rating_service: RatingService
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            battle_executor: Port for executing battles
            rating_service: Domain service for rating calculations
        """
        self.battle_executor = battle_executor
        self.rating_service = rating_service

    async def execute(
        self,
        agent_a: Agent,
        agent_b: Agent,
        update_ratings: bool = True,
        save_replay: bool = False
    ) -> BattleResult:
        """
        Execute a battle and optionally update agent ratings.
        
        Args:
            agent_a: First agent
            agent_b: Second agent
            update_ratings: Whether to update ELO ratings
            save_replay: Whether to save battle replay
            
        Returns:
            Battle result
        """
        # Execute battle via infrastructure port
        result = await self.battle_executor.execute_battle(
            agent_a,
            agent_b,
            save_replay=save_replay
        )
        
        # Update ratings if requested
        if update_ratings:
            self._update_agent_ratings(agent_a, agent_b, result)
        
        return result

    def _update_agent_ratings(
        self,
        agent_a: Agent,
        agent_b: Agent,
        result: BattleResult
    ) -> None:
        """
        Update agent ratings based on battle result.
        Pure domain logic coordinated by application layer.
        """
        # Calculate new ratings using domain service
        new_elo_a, new_elo_b = self.rating_service.calculate_ratings_after_battle(
            rating_a=agent_a.elo,
            rating_b=agent_b.elo,
            winner=result.winner
        )
        
        # Update agents (domain entities)
        agent_a.update_elo(new_elo_a)
        agent_b.update_elo(new_elo_b)
        
        # Update battle records
        if result.winner == "a":
            agent_a.record_win()
            agent_b.record_loss()
        elif result.winner == "b":
            agent_a.record_loss()
            agent_b.record_win()
        else:
            agent_a.record_draw()
            agent_b.record_draw()
