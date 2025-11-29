"""
Tests for GenerateTeam use case.
Focus on application layer logic with mocked dependencies.
"""
import pytest
from unittest.mock import Mock
from application.use_cases.generate_team import GenerateTeam
from domain.entities.team import Team
from domain.entities.pokemon import Pokemon
from domain.services.mutation_service import MutationService


@pytest.fixture
def mock_pokedex_repository():
    """Create a mock Pokedex repository."""
    repo = Mock()
    repo.get_available_species.return_value = [
        "bulbasaur", "charmander", "squirtle", "pikachu", "eevee", "mewtwo"
    ]
    
    def create_random_pokemon(species):
        return Pokemon(
            name=species,
            types=["Normal"],
            possible_abilities=["test"],
            possible_moves=["tackle", "scratch"],
            moves=["tackle", "scratch"],
            ability="test"
        )
    
    repo.create_random_pokemon.side_effect = create_random_pokemon
    return repo


@pytest.fixture
def mutation_service():
    """Create a mutation service."""
    return MutationService(pokemon_mutation_rate=2, new_pokemon_rate=16)


@pytest.fixture
def generate_team_use_case(mock_pokedex_repository, mutation_service):
    """Create GenerateTeam use case with mocked dependencies."""
    return GenerateTeam(
        pokedex_repository=mock_pokedex_repository,
        mutation_service=mutation_service
    )


class TestGenerateTeamInit:
    """Test GenerateTeam initialization."""
    
    def test_init_without_validator(self, mock_pokedex_repository, mutation_service):
        """Test initialization without team validator."""
        use_case = GenerateTeam(
            pokedex_repository=mock_pokedex_repository,
            mutation_service=mutation_service
        )
        
        assert use_case.pokedex_repository is mock_pokedex_repository
        assert use_case.mutation_service is mutation_service
        assert use_case.team_validator is None


class TestExecute:
    """Test execute method."""
    
    def test_execute_generates_team(self, generate_team_use_case):
        """Test that execute generates a team."""
        team, errors = generate_team_use_case.execute(
            battle_format="gen1randombattle",
            team_size=6
        )
        
        assert isinstance(team, Team)
        assert len(team.pokemon_list) == 6
    
    def test_execute_custom_team_size(self, generate_team_use_case):
        """Test generating team with custom size."""
        team, errors = generate_team_use_case.execute(
            battle_format="gen1randombattle",
            team_size=3
        )
        
        assert len(team.pokemon_list) == 3
    
    def test_execute_calls_repository(self, generate_team_use_case, mock_pokedex_repository):
        """Test that execute calls repository methods."""
        team, errors = generate_team_use_case.execute(
            battle_format="gen1randombattle",
            team_size=6
        )
        
        mock_pokedex_repository.get_available_species.assert_called_once_with("gen1randombattle")
        assert mock_pokedex_repository.create_random_pokemon.call_count == 6
    
    def test_execute_no_available_species_raises_error(self, mutation_service):
        """Test that no available species raises error."""
        empty_repo = Mock()
        empty_repo.get_available_species.return_value = []
        
        use_case = GenerateTeam(
            pokedex_repository=empty_repo,
            mutation_service=mutation_service
        )
        
        with pytest.raises(ValueError, match="No Pokemon available"):
            use_case.execute(battle_format="invalid_format", team_size=6)


class TestExecuteMultiple:
    """Test execute_multiple method."""
    
    def test_execute_multiple_generates_teams(self, generate_team_use_case):
        """Test generating multiple teams."""
        teams = generate_team_use_case.execute_multiple(
            count=3,
            battle_format="gen1randombattle",
            team_size=6
        )
        
        assert len(teams) == 3
        assert all(isinstance(t[0], Team) for t in teams)
    
    def test_execute_multiple_all_teams_have_pokemon(self, generate_team_use_case):
        """Test that all generated teams have Pokemon."""
        teams = generate_team_use_case.execute_multiple(
            count=5,
            battle_format="gen1randombattle",
            team_size=6
        )
        
        for team, errors in teams:
            assert len(team.pokemon_list) == 6


class TestMutateExistingTeam:
    """Test mutate_existing_team method."""
    
    def test_mutate_existing_team(self, generate_team_use_case):
        """Test mutating an existing team."""
        # First generate a base team
        base_team, _ = generate_team_use_case.execute(
            battle_format="gen1randombattle",
            team_size=6
        )
        
        # Then mutate it
        mutated_team, errors = generate_team_use_case.mutate_existing_team(
            base_team=base_team
        )
        
        assert isinstance(mutated_team, Team)
        assert len(mutated_team.pokemon_list) == len(base_team.pokemon_list)
        assert mutated_team is not base_team  # Should be a new instance
    
    def test_mutate_preserves_battle_format(self, generate_team_use_case):
        """Test that mutation preserves battle format."""
        base_team, _ = generate_team_use_case.execute(
            battle_format="gen1ou",
            team_size=6
        )
        
        mutated_team, errors = generate_team_use_case.mutate_existing_team(
            base_team=base_team
        )
        
        assert mutated_team.battle_format == base_team.battle_format
