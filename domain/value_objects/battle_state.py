"""
Battle state value objects - decoupled from poke_env.Battle.
Represents the observable state of a battle.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    """Pokemon status conditions."""
    NONE = "none"
    FNT = "fnt"  # Fainted
    BRN = "brn"  # Burn
    FRZ = "frz"  # Freeze
    PAR = "par"  # Paralysis
    PSN = "psn"  # Poison
    SLP = "slp"  # Sleep
    TOX = "tox"  # Toxic


class PokemonType(Enum):
    """Pokemon types for Gen 1."""
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    ELECTRIC = "Electric"
    GRASS = "Grass"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"


class MoveCategory(Enum):
    """Move categories."""
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


@dataclass(frozen=True)
class MoveInfo:
    """Information about a specific move."""
    name: str
    type: PokemonType
    category: MoveCategory
    power: int
    accuracy: int
    pp: int
    priority: int = 0


@dataclass(frozen=True)
class PokemonState:
    """
    Immutable snapshot of a Pokemon's state during battle.
    Decoupled from poke_env Pokemon object.
    """
    species: str
    current_hp: int
    max_hp: int
    level: int
    status: Status
    types: List[PokemonType]
    active: bool
    fainted: bool
    boosts: Dict[str, int]  # stat boosts: atk, def, spa, spd, spe, accuracy, evasion
    available_moves: List[MoveInfo]
    
    @property
    def hp_fraction(self) -> float:
        """Return HP as fraction of max."""
        if self.max_hp == 0:
            return 0.0
        return self.current_hp / self.max_hp

    def is_healthy(self) -> bool:
        """Check if Pokemon has >50% HP."""
        return self.hp_fraction > 0.5

    def has_status(self) -> bool:
        """Check if Pokemon has a status condition."""
        return self.status != Status.NONE


@dataclass(frozen=True)
class BattleState:
    """
    Immutable snapshot of the entire battle state.
    Decoupled from poke_env.Battle object.
    """
    # Active Pokemon
    my_active_pokemon: Optional[PokemonState]
    opponent_active_pokemon: Optional[PokemonState]
    
    # Teams
    my_team: List[PokemonState]
    opponent_team: List[PokemonState]
    
    # Battle metadata
    turn: int
    battle_tag: str
    finished: bool
    won: Optional[bool]  # None if not finished, True/False if won/lost
    
    # Field conditions
    weather: Optional[str] = None
    terrain: Optional[str] = None
    
    # Available actions (for decision making)
    can_switch: bool = True
    can_mega_evolve: bool = False
    can_z_move: bool = False
    can_dynamax: bool = False
    force_switch: bool = False
    
    def my_alive_count(self) -> int:
        """Count alive Pokemon on my team."""
        return sum(1 for p in self.my_team if not p.fainted)
    
    def opponent_alive_count(self) -> int:
        """Count alive Pokemon on opponent team."""
        return sum(1 for p in self.opponent_team if not p.fainted)
    
    def my_team_health(self) -> float:
        """Average HP fraction of my team."""
        if not self.my_team:
            return 0.0
        return sum(p.hp_fraction for p in self.my_team) / len(self.my_team)
    
    def opponent_team_health(self) -> float:
        """Average HP fraction of opponent team."""
        if not self.opponent_team:
            return 0.0
        return sum(p.hp_fraction for p in self.opponent_team) / len(self.opponent_team)
    
    def is_valid(self) -> bool:
        """Check if battle state is valid."""
        return (
            self.turn >= 0 and
            len(self.my_team) <= 6 and
            len(self.opponent_team) <= 6
        )
