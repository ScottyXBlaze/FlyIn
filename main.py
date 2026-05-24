from src import Parsers, Hub, DroneNetwork, Metadata, ModelPrinter


class Main:
    def __init__(self) -> None:
        self.parsers = Parsers("maps/challenger/01_the_impossible_dream.txt")
        self.network = self.parsers.read_line()

    def run(self) -> None:
        ModelPrinter().print_drone_network(self.network)


if __name__ == "__main__":
    main = Main()
    main.run()
