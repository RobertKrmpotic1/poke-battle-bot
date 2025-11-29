"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_pokemon():
    """Fixture providing a sample Pokemon"""
    from domain.entities.pokemon import Pokemon
    
    return Pokemon(
        name="pikachu",
        types=["Electric"],
        possible_abilities=["static", "lightningrod"],
        possible_moves=["thunderbolt", "quickattack", "irontail", "thunderwave", "surf"],
        moves=["thunderbolt", "quickattack", "irontail", "thunderwave"],
        ability="static"
    )


@pytest.fixture
def sample_team():
    """Fixture providing a sample team"""
    from domain.entities.team import Team
    from domain.entities.pokemon import Pokemon
    
    team = Team(battle_format="gen1ou")
    
    for i in range(6):
        pokemon = Pokemon(
            name=f"pokemon{i}",
            types=["Normal"],
            possible_abilities=["test"],
            possible_moves=["tackle", "growl", "scratch", "bite"],
            moves=["tackle", "growl", "scratch", "bite"],
            ability="test"
        )
        team.add_pokemon(pokemon)
    
    return team


@pytest.fixture
def sample_agent():
    """Fixture providing a sample agent"""
    from domain.entities.agent import Agent
    
    return Agent(
        agent_id="TestBot",
        battle_format="gen1randombattle",
        elo=1000
    )


@pytest.fixture
def rating_service():
    """Fixture providing a rating service"""
    from domain.services.rating_service import RatingService
    
    return RatingService(k_value=50)


@pytest.fixture
def neural_network():
    """Fixture providing a neural network"""
    from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
    
    nn = TensorFlowNeuralNetwork()
    nn.initialize_random((38,), 5)
    return nn


@pytest.fixture
def pokedex_repository():
    """Fixture providing a Pokedex repository"""
    from infrastructure.repositories.csv_pokedex_repository import CSVPokedexRepository
    
    return CSVPokedexRepository(battle_format="gen1ou")
