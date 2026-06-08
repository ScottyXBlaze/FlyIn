# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    validation.py                                     :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:54:01 by nyramana         #+#    #+#              #
#    Updated: 2026/06/07 20:10:53 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

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
