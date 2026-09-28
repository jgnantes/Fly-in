import sys
from argparse import ArgumentParser
from pathlib import Path

from src.graph import MapGraph
from src.parser import MapParser
from src.simulator import Simulator


def main() -> None:
    """Run the drone simulation for the selected map."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument("map_file", type=Path)
    args = arg_parser.parse_args()

    try:
        parsed_map = MapParser().parse_file(args.map_file)
        graph = MapGraph(parsed_map)
        simulator = Simulator(graph, parsed_map.nb_drones)

        for movements in simulator.route_drones():
            print(" ".join(movements))
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()