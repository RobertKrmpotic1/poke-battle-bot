"""
JSON Agent Repository - persists agents to JSON files.
Infrastructure layer: implements IAgentRepository using file system.
"""
import json
import os
import numpy as np
from typing import List, Optional, Dict
from domain.repositories.agent_repository import IAgentRepository
from domain.entities.agent import Agent
from application.ports.neural_network import INeuralNetwork
from loguru import logger


class JsonAgentRepository(IAgentRepository):
    """
    JSON file-based implementation of agent repository.
    Saves agents with their neural networks to JSON files.
    """

    def __init__(self, base_path: str = "agents"):
        """
        Initialize repository.

        Args:
            base_path: Base directory for storing agent files
        """
        self.base_path = base_path
        self.hall_of_fame_path = os.path.join(base_path, "hall_of_fame")

        # Create directories if they don't exist
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.hall_of_fame_path, exist_ok=True)

    def _get_agent_filepath(self, agent_id: str) -> str:
        """Get filepath for agent JSON file."""
        return os.path.join(self.base_path, f"{agent_id}.json")

    def _get_hall_of_fame_filepath(self, generation: int) -> str:
        """Get filepath for hall of fame JSON file."""
        return os.path.join(self.hall_of_fame_path, f"gen_{generation}.json")

    def save_agent(self, agent: Agent) -> None:
        """
        Save an agent to JSON file.

        Args:
            agent: Agent to save
        """
        filepath = self._get_agent_filepath(agent.agent_id)

        # Serialize agent data
        agent_data = {
            "agent_id": agent.agent_id,
            "battle_format": agent.battle_format,
            "elo": agent.elo,
            "wins": agent.wins,
            "losses": agent.losses,
            "draws": agent.draws,
            "total_battles": agent.battles,
            "generation": agent.generation,
            "neural_network": None
        }

        # Note: Neural networks are stored in strategies, not agents
        # For persistence, we'd need to save strategies separately
        agent_data["neural_network"] = None

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(agent_data, f, indent=2)

        logger.debug(f"Saved agent {agent.agent_id} to {filepath}")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Load an agent from JSON file.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent or None if not found
        """
        filepath = self._get_agent_filepath(agent_id)

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r') as f:
                agent_data = json.load(f)

            # Create agent
            agent = Agent(
                agent_id=agent_data["agent_id"],
                battle_format=agent_data["battle_format"],
                elo=agent_data["elo"]
            )

            # Restore battle stats
            agent.wins = agent_data.get("wins", 0)
            agent.losses = agent_data.get("losses", 0)
            agent.draws = agent_data.get("draws", 0)
            agent.battles = agent_data.get("total_battles", 0)
            agent.generation = agent_data.get("generation", 0)

            # Note: Neural networks are stored in strategies, not loaded here
            # Strategies would need to be recreated separately

            logger.debug(f"Loaded agent {agent_id} from {filepath}")
            return agent

        except Exception as e:
            logger.error(f"Failed to load agent {agent_id}: {e}")
            return None

    def get_all_agents(self) -> List[Agent]:
        """
        Get all agents from JSON files.

        Returns:
            List of all agents
        """
        agents = []

        if not os.path.exists(self.base_path):
            return agents

        for filename in os.listdir(self.base_path):
            if filename.endswith('.json') and not filename.startswith('hall_of_fame'):
                agent_id = filename[:-5]  # Remove .json extension
                agent = self.get_agent(agent_id)
                if agent:
                    agents.append(agent)

        logger.info(f"Loaded {len(agents)} agents from {self.base_path}")
        return agents

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent JSON file.

        Args:
            agent_id: Agent identifier

        Returns:
            True if deleted, False if not found
        """
        filepath = self._get_agent_filepath(agent_id)

        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Deleted agent {agent_id}")
            return True

        return False

    def update_agent(self, agent: Agent) -> None:
        """
        Update an existing agent (same as save).

        Args:
            agent: Agent with updated data
        """
        self.save_agent(agent)

    def save_hall_of_fame(
        self,
        generation: int,
        agent: Agent,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Save a hall of fame winner.

        Args:
            generation: Generation/round number
            agent: Winning agent
            metadata: Additional metadata to save
        """
        filepath = self._get_hall_of_fame_filepath(generation)

        hof_data = {
            "generation": generation,
            "agent": {
                "agent_id": agent.agent_id,
                "battle_format": agent.battle_format,
                "elo": agent.elo,
                "wins": agent.wins,
                "losses": agent.losses,
                "total_battles": agent.battles
            },
            "metadata": metadata or {}
        }

        # Note: Neural network architecture info not saved in HOF for now

        with open(filepath, 'w') as f:
            json.dump(hof_data, f, indent=2)

        logger.info(f"Saved hall of fame for generation {generation}: {agent.agent_id} (ELO: {agent.elo})")

    def get_hall_of_fame(self, generation: int) -> Optional[Agent]:
        """
        Get hall of fame winner for a generation.

        Args:
            generation: Generation number

        Returns:
            Agent or None if not found
        """
        filepath = self._get_hall_of_fame_filepath(generation)

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r') as f:
                hof_data = json.load(f)

            agent_data = hof_data["agent"]
            agent = Agent(
                agent_id=agent_data["agent_id"],
                battle_format=agent_data["battle_format"],
                elo=agent_data["elo"]
            )

            # Restore battle stats
            agent.wins = agent_data.get("wins", 0)
            agent.losses = agent_data.get("losses", 0)
            agent.draws = 0  # Not stored in HOF
            agent.battles = agent_data.get("total_battles", 0)

            logger.debug(f"Loaded hall of fame agent for generation {generation}")
            return agent

        except Exception as e:
            logger.error(f"Failed to load hall of fame for generation {generation}: {e}")
            return None

    def agent_exists(self, agent_id: str) -> bool:
        """
        Check if agent exists.

        Args:
            agent_id: Agent identifier

        Returns:
            True if exists
        """
        filepath = self._get_agent_filepath(agent_id)
        return os.path.exists(filepath)

    def _deserialize_neural_network(self, nn_data: Dict) -> INeuralNetwork:
        """
        Deserialize neural network from saved data.

        Args:
            nn_data: Neural network data from JSON

        Returns:
            Neural network instance
        """
        from infrastructure.adapters.tensorflow_nn_adapter import TensorFlowNeuralNetwork

        nn = TensorFlowNeuralNetwork()

        # Set weights
        weights = [np.array(w) for w in nn_data["weights"]]
        nn.set_weights(weights)

        # Set architecture info (manually set since we loaded weights)
        arch = nn_data["architecture"]
        nn._input_shape = tuple(arch["input_shape"]) if arch["input_shape"] else None
        nn._output_shape = arch["output_shape"]

        return nn