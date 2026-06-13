# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:26 by nyramana         #+#    #+#              #
#    Updated: 2026/06/13 11:55:40 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Main file."""

import sys

from pydantic import ValidationError

from src import Parsers, Algorithm, StateManager


def print_error() -> None:
    """Print an error and usage message."""
    print("""
==== Usage ====

[Using the python file]
uv run python3 main.py <mapfile>

[Using the Makefile]
make run MAP=<mapfile>
""")


class Main:
    """Main function."""

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
        try:
            self.parsers = Parsers(self.path)
            self.network = self.parsers.read_line()
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

        self.algorithm = Algorithm(self.network)

        # Check that the path is available
        if not self.algorithm.h_value.get(self.network.get_start_hub.name):
            print("[ERROR] Start position is not linked with end position.\n")
            sys.exit(1)

        self.algorithm.run()

        if self.visual:
            path = self.algorithm.get_path()
            self.renderer = StateManager(
                self.network, self.algorithm.h_value, path
            )
            self.renderer.run()


if __name__ == "__main__":
    main = Main()
    try:
        main.run()
    except KeyboardInterrupt:
        print("Process ended")
