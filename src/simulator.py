from .graph import MapGraph


class Simulator:

    def __init__(self, graph: MapGraph) -> None:
        """Create a simulator for a map graph."""
        self.graph = graph

    def route_drones(self, drone_count: int) -> list[list[str]]:
        """Route drones one at a time and return movements grouped by turn."""
        path = self.graph.find_path(
            self.graph.start_hub,
            self.graph.end_hub,
        )
        turns: list[list[str]] = []

        for drone_id in range(1, drone_count + 1):
            for zone_name in path[1:]:
                turns.append([f"D{drone_id}-{zone_name}"])

        return turns


if __name__ == "__main__":
    from pathlib import Path
    from .parser import MapParser

    print("Sequential Drone Simulation Test\n")
    parsed_map = MapParser().parse_file(
        Path("maps/easy/01_linear_path.txt")
    )
    graph = MapGraph(parsed_map)
    simulator = Simulator(graph)

    for turn_number, movements in enumerate(
        simulator.route_drones(parsed_map.nb_drones),
        start=1,
    ):
        print(f"Turn {turn_number}: {' '.join(movements)}")
