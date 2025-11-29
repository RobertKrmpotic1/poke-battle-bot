"""
TensorFlow neural network adapter.
Implements INeuralNetwork port using TensorFlow.
Extracted from neural_network.py with port interface.
"""
import tensorflow as tf
import numpy as np
import random
from typing import List, Tuple, Optional
from application.ports.neural_network import INeuralNetwork


class TensorFlowNeuralNetwork(INeuralNetwork):
    """
    TensorFlow implementation of neural network port.
    Adapter that wraps TensorFlow and implements domain interface.
    """
    
    def __init__(self):
        """Initialize TensorFlow neural network."""
        self.model: Optional[tf.keras.Model] = None
        self._input_shape: Optional[Tuple[int, ...]] = None
        self._output_shape: Optional[int] = None

    def initialize_random(self, input_shape: Tuple[int, ...], output_shape: int) -> None:
        """
        Initialize network with random weights.
        
        Args:
            input_shape: Shape of input (e.g., (38,))
            output_shape: Number of outputs (e.g., 5)
        """
        self._input_shape = input_shape
        self._output_shape = output_shape
        
        self.model = tf.keras.models.Sequential([
            tf.keras.layers.InputLayer(input_shape=input_shape),
            tf.keras.layers.Dense(10, activation='relu'),
            tf.keras.layers.Dense(output_shape)
        ])

    def predict(self, inputs: np.ndarray) -> np.ndarray:
        """
        Make predictions from inputs.
        
        Args:
            inputs: Input array
            
        Returns:
            Output predictions
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize_random first.")
        
        # Ensure input has batch dimension
        if len(inputs.shape) == 1:
            inputs = inputs.reshape(1, -1)
        
        predictions = self.model.predict(inputs, verbose=0)
        return predictions[0] if len(predictions) == 1 else predictions

    def predict_batch(self, inputs: List[np.ndarray]) -> List[np.ndarray]:
        """
        Make predictions for multiple inputs.
        
        Args:
            inputs: List of input arrays
            
        Returns:
            List of output predictions
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize_random first.")
        
        batch = np.array(inputs)
        predictions = self.model.predict(batch, verbose=0)
        return [p for p in predictions]

    def mutate(self, mutation_rate: float = 0.05) -> None:
        """
        Mutate network weights (genetic algorithm).
        Scrambles a random subset of weights.
        
        Args:
            mutation_rate: Fraction of weights to mutate
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize_random first.")
        
        weights = self.model.get_weights()
        
        # Flatten and concatenate all weights into a single array
        flat_weights = np.concatenate([w.flatten() for w in weights])
        
        total_len = len(flat_weights)
        n_mutate = int(total_len * mutation_rate)
        
        if n_mutate == 0:
            return

        # Indices to mutate
        indices = random.sample(range(total_len), n_mutate)

        # Scramble selected values
        values_to_scramble = flat_weights[indices].copy()
        np.random.shuffle(values_to_scramble)
        flat_weights[indices] = values_to_scramble

        # Re-split into original weight shapes
        new_weights = []
        idx = 0
        for w in weights:
            size = w.size
            reshaped = flat_weights[idx:idx + size].reshape(w.shape)
            new_weights.append(reshaped)
            idx += size

        # Set mutated weights back
        self.model.set_weights(new_weights)

    def copy(self) -> 'TensorFlowNeuralNetwork':
        """
        Create a deep copy of this network.
        
        Returns:
            New network instance with same weights
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize_random first.")
        
        new_nn = TensorFlowNeuralNetwork()
        new_nn.initialize_random(self._input_shape, self._output_shape)
        new_nn.set_weights(self.get_weights())
        return new_nn

    def get_weights(self) -> List[np.ndarray]:
        """
        Get network weights.
        
        Returns:
            List of weight arrays
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize_random first.")
        
        return self.model.get_weights()

    def set_weights(self, weights: List[np.ndarray]) -> None:
        """
        Set network weights.
        
        Args:
            weights: List of weight arrays
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize_random first.")
        
        self.model.set_weights(weights)

    def save(self, filepath: str) -> None:
        """
        Save network to file.
        
        Args:
            filepath: Path to save to
        """
        if self.model is None:
            raise RuntimeError("Model not initialized. Call initialize_random first.")
        
        self.model.save(filepath)

    def load(self, filepath: str) -> None:
        """
        Load network from file.
        
        Args:
            filepath: Path to load from
        """
        self.model = tf.keras.models.load_model(filepath)
        
        # Extract shape information
        self._input_shape = tuple(self.model.input_shape[1:])
        self._output_shape = self.model.output_shape[-1]

    def get_architecture_info(self) -> dict:
        """
        Get information about network architecture.
        
        Returns:
            Dictionary with architecture details
        """
        if self.model is None:
            return {
                "initialized": False,
                "input_shape": None,
                "output_shape": None,
                "layers": 0
            }
        
        return {
            "initialized": True,
            "input_shape": self._input_shape,
            "output_shape": self._output_shape,
            "layers": len(self.model.layers),
            "total_params": self.model.count_params(),
            "layer_details": [
                {
                    "name": layer.name,
                    "type": layer.__class__.__name__,
                    "params": layer.count_params()
                }
                for layer in self.model.layers
            ]
        }
