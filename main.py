import sys
from argparse import ArgumentParser
from pathlib import Path

from src.graph import MapGraph
from src.parser import MapParser
from src.simulator import Simulator


ANSI_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "yellow": "\033[33m",
    "orange": "\033[38;5;208m",
    "cyan": "\033[36m",
    "purple": "\033[35m",
    "magenta": "\033[35m",
    "white": "\033[37m",
    "black": "\033[30m",
}
RESET = "\033[0m"


def colorize_move(move: str, graph: MapGraph) -> str:
    """Color a movement text using the destination zone color."""
    target_name = move.split("-", 2)[-1]
    color = graph.zones.get(target_name)
    if color is None or color.color is None:
        return move

    ansi_color = ANSI_COLORS.get(color.color.lower())
    if ansi_color is None:
        return move
    return f"{ansi_color}{move}{RESET}"


def main() -> None:
    """Run the drone simulation for the selected map."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument("map_file", type=Path)
    args = arg_parser.parse_args()

    try:
        parsed_map = MapParser().parse_file(args.map_file)
        graph = MapGraph(parsed_map)
        simulator = Simulator(graph, parsed_map.nb_drones)

        for turn_number, movements in enumerate(
            simulator.route_drones(),
            start=1,
        ):
            rendered = [
                colorize_move(movement, graph)
                for movement in movements
            ]
            prefix = "Turn " + str(turn_number) + " ->"
            print(f"{prefix} {' '.join(rendered)}")
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
