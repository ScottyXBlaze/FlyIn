# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    main.py                                           :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: nyramana <nyramana@student.42antananariv  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/07 19:53:26 by nyramana         #+#    #+#              #
#    Updated: 2026/06/07 19:54:04 by nyramana        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

"""Main file."""

from src import Parsers, Renderer, Algorithm


class Main:
    """Main function."""

    def __init__(self) -> None:
        """Everything starts here."""
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
        self.parsers = Parsers(self.maps_list[10])
        self.network = self.parsers.read_line()
        self.algorithm = Algorithm(self.network)
        self.renderer = Renderer(self.network, self.algorithm.heuristic_value)

    def run(self) -> None:
        """Run the entire program."""
        self.renderer.run()


if __name__ == "__main__":
    main = Main()
    main.run()
