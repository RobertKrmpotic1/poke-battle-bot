"""
Team validator port - interface for validating teams.
This abstracts away Pokemon Showdown subprocess validation.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from domain.entities.team import Team


@dataclass
class ValidationError:
    """Error found during team validation."""
    error_type: str  # "illegal_pokemon", "illegal_move", "illegal_item", etc.
    message: str
    pokemon_index: Optional[int] = None


class ITeamValidator(ABC):
    """
    Port interface for validating Pokemon teams.
    Infrastructure layer implements this using Pokemon Showdown validation.
    """
    
    @abstractmethod
    async def validate_team(self, team: Team) -> tuple[bool, List[ValidationError]]:
        """
        Validate a team for a specific battle format.
        
        Args:
            team: Team to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        pass

    @abstractmethod
    async def validate_teams(
        self, 
        teams: List[Team]
    ) -> dict[str, tuple[bool, List[ValidationError]]]:
        """
        Validate multiple teams concurrently.
        
        Args:
            teams: List of teams to validate
            
        Returns:
            Dictionary mapping team_id to (is_valid, errors)
        """
        pass

    @abstractmethod
    def is_pokemon_legal(self, pokemon_name: str, battle_format: str) -> bool:
        """
        Check if a Pokemon is legal in a format.
        
        Args:
            pokemon_name: Name of Pokemon
            battle_format: Battle format (e.g., "gen1ou")
            
        Returns:
            True if legal
        """
        pass

    @abstractmethod
    def is_move_legal(self, move_name: str, battle_format: str) -> bool:
        """
        Check if a move is legal in a format.
        
        Args:
            move_name: Name of move
            battle_format: Battle format
            
        Returns:
            True if legal
        """
        pass

    @abstractmethod
    def is_item_legal(self, item_name: str, battle_format: str) -> bool:
        """
        Check if an item is legal in a format.
        
        Args:
            item_name: Name of item
            battle_format: Battle format
            
        Returns:
            True if legal
        """
        pass
