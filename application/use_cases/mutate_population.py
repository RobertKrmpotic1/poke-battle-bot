"""
Mutate Population Use Case - applies genetic evolution to agent population.
Application layer: coordinates population evolution with neural network mutations.
"""
from typing import List, Dict, Any
from application.ports.neural_network import INeuralNetwork
from domain.entities.agent import Agent
from domain.services.tournament_service import TournamentService
from loguru import logger


class MutatePopulation:
    """
    Use case for evolving agent population through genetic algorithms.
    Creates new generation by mutating neural networks of top performers.
    """

    def __init__(
        self,
        neural_network_factory: callable,  # Factory function to create new NN instances
        tournament_service: TournamentService
    ):
        """
        Initialize use case with dependencies.

        Args:
            neural_network_factory: Function that returns new INeuralNetwork instances
            tournament_service: Domain service for agent selection
        """
        self.neural_network_factory = neural_network_factory
        self.tournament_service = tournament_service

    def execute(
        self,
        agents: List[Agent],
        population_size: int,
        elite_count: int = 2,
        mutation_rate: float = 0.05,
        mutation_strength: float = 0.1
    ) -> Dict[str, Any]:
        """
        Evolve population to next generation.

        Args:
            agents: Current population of agents
            population_size: Target population size for next generation
            elite_count: Number of top agents to keep unchanged
            mutation_rate: Fraction of weights to mutate
            mutation_strength: How much to mutate each weight

        Returns:
            Evolution results with new population and statistics
        """
        logger.info(f"Evolving population of {len(agents)} agents to {population_size}")

        # Select elite agents (top performers)
        elite_agents = self.tournament_service.select_top_agents(agents, elite_count)
        logger.info(f"Selected {len(elite_agents)} elite agents: {[a.agent_id for a in elite_agents]}")

        # Create new population starting with elites
        new_population = elite_agents.copy()

        # Calculate how many offspring to create
        offspring_needed = population_size - len(elite_agents)

        # Create offspring by mutating elites
        offspring_created = 0
        generation = 1

        while offspring_created < offspring_needed:
            # Cycle through elite agents as parents
            parent = elite_agents[offspring_created % len(elite_agents)]

            # Create offspring by copying and mutating
            offspring = self._create_offspring(parent, generation, offspring_created + 1)
            new_population.append(offspring)
            offspring_created += 1

        # Trim to exact population size if needed
        if len(new_population) > population_size:
            new_population = new_population[:population_size]

        # Reset agent statistics for new generation (except ELO)
        for agent in new_population:
            agent.reset_battle_stats()

        evolution_stats = {
            "original_population": len(agents),
            "new_population": len(new_population),
            "elite_count": len(elite_agents),
            "offspring_created": offspring_created,
            "mutation_rate": mutation_rate,
            "mutation_strength": mutation_strength,
            "top_elo_before": max(a.elo for a in agents) if agents else 0,
            "top_elo_after": max(a.elo for a in new_population) if new_population else 0,
            "avg_elo_before": sum(a.elo for a in agents) / len(agents) if agents else 0,
            "avg_elo_after": sum(a.elo for a in new_population) / len(new_population) if new_population else 0
        }

        logger.info(f"Evolution complete: {len(new_population)} agents, top ELO: {evolution_stats['top_elo_after']}")

        return {
            "new_population": new_population,
            "evolution_stats": evolution_stats
        }

    def _create_offspring(self, parent: Agent, generation: int, offspring_number: int) -> Agent:
        """
        Create offspring agent by copying parent and creating new strategy.

        Args:
            parent: Parent agent to base offspring on
            generation: Current generation number
            offspring_number: Sequential number for this offspring

        Returns:
            New agent with fresh neural network strategy
        """
        # Create new agent ID
        offspring_id = f"Gen{generation}_{offspring_number}"

        # Create new agent with inherited ELO but reset stats
        offspring = Agent(
            agent_id=offspring_id,
            battle_format=parent.battle_format,
            elo=parent.elo  # Inherit parent's ELO
        )

        # Note: Neural network strategy will be created separately by the container
        # The mutation happens at the strategy level, not agent level

        logger.debug(f"Created offspring {offspring_id} from {parent.agent_id}")

        return offspring