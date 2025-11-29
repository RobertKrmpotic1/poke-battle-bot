"""
Dependency Injection Container - wires all application dependencies.
Infrastructure layer: creates and configures all adapters and services.
"""
from typing import Optional
from application.ports.battle_executor import IBattleExecutor
from application.ports.neural_network import INeuralNetwork
from application.use_cases.execute_battle import ExecuteBattle
from application.use_cases.run_league_round import RunLeagueRound
from application.use_cases.mutate_population import MutatePopulation
from application.use_cases.generate_team import GenerateTeam
from application.use_cases.benchmark_agent import BenchmarkAgent
from infrastructure.repositories.pandas_league_repository import PandasLeagueRepository
from domain.services.rating_service import RatingService
from domain.services.tournament_service import TournamentService
from domain.entities.agent import Agent
from infrastructure.adapters.poke_env_battle_adapter import PokeEnvBattleAdapter
from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork
from infrastructure.repositories.csv_pokedex_repository import CSVPokedexRepository
from infrastructure.repositories.json_agent_repository import JsonAgentRepository


class Container:
    """
    Dependency injection container.
    Creates and wires all application dependencies.
    """

    def __init__(
        self,
        server_url: str = "localhost:8000",
        agents_path: str = "agents",
        elo_k_value: int = 50
    ):
        """
        Initialize container with configuration.

        Args:
            server_url: Pokemon Showdown server URL
            agents_path: Path for agent persistence
            elo_k_value: K-factor for ELO calculations
        """
        # Configuration
        self.server_url = server_url
        self.agents_path = agents_path
        self.elo_k_value = elo_k_value

        # Infrastructure layer
        self._battle_executor: Optional[IBattleExecutor] = None
        self._pokedex_repository = None
        self._agent_repository = None

        # Domain services
        self._rating_service = None
        self._tournament_service = None

        # Application use cases
        self._execute_battle = None
        self._run_league_round = None
        self._mutate_population = None

    # Infrastructure Layer - Adapters & Repositories

    @property
    def battle_executor(self) -> IBattleExecutor:
        """Get battle executor adapter."""
        if self._battle_executor is None:
            self._battle_executor = PokeEnvBattleAdapter(self.server_url)
        return self._battle_executor

    @property
    def pokedex_repository(self):
        """Get pokedex repository."""
        if self._pokedex_repository is None:
            self._pokedex_repository = CSVPokedexRepository()
        return self._pokedex_repository

    @property
    def agent_repository(self):
        """Get agent repository."""
        if self._agent_repository is None:
            self._agent_repository = JsonAgentRepository(self.agents_path)
        return self._agent_repository

    # Domain Services

    @property
    def rating_service(self) -> RatingService:
        """Get rating service."""
        if self._rating_service is None:
            self._rating_service = RatingService(k_value=self.elo_k_value)
        return self._rating_service

    @property
    def tournament_service(self) -> TournamentService:
        """Get tournament service."""
        if self._tournament_service is None:
            self._tournament_service = TournamentService()
        return self._tournament_service

    # Application Use Cases

    @property
    def execute_battle(self) -> ExecuteBattle:
        """Get execute battle use case."""
        if self._execute_battle is None:
            self._execute_battle = ExecuteBattle(
                battle_executor=self.battle_executor,
                rating_service=self.rating_service
            )
        return self._execute_battle

    @property
    def run_league_round(self) -> RunLeagueRound:
        """Get run league round use case."""
        if self._run_league_round is None:
            self._run_league_round = RunLeagueRound(
                battle_executor=self.battle_executor,
                execute_battle=self.execute_battle,
                tournament_service=self.tournament_service
            )
        return self._run_league_round

    @property
    def mutate_population(self) -> MutatePopulation:
        """Get mutate population use case."""
        if self._mutate_population is None:
            self._mutate_population = MutatePopulation(
                neural_network_factory=self._create_neural_network,
                tournament_service=self.tournament_service
            )
        return self._mutate_population

    @property
    def generate_team(self) -> GenerateTeam:
        """Get generate team use case."""
        if not hasattr(self, '_generate_team'):
            self._generate_team = GenerateTeam(
                pokedex_repository=self.pokedex_repository,
                mutation_service=self.mutation_service
            )
        return self._generate_team

    @property
    def benchmark_agent(self) -> BenchmarkAgent:
        """Get benchmark agent use case."""
        if not hasattr(self, '_benchmark_agent'):
            self._benchmark_agent = BenchmarkAgent(
                battle_executor=self.battle_executor,
                execute_battle=self.execute_battle,
                rating_service=self.rating_service
            )
        return self._benchmark_agent

    @property
    def league_repository(self):
        """Get league repository."""
        if not hasattr(self, '_league_repository'):
            self._league_repository = PandasLeagueRepository()
        return self._league_repository

    # Factory Methods

    def _create_neural_network(self) -> INeuralNetwork:
        """Factory method for creating neural network instances."""
        nn = TensorFlowNeuralNetwork()
        nn.initialize_random(input_shape=(38,), output_shape=5)
        return nn

    def create_agent_with_random_nn(self, agent_id: str, battle_format: str = "gen1randombattle") -> Agent:
        """
        Create a new agent with random neural network.

        Args:
            agent_id: Unique agent identifier
            battle_format: Battle format

        Returns:
            New agent with random neural network
        """
        agent = Agent(agent_id=agent_id, battle_format=battle_format)
        return agent

    def create_strategy_for_agent(self, agent: Agent) -> 'NeuralNetworkStrategy':
        """
        Create a neural network strategy for an agent.

        Args:
            agent: Agent to create strategy for

        Returns:
            Neural network strategy
        """
        from infrastructure.adapters.nn_battle_strategy import NeuralNetworkStrategy

        nn = self._create_neural_network()
        strategy = NeuralNetworkStrategy(nn)
        return strategy

    def create_population(self, size: int, prefix: str = "Agent") -> list:
        """
        Create a population of agents with random neural networks.

        Args:
            size: Population size
            prefix: Agent ID prefix

        Returns:
            List of agents
        """
        return [
            self.create_agent_with_random_nn(f"{prefix}{i+1}")
            for i in range(size)
        ]

    # Utility Methods

    def save_population(self, agents: list, generation: Optional[int] = None) -> None:
        """
        Save population to repository.

        Args:
            agents: List of agents to save
            generation: Optional generation number for hall of fame
        """
        for agent in agents:
            self.agent_repository.save_agent(agent)

        # Save hall of fame if generation specified
        if generation is not None and agents:
            top_agent = self.tournament_service.select_top_agents(agents, 1)[0]
            self.agent_repository.save_hall_of_fame(
                generation=generation,
                agent=top_agent,
                metadata={"population_size": len(agents)}
            )

    def load_population(self) -> list:
        """
        Load population from repository.

        Returns:
            List of loaded agents
        """
        return self.agent_repository.get_all_agents()

    def get_population_stats(self, agents: list) -> dict:
        """
        Get statistics about a population.

        Args:
            agents: List of agents

        Returns:
            Statistics dictionary
        """
        if not agents:
            return {}

        elos = [a.elo for a in agents]
        wins = [a.n_won_battles for a in agents]
        total_battles = [a.n_finished_battles for a in agents]

        return {
            "count": len(agents),
            "avg_elo": sum(elos) / len(elos),
            "max_elo": max(elos),
            "min_elo": min(elos),
            "total_wins": sum(wins),
            "total_battles": sum(total_battles),
            "avg_win_rate": sum(wins) / sum(total_battles) if sum(total_battles) > 0 else 0
        }