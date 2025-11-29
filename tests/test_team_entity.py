"""
Tests for Team entity - comprehensive coverage.
Focus on increasing coverage from 53% to >90%.
"""
import pytest
from domain.entities.team import Team
from domain.entities.pokemon import Pokemon


@pytest.fixture
def sample_pokemon():
    """Create a sample Pokemon."""
    return Pokemon(
        name="pikachu",
        types=["Electric"],
        possible_abilities=["static"],
        possible_moves=["thunderbolt", "quickattack"],
        moves=["thunderbolt", "quickattack"],
        ability="static"
    )


@pytest.fixture
def full_team():
    """Create a full team of 6 Pokemon."""
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


class TestTeamCreation:
    """Test team creation and initialization."""
    
    def test_create_empty_team(self):
        """Test creating an empty team."""
        team = Team(battle_format="gen1ou")
        
        assert team.battle_format == "gen1ou"
        assert len(team.pokemon_list) == 0
    
    def test_create_team_with_pokemon(self, sample_pokemon):
        """Test creating team with Pokemon list."""
        team = Team(
            pokemon_list=[sample_pokemon],
            battle_format="gen1ou"
        )
        
        assert len(team.pokemon_list) == 1
    
    def test_create_team_too_many_pokemon_raises_error(self):
        """Test that creating team with >6 Pokemon raises error."""
        pokemon_list = []
        for i in range(7):
            pokemon = Pokemon(
                name=f"pokemon{i}",
                types=["Normal"],
                possible_abilities=["test"],
                possible_moves=["tackle"],
                moves=["tackle"],
                ability="test"
            )
            pokemon_list.append(pokemon)
        
        with pytest.raises(ValueError, match="cannot have more than 6 Pokemon"):
            Team(pokemon_list=pokemon_list, battle_format="gen1ou")


class TestTeamSize:
    """Test team size methods."""
    
    def test_len_operator(self, full_team):
        """Test len() operator."""
        assert len(full_team.pokemon_list) == 6
    
    def test_is_full_true(self, full_team):
        """Test is_full with full team."""
        assert full_team.is_full() is True
    
    def test_is_full_false(self):
        """Test is_full with partial team."""
        pokemon = Pokemon(
            name="test",
            types=["Normal"],
            possible_abilities=["test"],
            possible_moves=["tackle"],
            moves=["tackle"],
            ability="test"
        )
        team = Team(pokemon_list=[pokemon], battle_format="gen1ou")
        
        assert team.is_full() is False
    
    def test_is_empty_true(self):
        """Test is_empty with empty team."""
        team = Team(battle_format="gen1ou")
        
        assert team.is_empty() is True
    
    def test_is_empty_false(self, full_team):
        """Test is_empty with non-empty team."""
        assert full_team.is_empty() is False


class TestTeamStateChecks:
    """Test team state checking methods."""
    
    def test_is_valid_true(self, full_team):
        """Test is_valid with valid team."""
        assert full_team.is_valid() is True
    
    def test_is_valid_empty_team(self):
        """Test is_valid with empty team (should be valid)."""
        team = Team(battle_format="gen1ou")
        
        assert team.is_valid() is True


class TestHasDuplicateSpecies:
    """Test checking for duplicate Pokemon species."""
    
    def test_no_duplicates(self, full_team):
        """Test team with no duplicate species."""
        # full_team has pokemon0-pokemon5, all different
        assert full_team.has_duplicate_species() is False
    
    def test_has_duplicates(self):
        """Test team with duplicate species."""
        pokemon_list = []
        
        # Add same species twice
        for i in range(2):
            pokemon = Pokemon(
                name="pikachu",
                types=["Electric"],
                possible_abilities=["static"],
                possible_moves=["thunderbolt"],
                moves=["thunderbolt"],
                ability="static"
            )
            pokemon_list.append(pokemon)
        
        team = Team(pokemon_list=pokemon_list, battle_format="gen1ou")
        
        assert team.has_duplicate_species() is True


class TestTeamCopy:
    """Test copying teams."""
    
    def test_copy_creates_new_team(self, full_team):
        """Test that copy creates a new team instance."""
        copy = full_team.copy()
        
        assert copy is not full_team
        assert isinstance(copy, Team)
    
    def test_copy_preserves_format(self, full_team):
        """Test that copy preserves battle format."""
        copy = full_team.copy()
        
        assert copy.battle_format == full_team.battle_format
    
    def test_copy_preserves_pokemon(self, full_team):
        """Test that copy preserves Pokemon."""
        copy = full_team.copy()
        
        assert len(copy.pokemon_list) == len(full_team.pokemon_list)
        for i in range(len(full_team.pokemon_list)):
            assert copy.pokemon_list[i].name == full_team.pokemon_list[i].name
    
    def test_copy_creates_new_pokemon_instances(self, full_team):
        """Test that copy creates new Pokemon instances."""
        copy = full_team.copy()
        
        # Pokemon should be different instances
        assert copy.pokemon_list[0] is not full_team.pokemon_list[0]


class TestTeamIteration:
    """Test iterating over team."""
    
    def test_iterate_over_team(self, full_team):
        """Test iterating over team Pokemon."""
        pokemon_names = []
        for pokemon in full_team:
            pokemon_names.append(pokemon.name)
        
        assert len(pokemon_names) == 6
        assert pokemon_names == [f"pokemon{i}" for i in range(6)]


class TestTeamStringRepresentations:
    """Test string representations of team."""
    
    def test_repr(self, full_team):
        """Test __repr__ method."""
        repr_str = repr(full_team)
        
        assert "6" in repr_str
        assert "gen1ou" in repr_str
    
    def test_str(self, full_team):
        """Test __str__ method."""
        str_repr = str(full_team)
        
        assert "gen1ou" in str_repr
        assert any(f"pokemon{i}" in str_repr for i in range(6))
