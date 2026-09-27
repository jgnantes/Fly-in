from .models import Connection, Zone
from .parser import ParsedMap
from collections import deque


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

    def find_path(self, start_zone: str, end_zone: str) -> list[str]:
        """Find a shortest path that avoids blocked zones."""
        if start_zone not in self.zones:
            raise ValueError("Start zone does not exist")
        if end_zone not in self.zones:
            raise ValueError("End zone does not exist")

        queue: deque[str] = deque([start_zone])
        previous: dict[str, str | None] = {start_zone: None}

        while queue:
            current_zone = queue.popleft()
            if current_zone == end_zone:
                break

            for neighbor, _ in self.get_neighbors(current_zone):
                if (
                    neighbor.zone_type == "blocked"
                    or neighbor.name in previous
                ):
                    continue
                previous[neighbor.name] = current_zone
                queue.append(neighbor.name)

        if end_zone not in previous:
            raise ValueError("No path exists between the zones")

        path: list[str] = []
        current_zone: str | None = end_zone
        while current_zone is not None:
            path.append(current_zone)
            current_zone = previous[current_zone]

        path.reverse()
        return path


if __name__ == "__main__":
    from pathlib import Path
    from .parser import MapParser

    print("Neighbor test")
    graph = MapGraph(MapParser().parse_file(
        Path("maps/easy/01_linear_path.txt")
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
        Path("maps/easy/01_linear_path.txt")
    )
    graph = MapGraph(parsed_map)
    path = graph.find_path(parsed_map.start_hub, parsed_map.end_hub)

    print(f"Shortest path: {' -> '.join(path)}")
