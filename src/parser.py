from .models import Zone, Connection, ParsedMap
import pathlib as pl


class MapParser:

    @staticmethod
    def _parse_int(
        value: str,
        field: str,
        line_number: int,
        positive: bool = False,
    ) -> int:
        """Convert text to an integer and optionally require positivity."""
        value = value.strip()
        digits = value[1:] if value[:1] in {"+", "-"} else value
        if not digits or not digits.isascii() or not digits.isdecimal():
            raise ValueError(
                f"Line {line_number}: {field} must be an integer"
            )
        number = int(value)
        if positive and number <= 0:
            raise ValueError(
                f"Line {line_number}: {field} must be positive"
            )
        return number

    @staticmethod
    def _parse_metadata(
        value: str,
        line_number: int,
    ) -> tuple[str, dict[str, str]]:
        """Separate a declaration from its metadata."""
        definition, opening, remainder = value.partition("[")

        if not opening:
            if "]" in value:
                raise ValueError(f"Line {line_number}: invalid metadata")
            return definition.strip(), {}
        if (
            not remainder.endswith("]")
            or "[" in remainder
            or "]" in remainder[:-1]
        ):
            raise ValueError(f"Line {line_number}: invalid metadata")

        metadata: dict[str, str] = {}
        for item in remainder[:-1].split():
            key, separator, field_value = item.partition("=")
            if not separator or not key or not field_value:
                raise ValueError(
                    f"Line {line_number}: invalid metadata field '{item}'"
                )
            if key in metadata:
                raise ValueError(
                    f"Line {line_number}: duplicate metadata key '{key}'"
                )
            metadata[key] = field_value

        return definition.strip(), metadata

    @staticmethod
    def _parse_zone(role: str, value: str, line_number: int) -> Zone:
        """Convert a zone declaration into a Zone."""
        if role not in {"start_hub", "end_hub", "hub"}:
            raise ValueError(f"Line {line_number}: invalid zone role")

        definition, metadata = MapParser._parse_metadata(value, line_number)
        fields = definition.split()
        if len(fields) != 3:
            raise ValueError(
                f"Line {line_number}: expected a name and two coordinates"
            )

        name, x_text, y_text = fields
        if "-" in name:
            raise ValueError(
                f"Line {line_number}: zone names cannot contain '-'"
            )

        allowed_metadata = {"zone", "color", "max_drones"}
        for key in metadata:
            if key not in allowed_metadata:
                raise ValueError(
                    f"Line {line_number}: unsupported metadata key '{key}'"
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
            name=name,
            x=MapParser._parse_int(x_text, "x", line_number),
            y=MapParser._parse_int(y_text, "y", line_number),
            zone_type=zone_type,
            color=metadata.get("color"),
            max_drones=max_drones,
        )

    @staticmethod
    def _parse_connection(
        value: str,
        zones: dict[str, Zone],
        line_number: int,
    ) -> Connection:
        """Convert a connection declaration into a Connection."""
        definition, metadata = MapParser._parse_metadata(value, line_number)
        endpoints = definition.split("-")

        if len(endpoints) != 2:
            raise ValueError(
                f"Line {line_number}: connection needs two zone names"
            )

        first_zone, second_zone = endpoints
        if (
            not first_zone
            or not second_zone
            or any(char.isspace() for char in first_zone + second_zone)
        ):
            raise ValueError(
                f"Line {line_number}: invalid zone name in connection"
            )

        for name in (first_zone, second_zone):
            if name not in zones:
                raise ValueError(
                    f"Line {line_number}: undefined zone '{name}'"
                )

        for key in metadata:
            if key != "max_link_capacity":
                raise ValueError(
                    f"Line {line_number}: unsupported metadata key '{key}'"
                )

        capacity = MapParser._parse_int(
            metadata.get("max_link_capacity", "1"),
            "max_link_capacity",
            line_number,
            positive=True,
        )

        return Connection(first_zone, second_zone, capacity)

    def parse_file(self, path: pl.Path) -> ParsedMap:
        """Read a map file and build its parsed representation."""
        nb_drones: int | None = None
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        seen_connections: set[frozenset[str]] = set()
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
                    zone = self._parse_zone(key, value, line_number)
                    if zone.name in zones:
                        raise ValueError(
                            f"Line {line_number}: duplicate zone '{zone.name}'"
                        )
                    zones[zone.name] = zone

                    if key == "start_hub":
                        if start_hub is not None:
                            raise ValueError(
                                f"Line {line_number}: duplicate 'start_hub'"
                            )
                        start_hub = zone.name
                    elif key == "end_hub":
                        if end_hub is not None:
                            raise ValueError(
                                f"Line {line_number}: duplicate 'end_hub'"
                            )
                        end_hub = zone.name
                    continue

                if key == "connection":
                    connection = self._parse_connection(
                        value, zones, line_number
                    )
                    pair = frozenset(
                        (connection.first_zone, connection.second_zone)
                    )
                    if pair in seen_connections:
                        raise ValueError(
                            f"Line {line_number}: duplicate connection"
                        )
                    seen_connections.add(pair)
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


if __name__ == "__main__":
    print("1. Inteiro:")
    print(MapParser._parse_int("4", "nb_drones", 1, positive=True))

    print("\n2. Metadata:")
    definition, metadata = MapParser._parse_metadata(
        "junction 1 0 [color=yellow max_drones=2]",
        2,
    )
    print(definition)
    print(metadata)

    print("\n3. Zona:")
    start = MapParser._parse_zone("start_hub", "start 0 0", 3)
    junction = MapParser._parse_zone(
        "hub",
        "junction 1 0 [color=yellow max_drones=2]",
        4,
    )
    print(start)
    print(junction)

    print("\n4. Conexao:")
    connection = MapParser._parse_connection(
        "start-junction [max_link_capacity=2]",
        {"start": start, "junction": junction},
        5,
    )
    print(connection)

    print("\n5. Arquivo completo:")
    parsed_map = MapParser().parse_file(
        pl.Path("maps/easy/01_linear_path.txt")
    )
    print(parsed_map)
