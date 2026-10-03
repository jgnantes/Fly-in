from pathlib import Path

from src.graph import MapGraph
from src.parser import MapParser
from src.simulator import Simulator


def test_parser_reads_easy_map() -> None:
    parsed_map = MapParser().parse_file(Path("maps/easy/01_linear_path.txt"))

    assert parsed_map.nb_drones == 2
    assert parsed_map.start_hub == "start"
    assert parsed_map.end_hub == "goal"
    assert {"start", "waypoint1", "waypoint2", "goal"}.issubset(
        parsed_map.zones
    )
    assert len(parsed_map.connections) == 3


def test_graph_prefers_priority_route() -> None:
    parsed_map = MapParser().parse_file(
        Path("maps/medium/03_priority_puzzle.txt")
    )
    graph = MapGraph(parsed_map)

    assert graph.find_path(parsed_map.start_hub, parsed_map.end_hub) == [
        "start",
        "fast_junction",
        "fast_path",
        "merge_point",
        "goal",
    ]


def test_simulator_routes_restricted_transit() -> None:
    parsed_map = MapParser().parse_file(
        Path("maps/medium/02_circular_loop.txt")
    )
    simulator = Simulator(MapGraph(parsed_map), 1)

    assert simulator.route_drones() == [
        ["D1-loop_a"],
        ["D1-loop_b"],
        ["D1-loop_b-exit_point"],
        ["D1-exit_point"],
        ["D1-goal"],
    ]
