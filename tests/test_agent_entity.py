"""
Tests for Agent entity - comprehensive coverage.
Focus on increasing coverage from 68% to >90%.
"""
import pytest
from domain.entities.agent import Agent
from domain.entities.team import Team
from domain.entities.pokemon import Pokemon


@pytest.fixture
def sample_agent():
    """Create a sample agent."""
    return Agent(
        agent_id="TestBot",
        elo=1000,
        battle_format="gen1randombattle"
    )


@pytest.fixture
def sample_team():
    """Create a sample team."""
    pokemon_list = []
    for i in range(6):
        pokemon = Pokemon(
            name=f"pokemon{i}",
            types=["Normal"],
            possible_abilities=["test"],
            possible_moves=["tackle", "growl"],
            moves=["tackle", "growl"],
            ability="test"
        )
        pokemon_list.append(pokemon)
    return Team(pokemon_list=pokemon_list, battle_format="gen1randombattle")


class TestAgentCreation:
    """Test agent creation and initialization."""
    
    def test_create_agent_basic(self):
        """Test creating an agent with basic parameters."""
        agent = Agent(agent_id="TestBot")
        
        assert agent.agent_id == "TestBot"
        assert agent.elo == 1000  # Default
        assert agent.wins == 0
        assert agent.losses == 0
        assert agent.draws == 0
        assert agent.battles == 0
    
    def test_create_agent_custom_elo(self):
        """Test creating agent with custom ELO."""
        agent = Agent(agent_id="TestBot", elo=1500)
        
        assert agent.elo == 1500
    
    def test_create_agent_with_team(self, sample_team):
        """Test creating agent with team."""
        agent = Agent(agent_id="TestBot", team=sample_team)
        
        assert agent.team == sample_team
    
    def test_create_agent_empty_id_raises_error(self):
        """Test that empty agent_id raises ValueError."""
        with pytest.raises(ValueError, match="Agent must have an ID"):
            Agent(agent_id="")
    
    def test_create_agent_negative_elo_raises_error(self):
        """Test that negative ELO raises ValueError."""
        with pytest.raises(ValueError, match="ELO rating cannot be negative"):
            Agent(agent_id="TestBot", elo=-100)
    
    def test_create_agent_with_generation(self):
        """Test creating agent with generation number."""
        agent = Agent(agent_id="TestBot", generation=5)
        
        assert agent.generation == 5


class TestAgentProperties:
    """Test agent computed properties."""
    
    def test_win_rate_no_battles(self, sample_agent):
        """Test win rate with no battles."""
        assert sample_agent.win_rate == 0.0
    
    def test_win_rate_all_wins(self, sample_agent):
        """Test win rate with all wins."""
        sample_agent.record_win()
        sample_agent.record_win()
        sample_agent.record_win()
        
        assert sample_agent.win_rate == 1.0
    
    def test_win_rate_mixed_results(self, sample_agent):
        """Test win rate with mixed results."""
        sample_agent.record_win()
        sample_agent.record_win()
        sample_agent.record_loss()
        sample_agent.record_draw()
        
        # 2 wins out of 4 battles = 0.5
        assert sample_agent.win_rate == 0.5
    
    def test_total_games(self, sample_agent):
        """Test total games calculation."""
        sample_agent.record_win()
        sample_agent.record_loss()
        sample_agent.record_draw()
        
        assert sample_agent.total_games == 3
        assert sample_agent.battles == 3


class TestRecordBattleResults:
    """Test recording battle results."""
    
    def test_record_win(self, sample_agent):
        """Test recording a win."""
        sample_agent.record_win()
        
        assert sample_agent.wins == 1
        assert sample_agent.battles == 1
        assert sample_agent.losses == 0
        assert sample_agent.draws == 0
    
    def test_record_loss(self, sample_agent):
        """Test recording a loss."""
        sample_agent.record_loss()
        
        assert sample_agent.losses == 1
        assert sample_agent.battles == 1
        assert sample_agent.wins == 0
    
    def test_record_draw(self, sample_agent):
        """Test recording a draw."""
        sample_agent.record_draw()
        
        assert sample_agent.draws == 1
        assert sample_agent.battles == 1
    
    def test_record_multiple_results(self, sample_agent):
        """Test recording multiple results."""
        sample_agent.record_win()
        sample_agent.record_win()
        sample_agent.record_loss()
        sample_agent.record_draw()
        
        assert sample_agent.wins == 2
        assert sample_agent.losses == 1
        assert sample_agent.draws == 1
        assert sample_agent.battles == 4


class TestResetBattleStats:
    """Test resetting battle statistics."""
    
    def test_reset_clears_stats(self, sample_agent):
        """Test that reset clears all battle stats."""
        sample_agent.record_win()
        sample_agent.record_win()
        sample_agent.record_loss()
        
        sample_agent.reset_battle_stats()
        
        assert sample_agent.wins == 0
        assert sample_agent.losses == 0
        assert sample_agent.draws == 0
        assert sample_agent.battles == 0
    
    def test_reset_preserves_elo(self, sample_agent):
        """Test that reset preserves ELO rating."""
        sample_agent.elo = 1500
        sample_agent.record_win()
        
        sample_agent.reset_battle_stats()
        
        assert sample_agent.elo == 1500


class TestUpdateElo:
    """Test ELO rating updates."""
    
    def test_update_elo_increase(self, sample_agent):
        """Test updating ELO to higher value."""
        sample_agent.update_elo(1100)
        
        assert sample_agent.elo == 1100
    
    def test_update_elo_decrease(self, sample_agent):
        """Test updating ELO to lower value."""
        sample_agent.update_elo(900)
        
        assert sample_agent.elo == 900
    
    def test_update_elo_negative_raises_error(self, sample_agent):
        """Test that negative ELO raises ValueError."""
        with pytest.raises(ValueError, match="ELO rating cannot be negative"):
            sample_agent.update_elo(-100)


class TestSetTeam:
    """Test setting agent team."""
    
    def test_set_team_valid(self, sample_agent, sample_team):
        """Test setting a valid team."""
        sample_agent.set_team(sample_team)
        
        assert sample_agent.team == sample_team
    
    def test_set_team_wrong_format_raises_error(self, sample_agent):
        """Test that team with wrong format raises ValueError."""
        pokemon = Pokemon(
            name="test",
            types=["Normal"],
            possible_abilities=["test"],
            possible_moves=["tackle"],
            moves=["tackle"],
            ability="test"
        )
        wrong_format_team = Team(pokemon_list=[pokemon], battle_format="gen2ou")
        
        with pytest.raises(ValueError, match="does not match"):
            sample_agent.set_team(wrong_format_team)


class TestHasTeam:
    """Test checking if agent has team."""
    
    def test_has_team_false_initially(self, sample_agent):
        """Test that agent initially has no team."""
        assert sample_agent.has_team() is False
    
    def test_has_team_true_after_set(self, sample_agent, sample_team):
        """Test that has_team returns True after setting team."""
        sample_agent.set_team(sample_team)
        
        assert sample_agent.has_team() is True


class TestAgentCopy:
    """Test creating copies of agents."""
    
    def test_copy_creates_new_instance(self, sample_agent):
        """Test that copy creates a new agent instance."""
        copy = sample_agent.copy("TestBot_Copy")
        
        assert copy is not sample_agent
        assert isinstance(copy, Agent)
    
    def test_copy_has_new_id(self, sample_agent):
        """Test that copy has the new ID."""
        copy = sample_agent.copy("NewBot")
        
        assert copy.agent_id == "NewBot"
    
    def test_copy_preserves_elo(self, sample_agent):
        """Test that copy preserves ELO."""
        sample_agent.elo = 1500
        copy = sample_agent.copy("Copy")
        
        assert copy.elo == 1500
    
    def test_copy_resets_stats(self, sample_agent):
        """Test that copy resets battle stats."""
        sample_agent.record_win()
        sample_agent.record_win()
        sample_agent.record_loss()
        
        copy = sample_agent.copy("Copy")
        
        assert copy.wins == 0
        assert copy.losses == 0
        assert copy.draws == 0
        assert copy.battles == 0
    
    def test_copy_increments_generation(self, sample_agent):
        """Test that copy increments generation."""
        sample_agent.generation = 5
        copy = sample_agent.copy("Copy")
        
        assert copy.generation == 6
    
    def test_copy_with_team(self, sample_agent, sample_team):
        """Test copying agent with team."""
        sample_agent.set_team(sample_team)
        copy = sample_agent.copy("Copy")
        
        assert copy.team is not None
        assert copy.team is not sample_agent.team  # Different instance


class TestAgentStringRepresentations:
    """Test string representations of agent."""
    
    def test_repr(self, sample_agent):
        """Test __repr__ method."""
        sample_agent.record_win()
        sample_agent.record_loss()
        
        repr_str = repr(sample_agent)
        
        assert "TestBot" in repr_str
        assert "1000" in repr_str  # ELO
        assert "1-1-0" in repr_str  # Record
    
    def test_str(self, sample_agent):
        """Test __str__ method."""
        sample_agent.record_win()
        sample_agent.record_loss()
        
        str_repr = str(sample_agent)
        
        assert "TestBot" in str_repr
        assert "1000" in str_repr  # ELO
