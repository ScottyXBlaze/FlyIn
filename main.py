# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:26 by nyramana         #+#    #+#              #
#    Updated: 2026/06/15 18:40:46 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Main file."""

import importlib

import sys


def print_error() -> None:
    """Print an error and usage message."""
    print(
        """
==== Usage ====

[Using the python file]
uv run python3 main.py <mapfile>

[Using the Makefile]
make run MAP=<mapfile>
"""
    )


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
    for dependency in dependencies:
        try:
            importlib.import_module(dependency)
        except ImportError:
            print("Hello", dependency)
            return False
    return True


if not check_dependencies():
    print("[Error] Missing dependencies")
    print_error()
    sys.exit(1)
from src import Parsers, Algorithm, StateManager  # noqa: E402


class Main:
    """Main Class."""

    def __init__(self) -> None:
        """Everything starts here."""
        self.path = ""
        self.visual = False
        self.check_args()

    def check_args(self) -> None:
        """Check the argument of the program."""
        for arg in sys.argv[1:]:
            if arg == "--visual":
                self.visual = True
            elif self.path == "":
                self.path = arg
            else:
                print("[Error] Too much arguments")
                print_error()
                sys.exit(1)
        if self.path == "":
            print("[Error] No enough arguments")
            print_error()
            sys.exit(1)
        print()

    def run(self) -> None:
        """Run the entire program."""
        from pydantic import ValidationError

        try:
            parsers = Parsers(self.path)
            network = parsers.read_line()
        except ValidationError as e:
            for error in e.errors():
                print(
                    f"[ERROR] {error['msg']} {error['loc']}{error['input']}\n"
                )
            sys.exit(1)
        except ValueError as e:
            print(f"[ERROR] {e}\n")
            sys.exit(1)
        except Exception as e:
            print(f"[Error] Unexpected {e}")
            sys.exit(1)

        self.algorithm = Algorithm(network)

        # Check that the path is available
        if not self.algorithm.h_value.get(network.get_start_hub.name):
            print("[ERROR] Start position is not linked with end position.\n")
            sys.exit(1)

        self.algorithm.run()

        if self.visual:
            path = self.algorithm.get_path()
            self.renderer = StateManager(network, self.algorithm.h_value, path)
            self.renderer.run()


if __name__ == "__main__":

    if not check_dependencies():
        print("[Error] Missing dependencies")

    main = Main()
    try:
        main.run()
    except KeyboardInterrupt:
        print("Process ended")
