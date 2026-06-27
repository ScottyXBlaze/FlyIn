# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:26 by nyramana         #+#    #+#              #
#    Updated: 2026/06/27 11:37:35 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""
Main Entry point for the program.

It contains the class that combine everything
from parsing and algorithm to rendering.
"""

import importlib
import os
import sys


def print_error() -> None:
    """Print an error and usage message."""
    print(
        """
==== Usage ====

[Using the python file]
uv run python3 main.py <mapfile>

[Using the Makefile]
make run MAP=<mapfile>"""
    )


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"


def check_dependencies() -> bool:
    """
    Check every depedencies to run the program.

    Returns:
        bool: True if every dependencies is installed.
    """
    dependencies = {
        "pygame",
        "pydantic",
    }
    missing = set()
    for dependency in dependencies:
        try:
            _ = importlib.import_module(dependency)
        except ImportError:
            missing.add(dependency)
    if missing:
        print(f"Missing dependency: {", ".join(missing)}")
        return False
    return True


if not check_dependencies():
    print_error()
    sys.exit(1)

from main_algorithm import Algorithm  # noqa: 402
from main_parsers import Parsers  # noqa: 402
from main_rendering import StateManager  # noqa: 402


class Main:
    """
    Main Entry class for the program.

    Every initialization starts here and
    the basic structure of the project.
    """

    def __init__(self) -> None:
        """Everything starts here."""
        self._path: str = ""
        self._visual: bool = False
        self.check_args()

    def check_args(self) -> None:
        """Check if the argument of the program is valid."""
        for arg in sys.argv[1:]:
            if arg == "--visual":
                self._visual = True
            elif self._path == "":
                self._path = arg
            else:
                print("[Error] Too much arguments")
                print_error()
                sys.exit(1)
        if self._path == "":
            print("[Error] No enough arguments")
            print_error()
            sys.exit(1)
        print()

    def run(self) -> None:
        """Run the entire program."""
        from pydantic import ValidationError

        try:
            parsers = Parsers(self._path)
            network = parsers.read_line()
        except ValidationError as e:
            for error in e.errors():
                print(f"[ERROR] {error['msg']}\n")
            sys.exit(1)
        except ValueError as e:
            print(f"[ERROR] {e}\n")
            sys.exit(1)
        except Exception as e:
            print(f"[Error] Unexpected {e}")
            sys.exit(1)

        algorithm = Algorithm(network)

        # Check that the path is available
        if not algorithm.h_value.get(network.get_start_hub.name):
            print("[ERROR] Start position is not linked with end position.\n")
            sys.exit(1)

        algorithm.run()

        if self._visual:
            path = algorithm.get_path()
            renderer = StateManager(network, algorithm.h_value, path)
            renderer.run()


if __name__ == "__main__":
    main = Main()
    try:
        main.run()
    except KeyboardInterrupt:
        print("Process ended")
