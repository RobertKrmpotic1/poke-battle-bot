"""
Pure Team aggregate - no external dependencies.
Extracted from team_generator.py with Teambuilder inheritance removed.
"""
from typing import List, Optional
from dataclasses import dataclass, field
from .pokemon import Pokemon


@dataclass
class Team:
    """
    Aggregate root representing a team of up to 6 Pokemon.
    Pure domain entity with no infrastructure dependencies.
    """
    pokemon_list: List[Pokemon] = field(default_factory=list)
    battle_format: str = "gen1ou"
    team_id: Optional[str] = None

    def __post_init__(self):
        """Validate team state after initialization."""
        if len(self.pokemon_list) > 6:
            raise ValueError(f"Team cannot have more than 6 Pokemon, got {len(self.pokemon_list)}")

    def add_pokemon(self, pokemon: Pokemon) -> None:
        """
        Add a pokemon to the team.
        
        Args:
            pokemon: Pokemon to add
            
        Raises:
            ValueError: If team already has 6 Pokemon
        """
        if len(self.pokemon_list) >= 6:
            raise ValueError("Cannot add more than 6 Pokemon to a team")
        if not pokemon.is_valid():
            raise ValueError(f"Cannot add invalid Pokemon: {pokemon}")
        self.pokemon_list.append(pokemon)

    def remove_pokemon(self, index: int) -> Pokemon:
        """
        Remove pokemon at given index.
        
        Args:
            index: Index of pokemon to remove
            
        Returns:
            The removed Pokemon
            
        Raises:
            IndexError: If index out of range
        """
        if not 0 <= index < len(self.pokemon_list):
            raise IndexError(f"Index {index} out of range for team of size {len(self.pokemon_list)}")
        return self.pokemon_list.pop(index)

    def replace_pokemon(self, index: int, pokemon: Pokemon) -> Pokemon:
        """
        Replace pokemon at given index with new pokemon.
        
        Args:
            index: Index to replace
            pokemon: New pokemon
            
        Returns:
            The old Pokemon that was replaced
            
        Raises:
            IndexError: If index out of range
            ValueError: If new pokemon is invalid
        """
        if not 0 <= index < len(self.pokemon_list):
            raise IndexError(f"Index {index} out of range for team of size {len(self.pokemon_list)}")
        if not pokemon.is_valid():
            raise ValueError(f"Cannot add invalid Pokemon: {pokemon}")
        
        old_pokemon = self.pokemon_list[index]
        self.pokemon_list[index] = pokemon
        return old_pokemon

    def get_pokemon(self, index: int) -> Pokemon:
        """Get pokemon at given index."""
        return self.pokemon_list[index]

    def size(self) -> int:
        """Return number of Pokemon in team."""
        return len(self.pokemon_list)

    def is_full(self) -> bool:
        """Check if team has 6 Pokemon."""
        return len(self.pokemon_list) == 6

    def is_empty(self) -> bool:
        """Check if team has no Pokemon."""
        return len(self.pokemon_list) == 0

    def is_valid(self) -> bool:
        """
        Check if team is in a valid state.
        
        Returns:
            True if all Pokemon are valid and team size is valid
        """
        return (
            0 <= len(self.pokemon_list) <= 6 and
            all(p.is_valid() for p in self.pokemon_list)
        )

    def has_duplicate_species(self) -> bool:
        """Check if team has duplicate Pokemon species."""
        species = [p.name for p in self.pokemon_list]
        return len(species) != len(set(species))

    def copy(self) -> 'Team':
        """Create a deep copy of this team."""
        return Team(
            pokemon_list=[p.copy() for p in self.pokemon_list],
            battle_format=self.battle_format,
            team_id=self.team_id
        )

    def __len__(self) -> int:
        return len(self.pokemon_list)

    def __iter__(self):
        return iter(self.pokemon_list)

    def __getitem__(self, index: int) -> Pokemon:
        return self.pokemon_list[index]

    def __repr__(self) -> str:
        return f"Team(size={len(self.pokemon_list)}, format={self.battle_format})"

    def __str__(self) -> str:
        pokemon_names = [p.name for p in self.pokemon_list]
        return f"Team[{self.battle_format}]: {pokemon_names}"
