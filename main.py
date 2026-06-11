# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:26 by nyramana         #+#    #+#              #
#    Updated: 2026/06/11 12:00:00 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Main file."""

from pprint import pprint
import sys

from src import Parsers, Renderer, Algorithm


class Main:
    """Main function."""

    def __init__(self) -> None:
        """Everything starts here."""
        if len(sys.argv) != 2:
            self.print_error()
            sys.exit(1)

    def run(self) -> None:
        """Run the entire program."""
        self.parsers = Parsers(sys.argv[1])
        self.network = self.parsers.read_line()
        self.algorithm = Algorithm(self.network)
        self.algorithm.run()
        # pprint(self.algorithm.drone_positions_per_turn)

        self.renderer = Renderer(self.network, self.algorithm.h_value)
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
