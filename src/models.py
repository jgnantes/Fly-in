from dataclasses import dataclass


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str
    color: str | None
    max_drones: int | None


@dataclass
class Connection:
    first_zone: str
    second_zone: str
    max_link_capacity: int


@dataclass
class ParsedMap:
    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]
    start_hub: str
    end_hub: str


if __name__ == "__main__":
    from .parser import MapParser
    from pathlib import Path

    print("Data Types Test\n")
    zone1 = Zone("zone1", 0, 0, "normal", "blue", 2)
    zone2 = Zone("zone2", 6, 7, "abnormal", "pinky", 0)
    print(f"Zone 1: {zone1}")
    print(f"Zone 2: {zone2}\n")
    connection = Connection("zone1", "zone2", 2)
    print(f"Connection test: {connection}\n")
    parsed_map = MapParser().parse_file(
        Path("maps/easy/01_linear_path.txt")
    )
    print(f"Parsed Map: {parsed_map}")
