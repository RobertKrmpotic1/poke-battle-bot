"""
Tournament service - pairing and bracket logic.
Extracted from league.py and tournament.py.
"""
from typing import List, Tuple
from ..entities.agent import Agent


class TournamentService:
    """
    Service for tournament organization and pairing logic.
    Pure domain logic with no external dependencies.
    """
    
    def create_round_robin_pairings(self, agents: List[Agent]) -> List[Tuple[str, str]]:
        """
        Create round-robin pairings for a list of agents.
        Each agent plays every other agent once.
        
        Args:
            agents: List of agents to pair
            
        Returns:
            List of tuples (agent_id_1, agent_id_2)
        """
        pairings = []
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                pairings.append((agents[i].agent_id, agents[j].agent_id))
        return pairings

    def create_sorted_pairings(self, agents: List[Agent]) -> List[Tuple[str, str]]:
        """
        Create pairings by sorting agents by ELO and pairing adjacent agents.
        Used in league play where top agent plays second, third plays fourth, etc.
        
        Args:
            agents: List of agents to pair
            
        Returns:
            List of tuples (agent_id_1, agent_id_2)
        """
        # Sort by ELO descending
        sorted_agents = sorted(agents, key=lambda a: a.elo, reverse=True)
        
        # Pair adjacent agents
        pairings = []
        for i in range(0, len(sorted_agents) - 1, 2):
            pairings.append((sorted_agents[i].agent_id, sorted_agents[i + 1].agent_id))
        
        return pairings

    def create_random_pairings(
        self, 
        agents: List[Agent], 
        matches_per_agent: int = 1
    ) -> List[Tuple[str, str]]:
        """
        Create random pairings where each agent plays N matches.
        
        Args:
            agents: List of agents
            matches_per_agent: How many matches each agent should play
            
        Returns:
            List of tuples (agent_id_1, agent_id_2)
        """
        import random
        
        pairings = []
        agent_ids = [a.agent_id for a in agents]
        
        for _ in range(matches_per_agent):
            shuffled = agent_ids.copy()
            random.shuffle(shuffled)
            
            for i in range(0, len(shuffled) - 1, 2):
                pairings.append((shuffled[i], shuffled[i + 1]))
        
        return pairings

    def select_top_agents(self, agents: List[Agent], n: int) -> List[Agent]:
        """
        Select top N agents by ELO rating.
        
        Args:
            agents: List of agents
            n: Number of top agents to select
            
        Returns:
            List of top N agents sorted by ELO descending
        """
        sorted_agents = sorted(agents, key=lambda a: a.elo, reverse=True)
        return sorted_agents[:n]

    def select_bottom_agents(self, agents: List[Agent], n: int) -> List[Agent]:
        """
        Select bottom N agents by ELO rating.
        
        Args:
            agents: List of agents
            n: Number of bottom agents to select
            
        Returns:
            List of bottom N agents sorted by ELO ascending
        """
        sorted_agents = sorted(agents, key=lambda a: a.elo)
        return sorted_agents[:n]

    def create_elimination_bracket(
        self, 
        agents: List[Agent], 
        seeded: bool = True
    ) -> List[List[Tuple[str, str]]]:
        """
        Create single-elimination tournament bracket.
        
        Args:
            agents: List of agents (should be power of 2)
            seeded: If True, seed by ELO rating (1 vs n, 2 vs n-1, etc.)
            
        Returns:
            List of rounds, each containing list of pairings
        """
        if seeded:
            sorted_agents = sorted(agents, key=lambda a: a.elo, reverse=True)
        else:
            import random
            sorted_agents = agents.copy()
            random.shuffle(sorted_agents)
        
        rounds = []
        current_round = sorted_agents
        
        while len(current_round) > 1:
            pairings = []
            for i in range(0, len(current_round), 2):
                if i + 1 < len(current_round):
                    pairings.append((
                        current_round[i].agent_id,
                        current_round[i + 1].agent_id
                    ))
            
            rounds.append(pairings)
            # For next round, we'd need winners, but that's application layer
            # This just returns the bracket structure
            current_round = current_round[:len(current_round) // 2]
        
        return rounds

    def calculate_league_standings(self, agents: List[Agent]) -> List[Tuple[int, Agent]]:
        """
        Calculate league standings with ranking.
        
        Args:
            agents: List of agents
            
        Returns:
            List of tuples (rank, agent) sorted by ELO descending
        """
        sorted_agents = sorted(agents, key=lambda a: a.elo, reverse=True)
        return [(i + 1, agent) for i, agent in enumerate(sorted_agents)]
