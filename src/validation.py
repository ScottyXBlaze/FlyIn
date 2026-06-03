"""Module that contain a validation utilities."""

import importlib


class Validation:
    """Validation function."""

    @staticmethod
    def check_dependencies(dependencies: set[str]) -> bool:
        """
        Check if everything in the parameter is installed.

        Args:
            dependencies (set[str]): Dependency list.
        Returns:
            bool: True if everything is installed.
        """
        for dependency in dependencies:
            try:
                _ = importlib.import_module(dependency)
            except ImportError:
                return False
        return True
