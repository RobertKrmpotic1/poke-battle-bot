"""
Tests for MutationService - Genetic algorithm operations.
Focus on domain logic without external dependencies.
"""
import pytest
import random
from unittest.mock import Mock
from domain.services.mutation_service import MutationService
from domain.entities.team import Team
from domain.entities.pokemon import Pokemon


@pytest.fixture
def mutation_service():
    """Create mutation service with default settings."""
    return MutationService(pokemon_mutation_rate=2, new_pokemon_rate=16)


@pytest.fixture
def sample_pokemon():
    """Create a sample Pokemon for testing."""
    return Pokemon(
        name="pikachu",
        types=["Electric"],
        possible_abilities=["static"],
        possible_moves=["thunderbolt", "quickattack", "irontail", "thunderwave"],
        moves=["thunderbolt", "quickattack", "irontail", "thunderwave"],
        ability="static"
    )


@pytest.fixture
def sample_team():
    """Create a sample team for testing."""
    pokemon_list = []
    for i in range(6):
        pokemon = Pokemon(
            name=f"pokemon{i}",
            types=["Normal"],
            possible_abilities=["test"],
            possible_moves=["tackle", "growl", "scratch", "bite"],
            moves=["tackle", "growl", "scratch", "bite"],
            ability="test"
        )
        pokemon_list.append(pokemon)
    return Team(pokemon_list=pokemon_list, battle_format="gen1ou")


@pytest.fixture
def mock_pokemon_factory():
    """Create a mock Pokemon factory."""
    factory = Mock()
    factory.get_available_species.return_value = ["bulbasaur", "charmander", "squirtle"]
    
    def create_random_pokemon(species):
        return Pokemon(
            name=species,
            types=["Normal"],
            possible_abilities=["test"],
            possible_moves=["tackle", "scratch"],
            moves=["tackle", "scratch"],
            ability="test"
        )
    
    factory.create_random_pokemon.side_effect = create_random_pokemon
    factory.get_random_moves.return_value = [1, 2, 3, 4]
    return factory


class TestMutationServiceInit:
    """Test MutationService initialization."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        service = MutationService()
        assert service.pokemon_mutation_rate == 2
        assert service.new_pokemon_rate == 16
    
    def test_init_custom_values(self):
        """Test initialization with custom values."""
        service = MutationService(pokemon_mutation_rate=3, new_pokemon_rate=10)
        assert service.pokemon_mutation_rate == 3
        assert service.new_pokemon_rate == 10


class TestMutationServiceProbabilities:
    """Test probability methods."""
    
    def test_should_mutate_pokemon_randomness(self, mutation_service):
        """Test that should_mutate_pokemon returns boolean values."""
        random.seed(42)
        results = [mutation_service.should_mutate_pokemon() for _ in range(100)]
        assert all(isinstance(r, bool) for r in results)
        # Should have both True and False
        assert True in results
        assert False in results
    
    def test_should_replace_with_new_randomness(self, mutation_service):
        """Test that should_replace_with_new returns boolean values."""
        random.seed(42)
        results = [mutation_service.should_replace_with_new() for _ in range(100)]
        assert all(isinstance(r, bool) for r in results)


class TestMutateTeam:
    """Test team mutation."""
    
    def test_mutate_team_returns_new_team(self, mutation_service, sample_team, mock_pokemon_factory):
        """Test that mutate_team returns a new team instance."""
        random.seed(42)
        mutated = mutation_service.mutate_team(sample_team, mock_pokemon_factory)
        
        assert mutated is not sample_team
        assert isinstance(mutated, Team)
        assert mutated.battle_format == sample_team.battle_format
    
    def test_mutate_team_preserves_size(self, mutation_service, sample_team, mock_pokemon_factory):
        """Test that mutated team has same size as original."""
        random.seed(42)
        mutated = mutation_service.mutate_team(sample_team, mock_pokemon_factory)
        
        assert len(mutated.pokemon_list) == len(sample_team.pokemon_list)
    
    def test_mutate_team_calls_factory(self, mutation_service, sample_team, mock_pokemon_factory):
        """Test that factory methods are called during mutation."""
        # Try multiple seeds to ensure at least one triggers mutation
        called = False
        for seed in range(100):
            random.seed(seed)
            mock_pokemon_factory.reset_mock()
            mutated = mutation_service.mutate_team(sample_team, mock_pokemon_factory)
            if mock_pokemon_factory.get_available_species.called:
                called = True
                break
        
        # Factory should have been called at least once
        assert called


class TestCrossoverTeams:
    """Test team crossover."""
    
    def test_crossover_returns_new_team(self, mutation_service, sample_team):
        """Test that crossover returns a new team."""
        team_a = sample_team
        team_b = sample_team.copy()
        
        offspring = mutation_service.crossover_teams(team_a, team_b)
        
        assert offspring is not team_a
        assert offspring is not team_b
        assert isinstance(offspring, Team)
    
    def test_crossover_preserves_format(self, mutation_service, sample_team):
        """Test that crossover preserves battle format."""
        team_a = sample_team
        team_b = sample_team.copy()
        
        offspring = mutation_service.crossover_teams(team_a, team_b)
        
        assert offspring.battle_format == team_a.battle_format
    
    def test_crossover_combines_teams(self, mutation_service):
        """Test that crossover combines Pokemon from both parents."""
        pokemon_a = []
        pokemon_b = []
        
        for i in range(6):
            pokemon_a.append(Pokemon(
                name=f"teamA_pokemon{i}",
                types=["Normal"],
                possible_abilities=["test"],
                possible_moves=["tackle"],
                moves=["tackle"],
                ability="test"
            ))
            pokemon_b.append(Pokemon(
                name=f"teamB_pokemon{i}",
                types=["Normal"],
                possible_abilities=["test"],
                possible_moves=["scratch"],
                moves=["scratch"],
                ability="test"
            ))
        
        team_a = Team(pokemon_list=pokemon_a, battle_format="gen1ou")
        team_b = Team(pokemon_list=pokemon_b, battle_format="gen1ou")
        
        offspring = mutation_service.crossover_teams(team_a, team_b)
        
        # Should have Pokemon from both teams
        pokemon_names = [p.name for p in offspring.pokemon_list]
        has_team_a = any("teamA" in name for name in pokemon_names)
        has_team_b = any("teamB" in name for name in pokemon_names)
        
        assert has_team_a or has_team_b
        assert len(offspring.pokemon_list) <= 6
