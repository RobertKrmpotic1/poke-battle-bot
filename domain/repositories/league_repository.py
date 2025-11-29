"""
League repository interface - for persisting league state.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LeagueStanding:
    """Represents an agent's standing in the league."""
    agent_id: str
    rank: int
    elo: int
    wins: int
    losses: int
    draws: int
    battles: int


class ILeagueRepository(ABC):
    """
    Repository interface for league state persistence.
    Infrastructure layer implements this using CSV, database, etc.
    """
    
    @abstractmethod
    def save_standings(
        self, 
        standings: List[LeagueStanding],
        round_number: int
    ) -> None:
        """
        Save league standings for a round.
        
        Args:
            standings: List of standings
            round_number: Current round number
        """
        pass

    @abstractmethod
    def get_standings(self, round_number: int) -> List[LeagueStanding]:
        """
        Get standings for a specific round.
        
        Args:
            round_number: Round number
            
        Returns:
            List of standings
        """
        pass

    @abstractmethod
    def get_latest_standings(self) -> List[LeagueStanding]:
        """
        Get the most recent standings.
        
        Returns:
            List of standings
        """
        pass

    @abstractmethod
    def save_league_config(self, config: Dict) -> None:
        """
        Save league configuration.
        
        Args:
            config: Configuration dictionary
        """
        pass

    @abstractmethod
    def get_league_config(self) -> Optional[Dict]:
        """
        Get league configuration.
        
        Returns:
            Configuration dictionary or None
        """
        pass

    @abstractmethod
    def get_current_round(self) -> int:
        """
        Get current round number.
        
        Returns:
            Current round number
        """
        pass

    @abstractmethod
    def increment_round(self) -> int:
        """
        Increment and return new round number.
        
        Returns:
            New round number
        """
        pass

    @abstractmethod
    def save_match_result(
        self,
        round_number: int,
        agent_a_id: str,
        agent_b_id: str,
        winner: str,
        turns: int
    ) -> None:
        """
        Save individual match result.
        
        Args:
            round_number: Round number
            agent_a_id: First agent ID
            agent_b_id: Second agent ID
            winner: "a", "b", or "draw"
            turns: Number of turns
        """
        pass

    @abstractmethod
    def get_match_history(
        self, 
        agent_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get match history for an agent.
        
        Args:
            agent_id: Agent identifier
            limit: Maximum number of matches to return
            
        Returns:
            List of match dictionaries
        """
        pass
