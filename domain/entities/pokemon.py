"""
Pure Pokemon entity - no external dependencies.
Extracted from abstract_pokemon_class.py with infrastructure removed.
"""
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Pokemon:
    """
    Represents a Pokemon with its characteristics.
    Pure domain entity with no infrastructure dependencies.
    """
    name: str
    types: List[str]
    possible_abilities: List[str]
    possible_moves: List[str]
    moves: List[str] = field(default_factory=list)
    ability: Optional[str] = None
    evs: Optional[dict] = None
    nature: Optional[str] = None
    held_item: Optional[str] = None
    level: int = 100

    def __post_init__(self):
        """Validate Pokemon state after initialization."""
        if not self.name:
            raise ValueError("Pokemon must have a name")
        if not self.types:
            raise ValueError(f"Pokemon {self.name} must have at least one type")
        if len(self.moves) > 4:
            raise ValueError(f"Pokemon {self.name} cannot have more than 4 moves")

    def set_moves(self, moves: List[str]) -> None:
        """
        Set moves for the pokemon, validating they are learnable.
        
        Args:
            moves: List of move names to set
            
        Raises:
            ValueError: If move is not in possible_moves or more than 4 moves
        """
        if len(moves) > 4:
            raise ValueError(f"Cannot set more than 4 moves, got {len(moves)}")
        
        invalid_moves = [m for m in moves if m not in self.possible_moves]
        if invalid_moves:
            raise ValueError(
                f"Moves {invalid_moves} are not in possible moves for {self.name}"
            )
        
        self.moves = moves.copy()

    def set_ability(self, ability: str) -> None:
        """
        Set ability for the pokemon.
        
        Args:
            ability: Ability name
            
        Raises:
            ValueError: If ability is not in possible_abilities
        """
        if ability not in self.possible_abilities:
            raise ValueError(
                f"Ability {ability} not in possible abilities for {self.name}: "
                f"{self.possible_abilities}"
            )
        self.ability = ability

    def has_move(self, move_name: str) -> bool:
        """Check if pokemon knows a specific move."""
        return move_name in self.moves

    def can_learn_move(self, move_name: str) -> bool:
        """Check if pokemon can learn a specific move."""
        return move_name in self.possible_moves

    def is_valid(self) -> bool:
        """
        Check if pokemon is in a valid state.
        
        Returns:
            True if pokemon has required attributes set
        """
        return (
            bool(self.name) and
            bool(self.types) and
            len(self.moves) <= 4 and
            all(m in self.possible_moves for m in self.moves)
        )

    def copy(self) -> 'Pokemon':
        """Create a deep copy of this Pokemon."""
        return Pokemon(
            name=self.name,
            types=self.types.copy(),
            possible_abilities=self.possible_abilities.copy(),
            possible_moves=self.possible_moves.copy(),
            moves=self.moves.copy(),
            ability=self.ability,
            evs=self.evs.copy() if self.evs else None,
            nature=self.nature,
            held_item=self.held_item,
            level=self.level
        )

    def __repr__(self) -> str:
        return (
            f"Pokemon(name={self.name}, types={self.types}, "
            f"ability={self.ability}, moves={self.moves}, "
            f"nature={self.nature}, item={self.held_item})"
        )

    def __str__(self) -> str:
        return (
            f"{self.name} {self.types} "
            f"[ability: {self.ability}] "
            f"[moves: {self.moves}] "
            f"nature: {self.nature} "
            f"item: {self.held_item}"
        )
