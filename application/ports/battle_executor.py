"""
Battle executor port - interface for executing battles.
This abstracts away poke_env Player execution model.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from domain.entities.agent import Agent
from domain.value_objects.battle_state import BattleState
from domain.value_objects.move_decision import MoveDecision


@dataclass
class BattleResult:
    """Result of a battle between two agents."""
    agent_a_id: str
    agent_b_id: str
    winner: str  # "a", "b", or "draw"
    turns: int
    agent_a_final_hp: float  # Total HP fraction remaining
    agent_b_final_hp: float
    replay_data: Optional[str] = None


class IBattleExecutor(ABC):
    """
    Port interface for executing Pokemon battles.
    Infrastructure layer will implement this using poke_env or other battle engines.
    """
    
    @abstractmethod
    async def execute_battle(
        self, 
        agent_a: Agent, 
        agent_b: Agent,
        save_replay: bool = False
    ) -> BattleResult:
        """
        Execute a battle between two agents.
        
        Args:
            agent_a: First agent
            agent_b: Second agent
            save_replay: Whether to save battle replay
            
        Returns:
            Battle result with winner and stats
        """
        pass

    @abstractmethod
    async def execute_battles(
        self,
        agent_pairs: list[tuple[Agent, Agent]],
        save_replays: bool = False
    ) -> list[BattleResult]:
        """
        Execute multiple battles concurrently.
        
        Args:
            agent_pairs: List of (agent_a, agent_b) tuples
            save_replays: Whether to save replays
            
        Returns:
            List of battle results
        """
        pass

    @abstractmethod
    def get_current_state(self, battle_id: str) -> Optional[BattleState]:
        """
        Get current state of an ongoing battle.
        
        Args:
            battle_id: Battle identifier
            
        Returns:
            Current battle state or None if battle not found
        """
        pass

    @abstractmethod
    def register_strategy(self, agent_id: str, strategy) -> None:
        """
        Register a battle strategy for an agent.
        
        Args:
            agent_id: Agent identifier
            strategy: Battle strategy implementation (IBattleStrategy)
        """
        pass
