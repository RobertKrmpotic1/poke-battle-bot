"""
Move decision value object - represents a battle decision.
Decoupled from poke_env BattleOrder.
"""
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class DecisionType(Enum):
    """Type of battle decision."""
    MOVE = "move"
    SWITCH = "switch"
    FORFEIT = "forfeit"


@dataclass(frozen=True)
class MoveDecision:
    """
    Immutable value object representing a battle decision.
    Can be a move, switch, or forfeit.
    """
    decision_type: DecisionType
    move_index: Optional[int] = None  # Index of move to use (0-3)
    switch_target: Optional[int] = None  # Index of Pokemon to switch to (0-5)
    mega_evolve: bool = False
    z_move: bool = False
    dynamax: bool = False
    
    def __post_init__(self):
        """Validate decision."""
        if self.decision_type == DecisionType.MOVE:
            if self.move_index is None:
                raise ValueError("Move decision requires move_index")
            if not 0 <= self.move_index <= 3:
                raise ValueError(f"Move index must be 0-3, got {self.move_index}")
        elif self.decision_type == DecisionType.SWITCH:
            if self.switch_target is None:
                raise ValueError("Switch decision requires switch_target")
            if not 0 <= self.switch_target <= 5:
                raise ValueError(f"Switch target must be 0-5, got {self.switch_target}")

    @classmethod
    def move(cls, index: int, mega: bool = False, z: bool = False, dmax: bool = False) -> 'MoveDecision':
        """Create a move decision."""
        return cls(
            decision_type=DecisionType.MOVE,
            move_index=index,
            mega_evolve=mega,
            z_move=z,
            dynamax=dmax
        )

    @classmethod
    def switch(cls, target: int) -> 'MoveDecision':
        """Create a switch decision."""
        return cls(
            decision_type=DecisionType.SWITCH,
            switch_target=target
        )

    @classmethod
    def forfeit(cls) -> 'MoveDecision':
        """Create a forfeit decision."""
        return cls(decision_type=DecisionType.FORFEIT)

    def is_move(self) -> bool:
        """Check if this is a move decision."""
        return self.decision_type == DecisionType.MOVE

    def is_switch(self) -> bool:
        """Check if this is a switch decision."""
        return self.decision_type == DecisionType.SWITCH

    def is_forfeit(self) -> bool:
        """Check if this is a forfeit decision."""
        return self.decision_type == DecisionType.FORFEIT

    def __repr__(self) -> str:
        if self.is_move():
            extras = []
            if self.mega_evolve:
                extras.append("MEGA")
            if self.z_move:
                extras.append("Z")
            if self.dynamax:
                extras.append("DMAX")
            extra_str = f" ({', '.join(extras)})" if extras else ""
            return f"MoveDecision(MOVE {self.move_index}{extra_str})"
        elif self.is_switch():
            return f"MoveDecision(SWITCH to {self.switch_target})"
        else:
            return "MoveDecision(FORFEIT)"
