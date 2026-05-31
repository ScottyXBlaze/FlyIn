from src import Parsers, Hub, DroneNetwork, Metadata, ModelPrinter, Renderer


class Main:
    def __init__(self) -> None:
        self.parsers = Parsers("maps/easy/02_simple_fork.txt")
        self.network = self.parsers.read_line()
        self.renderer = Renderer(self.network)

    def run(self) -> None:
        self.renderer.run()


if __name__ == "__main__":
    main = Main()
    main.run()
