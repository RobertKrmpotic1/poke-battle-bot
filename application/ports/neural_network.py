"""
Neural network port - interface for ML models.
This abstracts away TensorFlow/PyTorch implementations.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np


class INeuralNetwork(ABC):
    """
    Port interface for neural network implementations.
    Infrastructure layer implements this using TensorFlow, PyTorch, etc.
    """
    
    @abstractmethod
    def initialize_random(self, input_shape: Tuple[int, ...], output_shape: int) -> None:
        """
        Initialize network with random weights.
        
        Args:
            input_shape: Shape of input (e.g., (38,) for battle state)
            output_shape: Number of outputs (e.g., 5 for move decisions)
        """
        pass

    @abstractmethod
    def predict(self, inputs: np.ndarray) -> np.ndarray:
        """
        Make predictions from inputs.
        
        Args:
            inputs: Input array
            
        Returns:
            Output predictions
        """
        pass

    @abstractmethod
    def predict_batch(self, inputs: List[np.ndarray]) -> List[np.ndarray]:
        """
        Make predictions for multiple inputs.
        
        Args:
            inputs: List of input arrays
            
        Returns:
            List of output predictions
        """
        pass

    @abstractmethod
    def mutate(self, mutation_rate: float = 0.05) -> None:
        """
        Mutate network weights (genetic algorithm).
        
        Args:
            mutation_rate: Fraction of weights to mutate
        """
        pass

    @abstractmethod
    def copy(self) -> 'INeuralNetwork':
        """
        Create a deep copy of this network.
        
        Returns:
            New network instance with same weights
        """
        pass

    @abstractmethod
    def get_weights(self) -> List[np.ndarray]:
        """
        Get network weights.
        
        Returns:
            List of weight arrays
        """
        pass

    @abstractmethod
    def set_weights(self, weights: List[np.ndarray]) -> None:
        """
        Set network weights.
        
        Args:
            weights: List of weight arrays
        """
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """
        Save network to file.
        
        Args:
            filepath: Path to save to
        """
        pass

    @abstractmethod
    def load(self, filepath: str) -> None:
        """
        Load network from file.
        
        Args:
            filepath: Path to load from
        """
        pass

    @abstractmethod
    def get_architecture_info(self) -> dict:
        """
        Get information about network architecture.
        
        Returns:
            Dictionary with architecture details
        """
        pass
