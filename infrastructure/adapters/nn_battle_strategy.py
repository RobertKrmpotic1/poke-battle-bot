"""
Neural Network Battle Strategy - uses NN for decision making.
Extracted from driver.py choose_move logic.
"""
import numpy as np
from typing import List
from domain.services.battle_strategy import IBattleStrategy
from domain.value_objects.battle_state import BattleState, Status, MoveCategory
from domain.value_objects.move_decision import MoveDecision
from application.ports.neural_network import INeuralNetwork


class NeuralNetworkStrategy(IBattleStrategy):
    """
    Battle strategy that uses a neural network for decision making.
    Implements the battle strategy interface using ML predictions.
    """
    
    def __init__(self, neural_network: INeuralNetwork):
        """
        Initialize strategy with a neural network.
        
        Args:
            neural_network: Neural network implementation (INeuralNetwork port)
        """
        self.nn = neural_network

    def choose_action(self, battle_state: BattleState) -> MoveDecision:
        """
        Choose an action based on current battle state using neural network.
        
        Args:
            battle_state: Current state of the battle
            
        Returns:
            Decision to make (move, switch, or forfeit)
        """
        if not battle_state.my_active_pokemon:
            return MoveDecision.forfeit()
        
        if battle_state.force_switch:
            # Must switch - choose best non-fainted Pokemon
            available = [
                i for i, p in enumerate(battle_state.my_team)
                if not p.fainted and not p.active
            ]
            if available:
                return MoveDecision.switch(available[0])
            return MoveDecision.forfeit()
        
        # Get action priorities from neural network
        priorities = self.get_action_priorities(battle_state)
        
        # Choose top legal move based on priorities
        return self._choose_top_legal_move(priorities, battle_state)

    def get_action_priorities(self, battle_state: BattleState) -> List[float]:
        """
        Get priority scores for all possible actions using neural network.
        
        Args:
            battle_state: Current state of the battle
            
        Returns:
            List of scores for each possible action
        """
        # Transform battle state to neural network input
        nn_input = self._transform_battle_state(battle_state)
        
        # Get predictions from neural network
        predictions = self.nn.predict(nn_input)
        
        return predictions.tolist()

    def _transform_battle_state(self, battle_state: BattleState) -> np.ndarray:
        """
        Transform battle state into neural network input vector.
        Simplified version from driver.py parse_input method.
        
        Args:
            battle_state: Current battle state
            
        Returns:
            Input array for neural network
        """
        features = []
        
        if battle_state.my_active_pokemon and battle_state.opponent_active_pokemon:
            my_poke = battle_state.my_active_pokemon
            opp_poke = battle_state.opponent_active_pokemon
            
            # HP fractions
            features.append(my_poke.hp_fraction)
            features.append(opp_poke.hp_fraction)
            
            # Status (7 features each)
            features.extend(self._encode_status(my_poke.status))
            features.extend(self._encode_status(opp_poke.status))
            
            # Boosts (7 features each)
            features.extend(self._encode_boosts(my_poke.boosts))
            features.extend(self._encode_boosts(opp_poke.boosts))
            
            # Type advantages for first move (if available)
            if my_poke.available_moves:
                effectiveness = self._calculate_effectiveness(
                    my_poke.available_moves[0].type,
                    opp_poke.types
                )
                features.append(effectiveness)
            else:
                features.append(1.0)
        else:
            # No active Pokemon - return zeros
            features = [0.0] * 38
        
        # Pad or trim to expected size (38 features)
        while len(features) < 38:
            features.append(0.0)
        
        return np.array(features[:38], dtype=np.float32)

    def _encode_status(self, status: Status) -> List[float]:
        """One-hot encode status condition."""
        encoding = [0.0] * 7
        status_map = {
            Status.FNT: 0,
            Status.BRN: 1,
            Status.FRZ: 2,
            Status.PAR: 3,
            Status.PSN: 4,
            Status.SLP: 5,
            Status.TOX: 6
        }
        if status in status_map:
            encoding[status_map[status]] = 1.0
        return encoding

    def _encode_boosts(self, boosts: dict) -> List[float]:
        """Encode stat boosts (atk, def, spa, spd, spe, acc, eva)."""
        boost_keys = ["atk", "def", "spa", "spd", "spe", "accuracy", "evasion"]
        encoding = []
        for key in boost_keys:
            encoding.append(float(boosts.get(key, 0)) / 6.0)  # Normalize -6 to +6 → -1 to +1
        return encoding

    def _calculate_effectiveness(self, move_type, defender_types) -> float:
        """
        Calculate type effectiveness multiplier.
        Simplified - in real version would use type chart.
        """
        # Placeholder - real implementation would use actual type chart
        return 1.0

    def _choose_top_legal_move(
        self,
        priorities: List[float],
        battle_state: BattleState
    ) -> MoveDecision:
        """
        Choose the highest priority legal move.
        
        Args:
            priorities: Priority scores from neural network
            battle_state: Current battle state
            
        Returns:
            Move decision
        """
        if not battle_state.my_active_pokemon:
            return MoveDecision.forfeit()
        
        num_moves = len(battle_state.my_active_pokemon.available_moves)
        
        if num_moves == 0:
            return MoveDecision.forfeit()
        
        # Choose move with highest priority
        # Priorities array: [move0, move1, move2, move3, switch, ...]
        # For simplicity, just use first N priorities for N moves
        move_priorities = priorities[:num_moves]
        
        if move_priorities:
            best_move_idx = int(np.argmax(move_priorities))
            return MoveDecision.move(best_move_idx)
        
        return MoveDecision.move(0)  # Default to first move
