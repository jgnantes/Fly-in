from .models import Connection, Zone
from .parser import ParsedMap
from heapq import heappop, heappush


class MapGraph:

    def __init__(self, parsed_map: ParsedMap) -> None:
        """Build bidirectional adjacency from parsed connections."""
        self.zones = parsed_map.zones
        self.start_hub = parsed_map.start_hub
        self.end_hub = parsed_map.end_hub
        self.adjacency: dict[str, list[Connection]] = {
            name: [] for name in self.zones
        }
        for connection in parsed_map.connections:
            self.adjacency[connection.first_zone].append(connection)
            self.adjacency[connection.second_zone].append(connection)

    def get_neighbors(
        self,
        zone_name: str,
    ) -> list[tuple[Zone, Connection]]:
        """Return adjacent zones and their connecting links."""
        if zone_name not in self.adjacency:
            raise ValueError(f"Unknown zone '{zone_name}'")

        neighbors = []
        for connection in self.adjacency[zone_name]:
            if connection.first_zone == zone_name:
                neighbor_name = connection.second_zone
            else:
                neighbor_name = connection.first_zone

            neighbors.append((self.zones[neighbor_name], connection))

        return neighbors

    @staticmethod
    def movement_cost(zone: Zone) -> int | None:
        """Return the turns required to enter a zone."""
        if zone.zone_type == "blocked":
            return None
        if zone.zone_type == "restricted":
            return 2
        return 1

    def find_path(self, start_zone: str, end_zone: str) -> list[str]:
        """Find a path with the lowest zone-entry cost."""
        if start_zone not in self.zones:
            raise ValueError("Start zone does not exist")
        if end_zone not in self.zones:
            raise ValueError("End zone does not exist")

        distances = {start_zone: 0}
        previous: dict[str, str | None] = {start_zone: None}
        queue: list[tuple[int, str]] = [(0, start_zone)]

        while queue:
            current_cost, current_zone = heappop(queue)

            if current_cost != distances[current_zone]:
                continue
            if current_zone == end_zone:
                break

            for neighbor, _ in self.get_neighbors(current_zone):
                move_cost = self.movement_cost(neighbor)
                if move_cost is None:
                    continue

                new_cost = current_cost + move_cost
                known_cost = distances.get(neighbor.name)
                if known_cost is None or new_cost < known_cost:
                    distances[neighbor.name] = new_cost
                    previous[neighbor.name] = current_zone
                    heappush(queue, (new_cost, neighbor.name))

        if end_zone not in previous:
            raise ValueError("No path exists between the zones")

        path: list[str] = []
        current_zone_name: str | None = end_zone
        while current_zone_name is not None:
            path.append(current_zone_name)
            current_zone_name = previous[current_zone_name]

        path.reverse()
        return path


if __name__ == "__main__":
    from pathlib import Path
    from .parser import MapParser

    print("Neighbor test")
    graph = MapGraph(MapParser().parse_file(
        Path("maps/medium/03_priority_puzzle.txt")
        )
    )
    for neighbor, connection in graph.get_neighbors("start"):
        print(
            f"Neighbor: {neighbor.name}; "
            f"link capacity: {connection.max_link_capacity}"
        )
    print()

    print("Path Test")
    parsed_map = MapParser().parse_file(
        Path("maps/medium/03_priority_puzzle.txt")
    )
    graph = MapGraph(parsed_map)
    path = graph.find_path(parsed_map.start_hub, parsed_map.end_hub)
    print(f"Shortest path: {' -> '.join(path)}\n")

    print("Zone Movement Costs Test")
    parsed_map = MapParser().parse_file(
        Path("maps/medium/03_priority_puzzle.txt")
    )
    for zone in parsed_map.zones.values():
        print(f"{zone.name}: {MapGraph.movement_cost(zone)}")
