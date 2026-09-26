from dataclasses import dataclass
import pathlib as pl


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


class MapParser:
    def parse_file(self, path: pl.Path) -> ParsedMap:
        nb_drones: int | None = None
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        connection_keys: set[frozenset[str]] = set()
        start_hub: str | None = None
        end_hub: str | None = None

        with path.open(encoding="utf-8") as map_file:
            for line_number, raw_line in enumerate(map_file, start=1):
                line = raw_line.partition("#")[0].strip()
                if not line:
                    continue

                key, separator, value = line.partition(":")
                if not separator:
                    raise ValueError(f"Line {line_number}: expected ':'")

                key = key.strip()
                value = value.strip()

                if nb_drones is None and key != "nb_drones":
                    raise ValueError(
                        f"Line {line_number}: 'nb_drones' must come first"
                    )

                if key == "nb_drones":
                    if nb_drones is not None:
                        raise ValueError(
                            f"Line {line_number}: duplicate 'nb_drones'"
                        )
                    nb_drones = self._parse_int(
                        value, "nb_drones", line_number, positive=True
                    )
                    continue

                if key in {"start_hub", "end_hub", "hub"}:
                    zone = self._parse_zone(value, key, line_number)
                    if zone.name in zones:
                        raise ValueError(
                            f"Line {line_number}: duplicate zone '{zone.name}'"
                        )
                    if key == "start_hub":
                        if start_hub is not None:
                            raise ValueError(
                                f"Line {line_number}: duplicate start_hub"
                            )
                        start_hub = zone.name
                    elif key == "end_hub":
                        if end_hub is not None:
                            raise ValueError(
                                f"Line {line_number}: duplicate end_hub"
                            )
                        end_hub = zone.name
                    zones[zone.name] = zone
                    continue

                if key == "connection":
                    connection = self._parse_connection(
                        value, zones, line_number
                    )
                    pair = frozenset(
                        (connection.first_zone, connection.second_zone)
                    )
                    if pair in connection_keys:
                        raise ValueError(
                            f"Line {line_number}: duplicate connection"
                        )
                    connection_keys.add(pair)
                    connections.append(connection)
                    continue

                raise ValueError(
                    f"Line {line_number}: unknown entry '{key}'"
                )

        if nb_drones is None:
            raise ValueError("Missing 'nb_drones'")
        if start_hub is None:
            raise ValueError("Missing 'start_hub'")
        if end_hub is None:
            raise ValueError("Missing 'end_hub'")

        return ParsedMap(nb_drones, zones, connections, start_hub, end_hub)

    @staticmethod
    def _parse_zone(value: str, role: str, line_number: int) -> Zone:
        definition, metadata = MapParser._parse_metadata(
            value, {"zone", "color", "max_drones"}, line_number
        )
        fields = definition.split()
        if len(fields) != 3:
            raise ValueError(
                f"Line {line_number}: zone needs a name and two coordinates"
            )

        name, x_text, y_text = fields
        if "-" in name:
            raise ValueError(
                f"Line {line_number}: zone names cannot contain '-'"
            )

        zone_type = metadata.get("zone", "normal")
        if zone_type not in {"normal", "blocked", "restricted", "priority"}:
            raise ValueError(
                f"Line {line_number}: invalid zone type '{zone_type}'"
            )

        max_drones = None
        if role == "hub":
            max_drones = MapParser._parse_int(
                metadata.get("max_drones", "1"),
                "max_drones",
                line_number,
                positive=True,
            )

        return Zone(
            name,
            MapParser._parse_int(x_text, "x", line_number),
            MapParser._parse_int(y_text, "y", line_number),
            zone_type,
            metadata.get("color"),
            max_drones,
        )

    @staticmethod
    def _parse_connection(
        value: str,
        zones: dict[str, Zone],
        line_number: int,
    ) -> Connection:
        definition, metadata = MapParser._parse_metadata(
            value, {"max_link_capacity"}, line_number
        )
        endpoints = definition.split("-")
        if len(endpoints) != 2 or any(not name for name in endpoints):
            raise ValueError(
                f"Line {line_number}: connection needs two zone names"
            )

        first_zone, second_zone = endpoints
        if any(any(char.isspace() for char in name) for name in endpoints):
            raise ValueError(
                f"Line {line_number}: invalid zone name in connection"
            )
        for name in endpoints:
            if name not in zones:
                raise ValueError(
                    f"Line {line_number}: undefined zone '{name}'"
                )

        capacity = MapParser._parse_int(
            metadata.get("max_link_capacity", "1"),
            "max_link_capacity",
            line_number,
            positive=True,
        )
        return Connection(first_zone, second_zone, capacity)

    @staticmethod
    def _parse_metadata(
        value: str,
        allowed_keys: set[str],
        line_number: int,
    ) -> tuple[str, dict[str, str]]:
        definition, opening, remainder = value.partition("[")
        if opening:
            if (
                not remainder.endswith("]")
                or "[" in remainder
                or "]" in remainder[:-1]
            ):
                raise ValueError(f"Line {line_number}: invalid metadata")
            items = remainder[:-1].split()
        else:
            if "]" in value:
                raise ValueError(f"Line {line_number}: invalid metadata")
            items = []

        metadata: dict[str, str] = {}
        for item in items:
            key, separator, field_value = item.partition("=")
            if not separator or not key or not field_value:
                raise ValueError(
                    f"Line {line_number}: invalid metadata field '{item}'"
                )
            if key not in allowed_keys or key in metadata:
                raise ValueError(
                    f"Line {line_number}: invalid metadata key '{key}'"
                )
            metadata[key] = field_value

        return definition.strip(), metadata

    @staticmethod
    def _parse_int(
        value: str,
        field: str,
        line_number: int,
        positive: bool = False,
    ) -> int:
        digits = value[1:] if value[:1] in {"+", "-"} else value
        if not digits or not digits.isascii() or not digits.isdecimal():
            raise ValueError(f"Line {line_number}: {field} must be an integer")

        number = int(value)
        if positive and number <= 0:
            raise ValueError(f"Line {line_number}: {field} must be positive")
        return number


if __name__ == "__main__":
    print("TEST")