"""Visualization module for geological data and inversion results."""

from typing import Optional, List, Dict, Any, Tuple, Union
from pathlib import Path
import numpy as np
from loguru import logger

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not available. Plotting disabled.")


class GeologicalPlotter:
    """Plotter for geological data visualization."""

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """Initialize plotter.

        Args:
            output_dir: Directory to save plots
        """
        self.output_dir = Path(output_dir) if output_dir else Path("./output/plots")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib is required for plotting")

    def plot_velocity_profile(
        self,
        depths: np.ndarray,
        velocities: np.ndarray,
        title: str = "Velocity Profile",
        xlabel: str = "Velocity (km/s)",
        ylabel: str = "Depth (km)",
        save_path: Optional[Union[str, Path]] = None,
        show_layers: bool = True,
        layer_colors: Optional[List[str]] = None,
    ) -> Path:
        """Plot velocity vs depth profile.

        Args:
            depths: Depth values in km
            velocities: Velocity values in km/s
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            save_path: Path to save the plot
            show_layers: Whether to highlight different layers
            layer_colors: Colors for different layers

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(8, 10))

        # Plot velocity profile
        ax.plot(velocities, depths, 'b-', linewidth=2, label='Velocity')

        # Invert y-axis (depth increases downward)
        ax.invert_yaxis()

        # Add layer boundaries if requested
        if show_layers:
            self._add_layer_boundaries(ax, depths, velocities, layer_colors)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()

        save_path = save_path or self.output_dir / "velocity_profile.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"Velocity profile saved to: {save_path}")
        return Path(save_path)

    def plot_velocity_section(
        self,
        x: np.ndarray,
        depths: np.ndarray,
        velocities: np.ndarray,
        title: str = "Velocity Section",
        cmap: str = "jet",
        save_path: Optional[Union[str, Path]] = None,
        contour_levels: int = 20,
    ) -> Path:
        """Plot 2D velocity section.

        Args:
            x: Horizontal distance in km
            depths: Depth values in km
            velocities: 2D velocity array (x, depth)
            title: Plot title
            cmap: Colormap name
            save_path: Path to save the plot
            contour_levels: Number of contour levels

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Create meshgrid
        X, Z = np.meshgrid(x, depths)

        # Plot filled contours
        cf = ax.contourf(X, Z, velocities, levels=contour_levels, cmap=cmap)

        # Add contour lines
        cs = ax.contour(X, Z, velocities, levels=contour_levels // 2, colors='white', linewidths=0.5)
        ax.clabel(cs, inline=True, fontsize=8, fmt='%.2f')

        # Add colorbar
        cbar = plt.colorbar(cf, ax=ax)
        cbar.set_label('Velocity (km/s)', fontsize=12)

        ax.set_xlabel('Distance (km)', fontsize=12)
        ax.set_ylabel('Depth (km)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        plt.tight_layout()

        save_path = save_path or self.output_dir / "velocity_section.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"Velocity section saved to: {save_path}")
        return Path(save_path)

    def plot_inversion_result(
        self,
        observed_data: np.ndarray,
        predicted_data: np.ndarray,
        model: np.ndarray,
        title: str = "Inversion Results",
        save_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """Plot inversion results including data fit and model.

        Args:
            observed_data: Observed data
            predicted_data: Predicted data from inversion
            model: Inverted model parameters
            title: Plot title
            save_path: Path to save the plot

        Returns:
            Path to saved plot
        """
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))

        # Plot data fit
        ax1 = axes[0]
        ax1.plot(observed_data, 'ro', label='Observed', markersize=4, alpha=0.6)
        ax1.plot(predicted_data, 'b-', label='Predicted', linewidth=1.5)
        ax1.set_xlabel('Data Point', fontsize=11)
        ax1.set_ylabel('Value', fontsize=11)
        ax1.set_title('Data Fit', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Calculate misfit
        misfit = np.sqrt(np.mean((observed_data - predicted_data) ** 2))
        ax1.text(0.02, 0.98, f'RMS Misfit: {misfit:.4f}',
                transform=ax1.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Plot model
        ax2 = axes[1]
        ax2.plot(model, 'g-', linewidth=2)
        ax2.set_xlabel('Model Parameter Index', fontsize=11)
        ax2.set_ylabel('Model Value', fontsize=11)
        ax2.set_title('Inverted Model', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()

        save_path = save_path or self.output_dir / "inversion_result.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"Inversion result saved to: {save_path}")
        return Path(save_path)

    def plot_comparison(
        self,
        x: np.ndarray,
        datasets: List[Dict[str, Any]],
        title: str = "Comparison Plot",
        xlabel: str = "X",
        ylabel: str = "Y",
        save_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """Plot multiple datasets for comparison.

        Args:
            x: X-axis values
            datasets: List of dicts with 'data', 'label', 'style' keys
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            save_path: Path to save the plot

        Returns:
            Path to saved plot
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        for dataset in datasets:
            data = dataset['data']
            label = dataset.get('label', 'Unknown')
            style = dataset.get('style', '-')

            ax.plot(x, data, style, label=label, linewidth=2, alpha=0.8)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        save_path = save_path or self.output_dir / "comparison.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"Comparison plot saved to: {save_path}")
        return Path(save_path)

    def plot_residual_distribution(
        self,
        residuals: np.ndarray,
        title: str = "Residual Distribution",
        save_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """Plot distribution of residuals.

        Args:
            residuals: Residual values
            title: Plot title
            save_path: Path to save the plot

        Returns:
            Path to saved plot
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Histogram
        ax1 = axes[0]
        ax1.hist(residuals, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax1.set_xlabel('Residual', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Residual Histogram', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Add statistics
        mean_res = np.mean(residuals)
        std_res = np.std(residuals)
        stats_text = f'Mean: {mean_res:.4f}\nStd: {std_res:.4f}'
        ax1.text(0.98, 0.98, stats_text, transform=ax1.transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Q-Q plot (simple version)
        ax2 = axes[1]
        sorted_res = np.sort(residuals)
        theoretical = np.random.normal(mean_res, std_res, len(sorted_res))
        theoretical.sort()
        ax2.plot(theoretical, sorted_res, 'o', markersize=3, alpha=0.6)

        # Add 1:1 line
        min_val = min(theoretical.min(), sorted_res.min())
        max_val = max(theoretical.max(), sorted_res.max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)

        ax2.set_xlabel('Theoretical Quantiles', fontsize=11)
        ax2.set_ylabel('Sample Quantiles', fontsize=11)
        ax2.set_title('Q-Q Plot', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()

        save_path = save_path or self.output_dir / "residuals.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        logger.info(f"Residual distribution saved to: {save_path}")
        return Path(save_path)

    def _add_layer_boundaries(
        self,
        ax,
        depths: np.ndarray,
        velocities: np.ndarray,
        colors: Optional[List[str]] = None,
    ):
        """Add layer boundary annotations to plot.

        Args:
            ax: Matplotlib axis
            depths: Depth values
            velocities: Velocity values
            colors: Layer colors
        """
        # Simple layer detection based on velocity gradients
        velocity_gradient = np.gradient(velocities, depths)

        # Find significant changes (layer boundaries)
        threshold = np.percentile(np.abs(velocity_gradient), 90)
        boundaries = np.where(np.abs(velocity_gradient) > threshold)[0]

        if colors is None:
            colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']

        # Shade layers
        for i in range(len(boundaries) + 1):
            start = boundaries[i - 1] if i > 0 else 0
            end = boundaries[i] if i < len(boundaries) else len(depths) - 1

            color = colors[i % len(colors)]
            ax.axhspan(depths[start], depths[end], alpha=0.2, color=color)

            # Add boundary lines
            if i < len(boundaries):
                ax.axhline(y=depths[boundaries[i]], color='gray',
                          linestyle='--', linewidth=1, alpha=0.5)
