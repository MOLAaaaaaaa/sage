"""File system operations tool."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from loguru import logger


class FileSystemTool:
    """Tool for file system operations."""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize file system tool.

        Args:
            base_dir: Base directory for operations (default: current dir)
        """
        self.base_dir = base_dir or Path.cwd()

    def list_files(
        self,
        directory: str = '.',
        pattern: str = '*',
        recursive: bool = False,
        max_results: int = 50,
    ) -> Dict[str, Any]:
        """List files in directory.

        Args:
            directory: Directory to list
            pattern: File pattern (glob)
            recursive: Whether to search recursively
            max_results: Maximum number of results

        Returns:
            File listing result
        """
        try:
            # Resolve path
            if Path(directory).is_absolute():
                target_dir = Path(directory)
            else:
                target_dir = self.base_dir / directory

            if not target_dir.exists():
                return {
                    'success': False,
                    'error': f'Directory not found: {target_dir}',
                    'files': []
                }

            if not target_dir.is_dir():
                return {
                    'success': False,
                    'error': f'Not a directory: {target_dir}',
                    'files': []
                }

            # List files
            if recursive:
                files = list(target_dir.rglob(pattern))
            else:
                files = list(target_dir.glob(pattern))

            # Filter to files only
            files = [f for f in files if f.is_file()]

            # Limit results
            truncated = len(files) > max_results
            files = files[:max_results]

            # Build file info
            file_list = []
            for f in files:
                stat = f.stat()
                file_list.append({
                    'name': f.name,
                    'path': str(f.relative_to(self.base_dir)),
                    'size': self._format_size(stat.st_size),
                    'modified': self._format_time(stat.st_mtime),
                    'type': f.suffix or 'no extension'
                })

            result = {
                'success': True,
                'directory': str(target_dir),
                'pattern': pattern,
                'total_files': len(file_list),
                'truncated': truncated,
                'files': file_list
            }

            logger.info(f"Listed {len(file_list)} files in {target_dir}")
            return result

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return {
                'success': False,
                'error': str(e),
                'files': []
            }

    def read_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed file information.

        Args:
            file_path: Path to file

        Returns:
            File information
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return {'success': False, 'error': 'File not found'}

            stat = path.stat()
            return {
                'success': True,
                'name': path.name,
                'path': str(path),
                'size': self._format_size(stat.st_size),
                'size_bytes': stat.st_size,
                'created': self._format_time(stat.st_ctime),
                'modified': self._format_time(stat.st_mtime),
                'type': path.suffix or 'no extension',
                'is_file': path.is_file(),
                'is_dir': path.is_dir()
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def _format_time(timestamp: float) -> str:
        """Format timestamp.

        Args:
            timestamp: Unix timestamp

        Returns:
            Formatted time string
        """
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
