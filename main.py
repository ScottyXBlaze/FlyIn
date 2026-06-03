"""Main file."""

from src import Parsers, Renderer


class Main:
    """Main function."""

    def __init__(self) -> None:
        """Everything starts here."""
        self.parsers = Parsers("maps/challenger/01_the_impossible_dream.txt")
        # self.parsers = Parsers("maps/easy/01_linear_path.txt")
        # self.parsers = Parsers("maps/easy/02_simple_fork.txt")
        # self.parsers = Parsers("maps/easy/03_basic_capacity.txt")
        # self.parsers = Parsers("maps/hard/01_maze_nightmare.txt")
        # self.parsers = Parsers("maps/hard/02_capacity_hell.txt")
        # self.parsers = Parsers("maps/hard/03_ultimate_challenge.txt")
        # self.parsers = Parsers("maps/medium/01_dead_end_trap.txt")
        # self.parsers = Parsers("maps/medium/02_circular_loop.txt")
        # self.parsers = Parsers("maps/medium/03_priority_puzzle.txt")
        self.network = self.parsers.read_line()
        self.renderer = Renderer(self.network)

    def run(self) -> None:
        """Run the entire program."""
        self.renderer.run()


if __name__ == "__main__":
    main = Main()
    main.run()
