import importlib


class Validation:
    """
    Validation function.
    Returns:
        None
    """

    @staticmethod
    def check_dependencies(dependencies: set[str]) -> bool:
        """
        check function.
        Args:
            dependencies (set[str]): Check Dependencies dynamicaly to .
        Returns:
            bool: Description of return value.
        """
        for dependency in dependencies:
            try:
                _ = importlib.import_module(dependency)
            except ImportError:
                return False
        return True
