# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:26 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 13:19:43 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Main file."""

import sys

from src import Parsers, Renderer, Algorithm


class Main:
    """Main function."""

    def __init__(self) -> None:
        """Everything starts here."""
        self.path = ""
        self.visual = False
        self.check_args()

    def check_args(self):
        for arg in sys.argv[1:]:
            if arg == "--visual":
                self.visual = True
            elif self.path == "":
                self.path = arg
            else:
                print("[Error] Too much arguments")
                self.print_error()
                sys.exit(1)
        if self.path == "":
            print("[Error] No enough arguments")
            self.print_error()
            sys.exit(1)

    def run(self) -> None:
        """Run the entire program."""
        self.parsers = Parsers(self.path)
        self.network = self.parsers.read_line()
        self.algorithm = Algorithm(self.network)
        self.algorithm.run()
        # pprint(self.algorithm.drone_positions_per_turn)

        if self.visual:
            path = self.algorithm.get_path()
            self.renderer = Renderer(self.network, self.algorithm.h_value, path)
            self.renderer.run()
        # ModelPrinter().print_drone_network(self.network)

    @staticmethod
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


if __name__ == "__main__":
    main = Main()
    main.run()
