"""
Comprehensive tests for hexagonal architecture

Tests are organized by layer: Domain, Application, Infrastructure, Integration
"""
import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock


# ============================================================================
# DOMAIN LAYER TESTS - Pure business logic, no infrastructure
# ============================================================================

class TestDomainEntities:
    """Test domain entities"""
    
    def test_pokemon_creation(self):
        """Test creating a Pokemon entity"""
        from domain.entities.pokemon import Pokemon
        
        pokemon = Pokemon(
            name="pikachu",
            types=["Electric"],
            possible_abilities=["static", "lightningrod"],
            possible_moves=["thunderbolt", "quickattack", "irontail", "thunderwave"],
            moves=["thunderbolt", "quickattack"],
            ability="static"
        )
        
        assert pokemon.name == "pikachu"
        assert pokemon.types == ["Electric"]
        assert pokemon.ability == "static"
        assert len(pokemon.moves) == 2
    
    def test_team_creation(self):
        """Test creating a Team aggregate"""
        from domain.entities.team import Team
        from domain.entities.pokemon import Pokemon
        
        team = Team(battle_format="gen1ou")
        assert team.size() == 0
        
        pokemon = Pokemon(
            name="charizard",
            types=["Fire", "Flying"],
            possible_abilities=["blaze"],
            possible_moves=["flamethrower", "fly"],
            moves=["flamethrower", "fly"],
            ability="blaze"
        )
        
        team.add_pokemon(pokemon)
        assert team.size() == 1
    
    def test_agent_creation(self):
        """Test creating an Agent entity"""
        from domain.entities.agent import Agent
        
        agent = Agent(agent_id="TestBot", elo=1000)
        assert agent.agent_id == "TestBot"
        assert agent.elo == 1000
        assert agent.wins == 0
        assert agent.total_games == 0
    
    def test_agent_record_win(self):
        """Test recording wins"""
        from domain.entities.agent import Agent
        
        agent = Agent(agent_id="TestBot", elo=1000)
        agent.record_win()
        
        assert agent.wins == 1
        assert agent.total_games == 1
    
    def test_agent_win_rate(self):
        """Test win rate calculation"""
        from domain.entities.agent import Agent
        
        agent = Agent(agent_id="TestBot", elo=1000)
        agent.record_win()
        agent.record_win()
        agent.record_loss()
        
        assert agent.win_rate == pytest.approx(2/3)
        assert agent.total_games == 3


class TestDomainValueObjects:
    """Test domain value objects"""
    
    def test_battle_state_creation(self):
        """Test creating a BattleState"""
        from domain.value_objects.battle_state import BattleState, PokemonState, Status, PokemonType
        
        my_pokemon = PokemonState(
            species="pikachu",
            current_hp=100,
            max_hp=100,
            level=50,
            status=Status.NONE,
            types=[PokemonType.ELECTRIC],
            active=True,
            fainted=False,
            boosts={},
            available_moves=[]
        )
        
        opp_pokemon = PokemonState(
            species="charizard",
            current_hp=100,
            max_hp=100,
            level=50,
            status=Status.NONE,
            types=[PokemonType.FIRE, PokemonType.FLYING],
            active=True,
            fainted=False,
            boosts={},
            available_moves=[]
        )
        
        state = BattleState(
            my_active_pokemon=my_pokemon,
            opponent_active_pokemon=opp_pokemon,
            my_team=[my_pokemon],
            opponent_team=[opp_pokemon],
            turn=1,
            battle_tag="test",
            finished=False,
            won=None,
            can_switch=True,
            force_switch=False
        )
        
        assert state.turn == 1
        assert not state.finished
    
    def test_move_decision_creation(self):
        """Test creating move decisions"""
        from domain.value_objects.move_decision import MoveDecision, DecisionType
        
        # Test move decision
        move_dec = MoveDecision.move(index=0)
        assert move_dec.decision_type == DecisionType.MOVE
        assert move_dec.move_index == 0
        assert move_dec.is_move()
        
        # Test switch decision
        switch_dec = MoveDecision.switch(target=1)
        assert switch_dec.decision_type == DecisionType.SWITCH
        assert switch_dec.switch_target == 1
        assert switch_dec.is_switch()
        
        # Test forfeit decision
        forfeit_dec = MoveDecision.forfeit()
        assert forfeit_dec.is_forfeit()


class TestDomainServices:
    """Test domain services"""
    
    def test_rating_service_equal_ratings(self):
        """Test ELO calculations for equal ratings"""
        from domain.services.rating_service import RatingService
        
        service = RatingService(k_value=50)
        new_r1, new_r2 = service.calculate_ratings_after_battle(1000, 1000, "a")
        
        assert new_r1 == 1025  # Winner gains 25
        assert new_r2 == 975   # Loser loses 25
    
    def test_rating_service_underdog_wins(self):
        """Test larger rating change when underdog wins"""
        from domain.services.rating_service import RatingService
        
        service = RatingService(k_value=50)
        new_r1, new_r2 = service.calculate_ratings_after_battle(1000, 1200, "a")
        
        # Underdog (1000) wins - should gain more than 25
        assert new_r1 > 1025
        # Favorite (1200) loses - should lose more than 25
        assert new_r2 < 1175
    
    def test_tournament_service_sorted_pairings(self):
        """Test creating sorted pairings"""
        from domain.services.tournament_service import TournamentService
        from domain.entities.agent import Agent
        
        service = TournamentService()
        agents = [Agent(agent_id=f"Bot{i}", elo=1000 + i*100) for i in range(8)]
        
        pairings = service.create_sorted_pairings(agents)
        
        assert len(pairings) == 4
        # First pairing should be top 2 ELO agents
        assert "Bot7" in pairings[0]  # Highest ELO (1700)
        assert "Bot6" in pairings[0]  # Second highest (1600)
    
    def test_tournament_service_select_top_agents(self):
        """Test selecting top agents by ELO"""
        from domain.services.tournament_service import TournamentService
        from domain.entities.agent import Agent
        
        service = TournamentService()
        agents = [Agent(agent_id=f"Bot{i}", elo=1000 + i*100) for i in range(10)]
        
        top_3 = service.select_top_agents(agents, n=3)
        
        assert len(top_3) == 3
        assert top_3[0].elo == 1900  # Highest
        assert top_3[1].elo == 1800
        assert top_3[2].elo == 1700


# ============================================================================
# APPLICATION LAYER TESTS - Use cases and ports
# ============================================================================

class TestApplicationPorts:
    """Test application layer port interfaces"""
    
    def test_battle_executor_port_exists(self):
        """Test IBattleExecutor port is defined"""
        from abc import ABC
        from application.ports.battle_executor import IBattleExecutor, BattleResult
        
        assert issubclass(IBattleExecutor, ABC)
        
        # Test BattleResult dataclass
        result = BattleResult(
            agent_a_id="bot1",
            agent_b_id="bot2",
            winner="a",
            turns=25,
            agent_a_final_hp=0.5,
            agent_b_final_hp=0.0
        )
        assert result.winner == "a"
    
    def test_neural_network_port_exists(self):
        """Test INeuralNetwork port is defined"""
        from abc import ABC
        from application.ports.neural_network import INeuralNetwork
        
        assert issubclass(INeuralNetwork, ABC)
        assert hasattr(INeuralNetwork, 'predict')
        assert hasattr(INeuralNetwork, 'mutate')
        assert hasattr(INeuralNetwork, 'save')
        assert hasattr(INeuralNetwork, 'load')


class TestApplicationUseCases:
    """Test application layer use cases"""
    
    @pytest.mark.asyncio
    async def test_execute_battle_use_case(self):
        """Test ExecuteBattle use case"""
        from application.use_cases.execute_battle import ExecuteBattle
        from application.ports.battle_executor import BattleResult
        from domain.services.rating_service import RatingService
        from domain.entities.agent import Agent
        
        # Mock battle executor
        mock_executor = Mock()
        mock_executor.execute_battle = AsyncMock(return_value=BattleResult(
            agent_a_id="bot1",
            agent_b_id="bot2",
            winner="a",
            turns=25,
            agent_a_final_hp=0.5,
            agent_b_final_hp=0.0
        ))
        
        rating_service = RatingService(k_value=50)
        use_case = ExecuteBattle(mock_executor, rating_service)
        
        agent_a = Agent(agent_id="bot1", elo=1000)
        agent_b = Agent(agent_id="bot2", elo=1000)
        
        result = await use_case.execute(agent_a, agent_b)
        
        assert result.winner == "a"
        assert agent_a.wins == 1
        assert agent_b.losses == 1


# ============================================================================
# INFRASTRUCTURE LAYER TESTS - Adapters and repositories
# ============================================================================

class TestInfrastructureAdapters:
    """Test infrastructure adapters"""
    
    def test_tensorflow_nn_adapter(self):
        """Test TensorFlow neural network adapter"""
        from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
        
        nn = TensorFlowNeuralNetwork()
        nn.initialize_random((38,), 5)
        
        # Test prediction
        input_data = np.random.rand(38)
        prediction = nn.predict(input_data)
        
        assert prediction.shape == (5,)
        assert isinstance(prediction, np.ndarray)
    
    def test_tensorflow_nn_mutation(self):
        """Test neural network mutation"""
        from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
        
        nn = TensorFlowNeuralNetwork()
        nn.initialize_random((38,), 5)
        
        initial_weights = [w.copy() for w in nn.get_weights()]
        nn.mutate(mutation_rate=0.1)
        new_weights = nn.get_weights()
        
        # At least some weights should have changed
        weights_changed = any(
            not np.array_equal(initial, new)
            for initial, new in zip(initial_weights, new_weights)
        )
        assert weights_changed
    
    def test_tensorflow_nn_save_load(self, tmp_path):
        """Test saving and loading neural network"""
        from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
        
        nn = TensorFlowNeuralNetwork()
        nn.initialize_random((38,), 5)
        
        input_data = np.random.rand(38)
        original_prediction = nn.predict(input_data)
        
        # Save (add .keras extension for Keras 3.0)
        save_path = tmp_path / "test_nn.keras"
        nn.save(str(save_path))
        
        # Load into new network
        nn2 = TensorFlowNeuralNetwork()
        nn2.load(str(save_path))
        
        # Should make same prediction
        new_prediction = nn2.predict(input_data)
        np.testing.assert_array_almost_equal(original_prediction, new_prediction)


class TestInfrastructureRepositories:
    """Test infrastructure repositories"""
    
    def test_csv_pokedex_repository(self):
        """Test CSV Pokedex repository"""
        from infrastructure.repositories.csv_pokedex_repository import CSVPokedexRepository
        
        repo = CSVPokedexRepository(battle_format="gen1ou")
        
        # Test getting available species
        species = repo.get_available_species("gen1ou")
        assert isinstance(species, list)
        assert len(species) > 0
        # Gen 1 should have around 150 Pokemon
        assert len(species) >= 100
    
    def test_csv_pokedex_random_pokemon(self):
        """Test creating random Pokemon"""
        from infrastructure.repositories.csv_pokedex_repository import CSVPokedexRepository
        
        repo = CSVPokedexRepository(battle_format="gen1ou")
        
        # Get a species first
        species = repo.get_available_species("gen1ou")
        if species:
            pokemon = repo.create_random_pokemon(species[0])
            assert pokemon is not None
            assert pokemon.name is not None
            assert len(pokemon.types) > 0


# ============================================================================
# INTEGRATION TESTS - Full architecture flow
# ============================================================================

class TestHexagonalArchitectureIntegration:
    """Test complete hexagonal architecture integration"""
    
    def test_domain_layer_isolation(self):
        """Verify domain layer has no infrastructure dependencies"""
        from domain.entities.pokemon import Pokemon
        from domain.entities.team import Team
        from domain.entities.agent import Agent
        
        # Should be able to create domain entities without infrastructure
        pokemon = Pokemon(
            name="pikachu",
            types=["Electric"],
            possible_abilities=["static"],
            possible_moves=["thunderbolt"],
            moves=["thunderbolt"],
            ability="static"
        )
        assert pokemon is not None
    
    def test_adapter_implements_port(self):
        """Test that infrastructure adapters implement application ports"""
        from application.ports.neural_network import INeuralNetwork
        from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
        
        nn = TensorFlowNeuralNetwork()
        nn.initialize_random((38,), 5)
        
        # Should implement the port interface
        assert isinstance(nn, INeuralNetwork)
    
    def test_repository_implements_port(self):
        """Test that repositories implement ports"""
        from domain.repositories.pokedex_repository import IPokedexRepository
        from infrastructure.repositories.csv_pokedex_repository import CSVPokedexRepository
        
        repo = CSVPokedexRepository(battle_format="gen1ou")
        
        # Should implement the port interface
        assert isinstance(repo, IPokedexRepository)
    
    def test_full_architecture_flow(self):
        """Test complete flow through all layers"""
        from domain.entities.agent import Agent
        from domain.services.rating_service import RatingService
        from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
        from infrastructure.adapters.nn_battle_strategy import NeuralNetworkStrategy
        from infrastructure.repositories.csv_pokedex_repository import CSVPokedexRepository
        
        # Infrastructure: Create Pokedex
        pokedex = CSVPokedexRepository(battle_format="gen1randombattle")
        
        # Domain: Create agent
        agent = Agent(agent_id="TestBot", elo=1000)
        
        # Infrastructure: Create neural network
        nn = TensorFlowNeuralNetwork()
        nn.initialize_random((38,), 5)
        
        # Infrastructure: Create battle strategy
        strategy = NeuralNetworkStrategy(neural_network=nn)
        
        # Verify everything is connected
        assert agent is not None
        assert strategy.nn is not None
        assert pokedex is not None
    
    def test_rating_service_with_agents(self):
        """Test rating service updates across battles"""
        from domain.services.rating_service import RatingService
        from domain.entities.agent import Agent
        
        rating_service = RatingService(k_value=50)
        
        agent1 = Agent(agent_id="Bot1", elo=1000)
        agent2 = Agent(agent_id="Bot2", elo=1000)
        
        # Simulate battles
        for i in range(5):
            winner = "a" if i % 2 == 0 else "b"
            new_r1, new_r2 = rating_service.calculate_ratings_after_battle(
                agent1.elo, agent2.elo, winner
            )
            agent1.elo = new_r1
            agent2.elo = new_r2
            
            if winner == "a":
                agent1.record_win()
                agent2.record_loss()
            else:
                agent2.record_win()
                agent1.record_loss()
        
        # Verify battles were recorded
        assert agent1.total_games == 5
        assert agent2.total_games == 5


class TestArchitecturePrinciples:
    """Verify hexagonal architecture principles"""
    
    def test_dependency_inversion(self):
        """Test that adapters depend on ports, not vice versa"""
        from abc import ABC
        from application.ports.neural_network import INeuralNetwork
        from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
        
        # Port should be abstract
        assert issubclass(INeuralNetwork, ABC)
        
        # Infrastructure should depend on port
        assert issubclass(TensorFlowNeuralNetwork, INeuralNetwork)
    
    def test_no_infrastructure_in_domain(self):
        """Verify domain doesn't import infrastructure"""
        import importlib
        
        # Import domain module
        domain_module = importlib.import_module('domain.entities.pokemon')
        
        # Check that it doesn't import tensorflow or poke_env
        module_globals = vars(domain_module)
        assert 'tensorflow' not in module_globals
        assert 'poke_env' not in module_globals
