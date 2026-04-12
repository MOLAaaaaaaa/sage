"""Base classes for inversion algorithms."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
from loguru import logger


class InversionAlgorithm(ABC):
    """Abstract base class for inversion algorithms."""

    def __init__(self, **kwargs):
        """Initialize inversion algorithm.

        Args:
            **kwargs: Algorithm parameters
        """
        self.params = kwargs
        self.result = None

    @abstractmethod
    def forward(self, model: np.ndarray) -> np.ndarray:
        """Forward modeling operator.

        Args:
            model: Model parameters

        Returns:
            Predicted data
        """
        pass

    @abstractmethod
    def invert(self, data: np.ndarray, initial_model: Optional[np.ndarray] = None) -> np.ndarray:
        """Perform inversion.

        Args:
            data: Observed data
            initial_model: Initial model guess

        Returns:
            Inverted model
        """
        pass

    def compute_misfit(self, observed: np.ndarray, predicted: np.ndarray) -> float:
        """Compute RMS misfit between observed and predicted data.

        Args:
            observed: Observed data
            predicted: Predicted data

        Returns:
            RMS misfit value
        """
        return np.sqrt(np.mean((observed - predicted) ** 2))

    def save_result(self, filepath: str):
        """Save inversion result to file.

        Args:
            filepath: Output file path
        """
        if self.result is None:
            raise ValueError("No result to save. Run inversion first.")

        np.savez(filepath, **self.result)
        logger.info(f"Result saved to: {filepath}")


class LinearInversion(InversionAlgorithm):
    """Linear least squares inversion."""

    def __init__(self, regularization_weight: float = 0.01, **kwargs):
        """Initialize linear inversion.

        Args:
            regularization_weight: Weight for Tikhonov regularization
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)
        self.reg_weight = regularization_weight
        self.G = None  # Sensitivity matrix

    def set_forward_operator(self, G: np.ndarray):
        """Set the forward operator (sensitivity matrix).

        Args:
            G: Sensitivity matrix (n_data x n_model)
        """
        self.G = G

    def forward(self, model: np.ndarray) -> np.ndarray:
        """Linear forward modeling: d = G * m.

        Args:
            model: Model parameters

        Returns:
            Predicted data
        """
        if self.G is None:
            raise ValueError("Forward operator G not set")
        return self.G @ model

    def invert(self, data: np.ndarray, initial_model: Optional[np.ndarray] = None) -> np.ndarray:
        """Solve linear inverse problem with regularization.

        Args:
            data: Observed data
            initial_model: Not used in linear inversion

        Returns:
            Inverted model
        """
        if self.G is None:
            raise ValueError("Forward operator G not set")

        n_model = self.G.shape[1]

        # Damped least squares: m = (G^T G + λI)^{-1} G^T d
        GtG = self.G.T @ self.G
        Gtd = self.G.T @ data

        # Add regularization
        A = GtG + self.reg_weight * np.eye(n_model)

        # Solve system
        model = np.linalg.solve(A, Gtd)

        # Compute predicted data and misfit
        predicted = self.forward(model)
        misfit = self.compute_misfit(data, predicted)

        self.result = {
            'model': model,
            'predicted_data': predicted,
            'misfit': misfit,
            'regularization_weight': self.reg_weight,
        }

        logger.info(f"Linear inversion completed. Misfit: {misfit:.4f}")
        return model


class IterativeInversion(InversionAlgorithm):
    """Iterative nonlinear inversion using gradient descent."""

    def __init__(
        self,
        max_iterations: int = 100,
        learning_rate: float = 0.01,
        tolerance: float = 1e-6,
        **kwargs
    ):
        """Initialize iterative inversion.

        Args:
            max_iterations: Maximum number of iterations
            learning_rate: Step size for gradient descent
            tolerance: Convergence tolerance
            **kwargs: Additional parameters
        """
        super().__init__(**kwargs)
        self.max_iter = max_iterations
        self.lr = learning_rate
        self.tol = tolerance

    @abstractmethod
    def compute_gradient(self, model: np.ndarray, data: np.ndarray) -> np.ndarray:
        """Compute gradient of objective function.

        Args:
            model: Current model
            data: Observed data

        Returns:
            Gradient vector
        """
        pass

    def invert(self, data: np.ndarray, initial_model: Optional[np.ndarray] = None) -> np.ndarray:
        """Perform iterative inversion.

        Args:
            data: Observed data
            initial_model: Initial model guess

        Returns:
            Inverted model
        """
        n_params = len(data) * 2  # Heuristic for model size
        model = initial_model if initial_model is not None else np.zeros(n_params)

        best_misfit = float('inf')

        for iteration in range(self.max_iter):
            # Forward modeling
            predicted = self.forward(model)

            # Compute misfit
            misfit = self.compute_misfit(data, predicted)

            # Check convergence
            if abs(best_misfit - misfit) < self.tol:
                logger.info(f"Converged at iteration {iteration}")
                break

            best_misfit = misfit

            # Compute gradient and update model
            gradient = self.compute_gradient(model, data)
            model = model - self.lr * gradient

            if iteration % 10 == 0:
                logger.debug(f"Iteration {iteration}: Misfit = {misfit:.6f}")

        # Final forward modeling
        predicted = self.forward(model)
        final_misfit = self.compute_misfit(data, predicted)

        self.result = {
            'model': model,
            'predicted_data': predicted,
            'misfit': final_misfit,
            'iterations': iteration + 1,
        }

        logger.info(f"Iterative inversion completed. Final misfit: {final_misfit:.4f}")
        return model
