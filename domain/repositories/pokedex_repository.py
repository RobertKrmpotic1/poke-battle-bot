"""
Pokedex repository interface - for accessing Pokemon data.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ..entities.pokemon import Pokemon


class IPokedexRepository(ABC):
    """
    Repository interface for accessing Pokedex data.
    Infrastructure layer implements this using CSV files, database, API, etc.
    """
    
    @abstractmethod
    def get_pokemon(self, species: str) -> Optional[Pokemon]:
        """
        Get Pokemon by species name.
        
        Args:
            species: Pokemon species name
            
        Returns:
            Pokemon entity or None if not found
        """
        pass

    @abstractmethod
    def get_all_pokemon(self, battle_format: str) -> Dict[str, Pokemon]:
        """
        Get all Pokemon available in a battle format.
        
        Args:
            battle_format: Battle format (e.g., "gen1ou")
            
        Returns:
            Dictionary mapping species name to Pokemon
        """
        pass

    @abstractmethod
    def get_available_species(self, battle_format: str) -> List[str]:
        """
        Get list of available Pokemon species for a format.
        
        Args:
            battle_format: Battle format
            
        Returns:
            List of species names
        """
        pass

    @abstractmethod
    def get_banned_pokemon(self, battle_format: str) -> List[str]:
        """
        Get banned Pokemon for a format.
        
        Args:
            battle_format: Battle format
            
        Returns:
            List of banned Pokemon names
        """
        pass

    @abstractmethod
    def get_banned_moves(self, battle_format: str) -> List[str]:
        """
        Get banned moves for a format.
        
        Args:
            battle_format: Battle format
            
        Returns:
            List of banned move names
        """
        pass

    @abstractmethod
    def get_banned_items(self, battle_format: str) -> List[str]:
        """
        Get banned items for a format.
        
        Args:
            battle_format: Battle format
            
        Returns:
            List of banned item names
        """
        pass

    @abstractmethod
    def create_random_pokemon(self, species: str) -> Pokemon:
        """
        Create a Pokemon with random moves, ability, etc.
        
        Args:
            species: Pokemon species
            
        Returns:
            Randomized Pokemon
        """
        pass

    @abstractmethod
    def get_generation(self, battle_format: str) -> int:
        """
        Get generation number from battle format.
        
        Args:
            battle_format: Battle format (e.g., "gen1ou")
            
        Returns:
            Generation number
        """
        pass
