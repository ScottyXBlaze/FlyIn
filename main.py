from src import Parsers, Hub, DroneNetwork, Metadata, ModelPrinter, Renderer


class Main:
    def __init__(self) -> None:
        self.parsers = Parsers("maps/challenger/01_the_impossible_dream.txt")
        self.network = self.parsers.read_line()
        self.renderer = Renderer(self.network)

    def run(self) -> None:
        self.renderer.run()


if __name__ == "__main__":
    main = Main()
    main.run()
