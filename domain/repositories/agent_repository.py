"""
Agent repository interface - for persisting agents.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ..entities.agent import Agent


class IAgentRepository(ABC):
    """
    Repository interface for agent persistence.
    Infrastructure layer implements this using files, database, etc.
    """
    
    @abstractmethod
    def save_agent(self, agent: Agent) -> None:
        """
        Save an agent.
        
        Args:
            agent: Agent to save
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent or None if not found
        """
        pass

    @abstractmethod
    def get_all_agents(self) -> List[Agent]:
        """
        Get all agents.
        
        Returns:
            List of all agents
        """
        pass

    @abstractmethod
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def update_agent(self, agent: Agent) -> None:
        """
        Update an existing agent.
        
        Args:
            agent: Agent with updated data
        """
        pass

    @abstractmethod
    def save_hall_of_fame(
        self, 
        generation: int, 
        agent: Agent,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Save a hall of fame winner.
        
        Args:
            generation: Generation/round number
            agent: Winning agent
            metadata: Additional metadata to save
        """
        pass

    @abstractmethod
    def get_hall_of_fame(self, generation: int) -> Optional[Agent]:
        """
        Get hall of fame winner for a generation.
        
        Args:
            generation: Generation number
            
        Returns:
            Agent or None if not found
        """
        pass

    @abstractmethod
    def agent_exists(self, agent_id: str) -> bool:
        """
        Check if agent exists.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if exists
        """
        pass
