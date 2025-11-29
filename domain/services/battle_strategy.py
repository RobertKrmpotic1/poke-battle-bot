"""
Battle strategy interface - how agents make decisions.
Extracted from driver.py choose_move logic.
"""
from abc import ABC, abstractmethod
from typing import List
from ..value_objects.battle_state import BattleState
from ..value_objects.move_decision import MoveDecision


class IBattleStrategy(ABC):
    """
    Interface for battle decision-making strategies.
    Implementations can use neural networks, heuristics, or other approaches.
    """
    
    @abstractmethod
    def choose_action(self, battle_state: BattleState) -> MoveDecision:
        """
        Choose an action based on current battle state.
        
        Args:
            battle_state: Current state of the battle
            
        Returns:
            Decision to make (move, switch, or forfeit)
        """
        pass

    @abstractmethod
    def get_action_priorities(self, battle_state: BattleState) -> List[float]:
        """
        Get priority scores for all possible actions.
        
        Args:
            battle_state: Current state of the battle
            
        Returns:
            List of scores for each possible action
        """
        pass


class RandomStrategy(IBattleStrategy):
    """Simple random strategy for testing."""
    
    def choose_action(self, battle_state: BattleState) -> MoveDecision:
        """Choose a random move."""
        import random
        
        if not battle_state.my_active_pokemon:
            return MoveDecision.forfeit()
        
        if battle_state.force_switch:
            # Must switch - choose random non-fainted Pokemon
            available = [
                i for i, p in enumerate(battle_state.my_team)
                if not p.fainted and not p.active
            ]
            if available:
                return MoveDecision.switch(random.choice(available))
            return MoveDecision.forfeit()
        
        # Choose random move
        num_moves = len(battle_state.my_active_pokemon.available_moves)
        if num_moves > 0:
            return MoveDecision.move(random.randint(0, num_moves - 1))
        
        return MoveDecision.forfeit()

    def get_action_priorities(self, battle_state: BattleState) -> List[float]:
        """Return equal priorities for all actions."""
        import random
        
        if not battle_state.my_active_pokemon:
            return [0.0]
        
        num_moves = len(battle_state.my_active_pokemon.available_moves)
        return [random.random() for _ in range(num_moves)]
