# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:26 by nyramana         #+#    #+#              #
#    Updated: 2026/06/10 11:23:52 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Main file."""

import sys

from src import Parsers, Renderer, Algorithm


class Main:
    """Main function."""

    def __init__(self) -> None:
        """Everything starts here."""
        if len(sys.argv) != 2:
            self.print_error()
            sys.exit(1)

        self.maps_list = [
            "maps/challenger/01_the_impossible_dream.txt",
            "maps/easy/01_linear_path.txt",
            "maps/easy/02_simple_fork.txt",
            "maps/easy/03_basic_capacity.txt",
            "maps/medium/01_dead_end_trap.txt",
            "maps/hard/01_maze_nightmare.txt",
            "maps/hard/02_capacity_hell.txt",
            "maps/hard/03_ultimate_challenge.txt",
            "maps/medium/02_circular_loop.txt",
            "maps/medium/03_priority_puzzle.txt",
            "maps/test/01_blocked_hub.txt",
        ]

    def run(self) -> None:
        """Run the entire program."""
        self.parsers = Parsers(sys.argv[1])
        self.network = self.parsers.read_line()
        self.algorithm = Algorithm(self.network)
        self.renderer = Renderer(self.network, self.algorithm.h_value)

        self.renderer.run()
        self.algorithm.run()

    @staticmethod
    def print_error() -> None:

        print("""
==== Usage ====

[Using the python file]
uv run python3 main.py <mapfile>

[Using the Makefile]
make run MAP=<mapfile>
""")


if __name__ == "__main__":
    main = Main()
    main.run()
