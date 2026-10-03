from .models import Zone, Connection, Drone
from .graph import MapGraph


class Simulator:
    def __init__(self, graph: MapGraph, drone_count: int) -> None:
        """Create the fleet at the map's start zone."""
        self.graph = graph
        self.drones = [
            Drone(drone_id, graph.start_hub)
            for drone_id in range(1, drone_count + 1)
        ]

    def route_drones(self) -> list[list[str]]:
        """Route drones along one path while spacing restricted transits."""
        path = self.graph.find_path(
            self.graph.start_hub,
            self.graph.end_hub,
        )
        has_restricted_zone = any(
            self.graph.zones[zone_name].zone_type == "restricted"
            for zone_name in path[1:]
        )
        launch_interval = 2 if has_restricted_zone else 1
        turns: list[list[str]] = []

        for drone in self.drones:
            drone.current_zone = self.graph.start_hub
            drone.in_transit_to = None
            turn_index = (drone.id - 1) * launch_interval

            for zone_name in path[1:]:
                destination = self.graph.zones[zone_name]
                while len(turns) <= turn_index:
                    turns.append([])
                if destination.zone_type == "restricted":
                    connection = next(
                        link
                        for neighbor, link in self.graph.get_neighbors(
                            drone.current_zone
                        )
                        if neighbor.name == zone_name
                    )
                    turns[turn_index].append(
                        self._start_transit(drone, destination, connection)
                    )
                    turn_index += 1

                    while len(turns) <= turn_index:
                        turns.append([])

                    turns[turn_index].append(
                        self._complete_transit(drone)
                    )
                else:
                    turns[turn_index].append(
                        f"D{drone.id}-{zone_name}"
                    )
                    drone.current_zone = zone_name
                turn_index += 1
        return turns

    def _complete_transit(self, drone: Drone) -> str:
        """Move an in-transit drone into its destination zone."""
        destination = drone.in_transit_to
        if destination is None:
            raise ValueError(f"Drone {drone.id} is not in transit")

        drone.current_zone = destination
        drone.in_transit_to = None
        return f"D{drone.id}-{destination}"

    def _start_transit(
        self,
        drone: Drone,
        destination: Zone,
        connection: Connection,
    ) -> str:
        """Start a drone's transit to a restricted zone."""
        if drone.in_transit_to is not None:
            raise ValueError(f"Drone {drone.id} is already in transit")
        if destination.zone_type != "restricted":
            raise ValueError("Transit is only used for restricted zones")

        connection_endpoints = {
            connection.first_zone,
            connection.second_zone,
        }
        expected_endpoints = {drone.current_zone, destination.name}
        if connection_endpoints != expected_endpoints:
            raise ValueError(
                "Connection does not link the drone and destination"
            )

        drone.in_transit_to = destination.name
        return (
            f"D{drone.id}-"
            f"{drone.current_zone}-{destination.name}"
        )


if __name__ == "__main__":
    from pathlib import Path
    from .parser import MapParser

    print("Sequential Drone Simulation Test")
    parsed_map = MapParser().parse_file(
        Path("maps/easy/01_linear_path.txt")
    )
    graph = MapGraph(parsed_map)
    simulator = Simulator(graph, parsed_map.nb_drones)
    for turn_number, movements in enumerate(
        simulator.route_drones(),
        start=1,
    ):
        print(f"Turn {turn_number}: {' '.join(movements)}")
    print("\nFinal Drone Positions")
    for drone in simulator.drones:
        print(f"Drone {drone.id}: {drone.current_zone}")

    print("\nRestricted Transit Completion Test")
    restricted_map = MapParser().parse_file(
        Path("maps/medium/03_priority_puzzle.txt")
    )
    restricted_simulator = Simulator(
        MapGraph(restricted_map),
        restricted_map.nb_drones,
    )
    drone = Drone(99, "slow_path1", "slow_path2")
    print(f"Arrival movement: {restricted_simulator._complete_transit(drone)}")
    print(f"Drone after arrival: {drone}")

    print("\nRestricted Route Test")
    restricted_map = MapParser().parse_file(
        Path("maps/medium/02_circular_loop.txt")
    )
    restricted_graph = MapGraph(restricted_map)
    restricted_simulator = Simulator(restricted_graph, 1)
    for turn_number, movements in enumerate(
        restricted_simulator.route_drones(),
        start=1,
    ):
        print(f"Turn {turn_number}: {' '.join(movements)}")
