"""
Tests for TournamentService - Tournament pairing and organization logic.
Focus on domain logic without external dependencies.
"""
import pytest
from domain.services.tournament_service import TournamentService
from domain.entities.agent import Agent


@pytest.fixture
def tournament_service():
    """Create tournament service."""
    return TournamentService()


@pytest.fixture
def sample_agents():
    """Create a list of sample agents with varying ELO."""
    agents = []
    for i in range(8):
        agent = Agent(
            agent_id=f"Bot{i}",
            elo=1000 + i * 100,
            battle_format="gen1randombattle"
        )
        agents.append(agent)
    return agents


class TestCreateRoundRobinPairings:
    """Test round-robin pairing."""
    
    def test_round_robin_creates_all_pairs(self, tournament_service, sample_agents):
        """Test that round-robin creates all possible pairs."""
        pairings = tournament_service.create_round_robin_pairings(sample_agents)
        
        # With 8 agents, should have 8*7/2 = 28 pairings
        assert len(pairings) == 28
    
    def test_round_robin_no_duplicates(self, tournament_service, sample_agents):
        """Test that no agent is paired with themselves."""
        pairings = tournament_service.create_round_robin_pairings(sample_agents)
        
        for agent_a, agent_b in pairings:
            assert agent_a != agent_b
    
    def test_round_robin_two_agents(self, tournament_service):
        """Test round-robin with only 2 agents."""
        agents = [
            Agent(agent_id="Bot1", elo=1000),
            Agent(agent_id="Bot2", elo=1100)
        ]
        
        pairings = tournament_service.create_round_robin_pairings(agents)
        
        assert len(pairings) == 1
    
    def test_round_robin_empty_list(self, tournament_service):
        """Test round-robin with empty agent list."""
        pairings = tournament_service.create_round_robin_pairings([])
        assert pairings == []


class TestCreateSortedPairings:
    """Test sorted pairing (by ELO)."""
    
    def test_sorted_pairings_pairs_adjacent(self, tournament_service, sample_agents):
        """Test that sorted pairing pairs adjacent agents by ELO."""
        pairings = tournament_service.create_sorted_pairings(sample_agents)
        
        # With 8 agents, should have 4 pairings
        assert len(pairings) == 4
    
    def test_sorted_pairings_highest_first(self, tournament_service, sample_agents):
        """Test that highest ELO agents are in first pairing."""
        pairings = tournament_service.create_sorted_pairings(sample_agents)
        
        # Bot7 (ELO 1700) and Bot6 (ELO 1600) should be in first pairing
        first_pairing = pairings[0]
        assert "Bot7" in first_pairing
        assert "Bot6" in first_pairing
    
    def test_sorted_pairings_odd_number(self, tournament_service):
        """Test sorted pairing with odd number of agents."""
        agents = [
            Agent(agent_id=f"Bot{i}", elo=1000 + i * 100)
            for i in range(5)
        ]
        
        pairings = tournament_service.create_sorted_pairings(agents)
        
        # With 5 agents, should have 2 pairings (one agent unpaired)
        assert len(pairings) == 2


class TestCreateRandomPairings:
    """Test random pairing."""
    
    def test_random_pairings_correct_count(self, tournament_service, sample_agents):
        """Test that random pairing creates correct number of pairings."""
        pairings = tournament_service.create_random_pairings(sample_agents, matches_per_agent=1)
        
        # With 8 agents and 1 match each, should have 4 pairings
        assert len(pairings) == 4
    
    def test_random_pairings_multiple_matches(self, tournament_service, sample_agents):
        """Test random pairing with multiple matches per agent."""
        pairings = tournament_service.create_random_pairings(sample_agents, matches_per_agent=3)
        
        # With 8 agents and 3 matches each, should have 12 pairings
        assert len(pairings) == 12
    
    def test_random_pairings_no_self_pairing(self, tournament_service, sample_agents):
        """Test that agents are not paired with themselves."""
        pairings = tournament_service.create_random_pairings(sample_agents, matches_per_agent=2)
        
        for agent_a, agent_b in pairings:
            assert agent_a != agent_b


class TestSelectTopAgents:
    """Test selecting top agents by ELO."""
    
    def test_select_top_agents(self, tournament_service, sample_agents):
        """Test selecting top N agents."""
        top_3 = tournament_service.select_top_agents(sample_agents, 3)
        
        assert len(top_3) == 3
        assert top_3[0].agent_id == "Bot7"  # Highest ELO (1700)
        assert top_3[1].agent_id == "Bot6"  # Second (1600)
        assert top_3[2].agent_id == "Bot5"  # Third (1500)
    
    def test_select_top_more_than_available(self, tournament_service, sample_agents):
        """Test selecting more agents than available."""
        top_10 = tournament_service.select_top_agents(sample_agents, 10)
        
        assert len(top_10) == 8  # Only 8 agents available
    
    def test_select_top_zero(self, tournament_service, sample_agents):
        """Test selecting zero agents."""
        top_0 = tournament_service.select_top_agents(sample_agents, 0)
        
        assert len(top_0) == 0


class TestSelectBottomAgents:
    """Test selecting bottom agents by ELO."""
    
    def test_select_bottom_agents(self, tournament_service, sample_agents):
        """Test selecting bottom N agents."""
        bottom_3 = tournament_service.select_bottom_agents(sample_agents, 3)
        
        assert len(bottom_3) == 3
        assert bottom_3[0].agent_id == "Bot0"  # Lowest ELO (1000)
        assert bottom_3[1].agent_id == "Bot1"  # Second lowest (1100)
        assert bottom_3[2].agent_id == "Bot2"  # Third lowest (1200)


class TestCalculateLeagueStandings:
    """Test league standings calculation."""
    
    def test_calculate_standings(self, tournament_service, sample_agents):
        """Test calculating league standings."""
        standings = tournament_service.calculate_league_standings(sample_agents)
        
        assert len(standings) == 8
        
        # Check that standings are tuples of (rank, agent)
        assert all(isinstance(s, tuple) for s in standings)
        assert all(len(s) == 2 for s in standings)
    
    def test_standings_ranked_correctly(self, tournament_service, sample_agents):
        """Test that standings are ranked by ELO."""
        standings = tournament_service.calculate_league_standings(sample_agents)
        
        # Rank 1 should be highest ELO
        assert standings[0][0] == 1
        assert standings[0][1].agent_id == "Bot7"
        
        # Rank 8 should be lowest ELO
        assert standings[7][0] == 8
        assert standings[7][1].agent_id == "Bot0"
    
    def test_standings_empty_list(self, tournament_service):
        """Test standings with empty agent list."""
        standings = tournament_service.calculate_league_standings([])
        
        assert standings == []
