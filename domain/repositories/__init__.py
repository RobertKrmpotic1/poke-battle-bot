"""Domain repositories - interfaces for data persistence."""
from .pokedex_repository import IPokedexRepository
from .agent_repository import IAgentRepository
from .league_repository import ILeagueRepository

__all__ = ['IPokedexRepository', 'IAgentRepository', 'ILeagueRepository']
