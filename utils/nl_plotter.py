"""Natural language plotting tool."""

from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
from loguru import logger

from visualization.plotter import GeologicalPlotter


class NaturalLanguagePlotter:
    """Create plots from natural language commands."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize NL plotter.

        Args:
            output_dir: Directory to save plots
        """
        self.plotter = GeologicalPlotter(output_dir=output_dir or Path("./output/plots"))
        self.output_dir = self.plotter.output_dir

    def plot_from_command(
        self,
        command: str,
        data_file: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create plot from natural language command.

        Args:
            command: Natural language command
            data_file: Path to data file
            data: Direct data dict

        Returns:
            Plot result
        """
        try:
            # Load data if file provided
            if data_file and not data:
                data = self._load_data(data_file)
                if not data:
                    return {
                        'success': False,
                        'error': f'Failed to load data from {data_file}'
                    }

            if not data:
                return {
                    'success': False,
                    'error': 'No data provided'
                }

            # Determine plot type from command
            plot_type = self._detect_plot_type(command, data)

            # Create appropriate plot
            if plot_type == 'velocity_profile':
                return self._plot_velocity_profile(data, command)
            elif plot_type == 'velocity_section':
                return self._plot_velocity_section(data, command)
            elif plot_type == 'gravity':
                return self._plot_gravity(data, command)
            elif plot_type == 'magnetic':
                return self._plot_magnetic(data, command)
            elif plot_type == 'scatter':
                return self._plot_scatter(data, command)
            elif plot_type == 'line':
                return self._plot_line(data, command)
            else:
                return {
                    'success': False,
                    'error': f'Unknown plot type for command: {command}'
                }

        except Exception as e:
            logger.error(f"Plotting failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _detect_plot_type(self, command: str, data: Dict[str, Any]) -> str:
        """Detect plot type from command and data.

        Args:
            command: User command
            data: Data dict

        Returns:
            Plot type string
        """
        command_lower = command.lower()

        # Check command keywords
        if '速度剖面' in command or 'velocity profile' in command_lower:
            return 'velocity_profile'
        elif '速度断面' in command or 'velocity section' in command_lower:
            return 'velocity_section'
        elif '重力' in command or 'gravity' in command_lower:
            return 'gravity'
        elif '磁' in command or 'magnetic' in command_lower:
            return 'magnetic'
        elif '散点' in command or 'scatter' in command_lower:
            return 'scatter'

        # Infer from data structure
        if 'depth' in data and 'velocity' in data:
            if 'x' in data or len(data['velocity'].shape) > 1:
                return 'velocity_section'
            else:
                return 'velocity_profile'
        elif 'gravity' in data or 'bouguer' in data:
            return 'gravity'
        elif 'magnetic' in data or 'mag' in data:
            return 'magnetic'
        else:
            return 'line'

    def _plot_velocity_profile(
        self,
        data: Dict[str, Any],
        command: str
    ) -> Dict[str, Any]:
        """Plot velocity profile.

        Args:
            data: Data with 'depth' and 'velocity'
            command: User command

        Returns:
            Plot result
        """
        depths = np.array(data.get('depth', data.get('z', [])))
        velocities = np.array(data.get('velocity', data.get('v', [])))

        if len(depths) == 0 or len(velocities) == 0:
            return {'success': False, 'error': 'Missing depth or velocity data'}

        # Extract title from command or use default
        title = self._extract_title(command, "Velocity Profile")

        plot_path = self.plotter.plot_velocity_profile(
            depths=depths,
            velocities=velocities,
            title=title
        )

        return {
            'success': True,
            'plot_path': str(plot_path),
            'plot_type': 'velocity_profile',
            'message': f'速度剖面图已保存到: {plot_path}'
        }

    def _plot_velocity_section(
        self,
        data: Dict[str, Any],
        command: str
    ) -> Dict[str, Any]:
        """Plot velocity section.

        Args:
            data: Data with x, depth, velocity
            command: User command

        Returns:
            Plot result
        """
        x = np.array(data.get('x', data.get('distance', [])))
        depths = np.array(data.get('depth', data.get('z', [])))
        velocities = np.array(data.get('velocity', data.get('v', [])))

        if velocities.ndim != 2:
            return {'success': False, 'error': 'Velocity must be 2D for section plot'}

        title = self._extract_title(command, "Velocity Section")

        plot_path = self.plotter.plot_velocity_section(
            x=x,
            depths=depths,
            velocities=velocities,
            title=title
        )

        return {
            'success': True,
            'plot_path': str(plot_path),
            'plot_type': 'velocity_section',
            'message': f'速度断面图已保存到: {plot_path}'
        }

    def _plot_gravity(
        self,
        data: Dict[str, Any],
        command: str
    ) -> Dict[str, Any]:
        """Plot gravity data.

        Args:
            data: Gravity data
            command: User command

        Returns:
            Plot result
        """
        x = np.array(data.get('x', data.get('distance', [])))
        gravity = np.array(data.get('gravity', data.get('bouguer', [])))

        if len(x) == 0 or len(gravity) == 0:
            return {'success': False, 'error': 'Missing gravity data'}

        # Simple line plot for gravity
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, gravity, 'b-', linewidth=2)
        ax.set_xlabel('Distance (km)', fontsize=12)
        ax.set_ylabel('Gravity Anomaly (mGal)', fontsize=12)
        ax.set_title(self._extract_title(command, "Gravity Anomaly"), fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plot_path = self.output_dir / "gravity_plot.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return {
            'success': True,
            'plot_path': str(plot_path),
            'plot_type': 'gravity',
            'message': f'重力异常图已保存到: {plot_path}'
        }

    def _plot_magnetic(
        self,
        data: Dict[str, Any],
        command: str
    ) -> Dict[str, Any]:
        """Plot magnetic data.

        Args:
            data: Magnetic data
            command: User command

        Returns:
            Plot result
        """
        x = np.array(data.get('x', data.get('distance', [])))
        magnetic = np.array(data.get('magnetic', data.get('mag', [])))

        if len(x) == 0 or len(magnetic) == 0:
            return {'success': False, 'error': 'Missing magnetic data'}

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, magnetic, 'r-', linewidth=2)
        ax.set_xlabel('Distance (km)', fontsize=12)
        ax.set_ylabel('Magnetic Anomaly (nT)', fontsize=12)
        ax.set_title(self._extract_title(command, "Magnetic Anomaly"), fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plot_path = self.output_dir / "magnetic_plot.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return {
            'success': True,
            'plot_path': str(plot_path),
            'plot_type': 'magnetic',
            'message': f'磁异常图已保存到: {plot_path}'
        }

    def _plot_scatter(
        self,
        data: Dict[str, Any],
        command: str
    ) -> Dict[str, Any]:
        """Plot scatter plot.

        Args:
            data: Data with x and y
            command: User command

        Returns:
            Plot result
        """
        x = np.array(data.get('x', []))
        y = np.array(data.get('y', []))

        if len(x) == 0 or len(y) == 0:
            return {'success': False, 'error': 'Missing x or y data'}

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x, y, alpha=0.6, s=50)
        ax.set_xlabel('X', fontsize=12)
        ax.set_ylabel('Y', fontsize=12)
        ax.set_title(self._extract_title(command, "Scatter Plot"), fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plot_path = self.output_dir / "scatter_plot.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return {
            'success': True,
            'plot_path': str(plot_path),
            'plot_type': 'scatter',
            'message': f'散点图已保存到: {plot_path}'
        }

    def _plot_line(
        self,
        data: Dict[str, Any],
        command: str
    ) -> Dict[str, Any]:
        """Plot line chart.

        Args:
            data: Data to plot
            command: User command

        Returns:
            Plot result
        """
        # Try to find numeric arrays
        numeric_data = {}
        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)):
                arr = np.array(value)
                if arr.ndim == 1 and np.issubdtype(arr.dtype, np.number):
                    numeric_data[key] = arr

        if not numeric_data:
            return {'success': False, 'error': 'No numeric data found'}

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 6))

        for key, values in numeric_data.items():
            x = np.arange(len(values))
            ax.plot(x, values, label=key, linewidth=2)

        ax.set_xlabel('Index', fontsize=12)
        ax.set_ylabel('Value', fontsize=12)
        ax.set_title(self._extract_title(command, "Line Plot"), fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plot_path = self.output_dir / "line_plot.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)

        return {
            'success': True,
            'plot_path': str(plot_path),
            'plot_type': 'line',
            'message': f'折线图已保存到: {plot_path}'
        }

    @staticmethod
    def _extract_title(command: str, default: str) -> str:
        """Extract plot title from command.

        Args:
            command: User command
            default: Default title

        Returns:
            Title string
        """
        # Look for title after "标题" or "title"
        import re
        match = re.search(r'(?:标题|title)[:：]\s*(.+?)(?:\s*$)', command)
        if match:
            return match.group(1).strip()
        return default

    @staticmethod
    def _load_data(file_path: str) -> Optional[Dict[str, Any]]:
        """Load data from file.

        Args:
            file_path: Path to data file

        Returns:
            Loaded data dict
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            if path.suffix == '.npy':
                data = np.load(path, allow_pickle=True)
                if isinstance(data, np.ndarray) and data.ndim == 0:
                    return data.item()
                return {'data': data}
            elif path.suffix == '.npz':
                data = np.load(path)
                return {key: data[key] for key in data.files}
            elif path.suffix == '.json':
                import json
                with open(path, 'r') as f:
                    return json.load(f)
            elif path.suffix in ['.csv', '.txt']:
                import pandas as pd
                df = pd.read_csv(path)
                return {col: df[col].values for col in df.columns}
            else:
                logger.warning(f"Unsupported file format: {path.suffix}")
                return None

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return None
