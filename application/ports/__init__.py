"""Application ports - interfaces for external systems."""
from .battle_executor import IBattleExecutor, BattleResult
from .team_validator import ITeamValidator
from .neural_network import INeuralNetwork

__all__ = ['IBattleExecutor', 'BattleResult', 'ITeamValidator', 'INeuralNetwork']
