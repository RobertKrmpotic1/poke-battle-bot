"""
Baseline battle strategies for benchmarking.
Simple strategies to test agent performance against known opponents.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from poke_env.battle import Battle


class BaselineStrategy(ABC):
    """Base class for baseline battle strategies."""

    @abstractmethod
    def choose_move(self, battle: Battle) -> str:
        """
        Choose a move based on battle state.

        Args:
            battle: Current battle state

        Returns:
            Move choice string
        """
        pass


class RandomStrategy(BaselineStrategy):
    """Randomly selects moves - baseline for comparison."""

    def choose_move(self, battle: Battle) -> str:
        """Choose a random available move."""
        import random

        available_moves = [move for move in battle.available_moves if move]
        if available_moves:
            return random.choice(available_moves).id

        # If no moves available, try to switch
        available_switches = battle.available_switches
        if available_switches:
            return f"switch {random.choice(available_switches).species}"

        return "pass"


class MaxDamageStrategy(BaselineStrategy):
    """Always chooses the move that deals maximum damage."""

    def choose_move(self, battle: Battle) -> str:
        """Choose move with highest damage potential."""
        if not battle.available_moves:
            return "pass"

        # Calculate potential damage for each move
        best_move = None
        max_damage = 0

        for move in battle.available_moves:
            if move and move.base_power:
                damage = move.base_power
                # Consider STAB bonus
                if move.type in battle.active_pokemon.types:
                    damage *= 1.5
                # Consider type effectiveness (simplified)
                opponent = battle.opponent_active_pokemon
                if opponent:
                    effectiveness = self._get_type_effectiveness(move.type, opponent.types)
                    damage *= effectiveness

                if damage > max_damage:
                    max_damage = damage
                    best_move = move

        if best_move:
            return best_move.id

        # Fallback to random
        return RandomStrategy().choose_move(battle)

    def _get_type_effectiveness(self, move_type: str, defender_types: List[str]) -> float:
        """Simplified type effectiveness calculation."""
        # This is a very basic implementation - real type charts are more complex
        type_chart = {
            "fire": {"grass": 2.0, "water": 0.5, "fire": 0.5},
            "water": {"fire": 2.0, "grass": 0.5, "water": 0.5},
            "grass": {"water": 2.0, "fire": 0.5, "grass": 0.5},
            "electric": {"water": 2.0, "grass": 0.5, "electric": 0.5},
        }

        effectiveness = 1.0
        for defender_type in defender_types:
            if move_type in type_chart and defender_type in type_chart[move_type]:
                effectiveness *= type_chart[move_type][defender_type]

        return effectiveness


class FirstMoveStrategy(BaselineStrategy):
    """Always chooses the first available move."""

    def choose_move(self, battle: Battle) -> str:
        """Choose the first available move."""
        if battle.available_moves and battle.available_moves[0]:
            return battle.available_moves[0].id

        # Fallback
        return RandomStrategy().choose_move(battle)