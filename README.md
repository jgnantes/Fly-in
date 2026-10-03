*This project has been created as part of the 42 curriculum by jnantes-.*

# Fly-in

This project simulates a drone fleet moving from a start hub to an end hub across a map made of zones and connections.

## Project structure

- `main.py`: CLI entry point.
- `src/parser.py`: reads the map files and validates metadata.
- `src/graph.py`: builds the graph and finds the cheapest path.
- `src/simulator.py`: schedules drone motion and restricted-zone transit.
- `maps/`: map files used for validation.

## Quick start

1. Create the virtual environment:
   `python3 -m venv .venv`
2. Install the dependencies:
   `. .venv/bin/activate && python -m pip install -r requirements.txt`
3. Run a map:
   `. .venv/bin/activate && python main.py maps/easy/01_linear_path.txt`

## Available commands

- `make venv`
- `make install`
- `make run ARGS="maps/medium/02_circular_loop.txt"`
- `make lint`

## Rules covered by the implementation

- zone parsing and metadata validation
- connection parsing with capacity metadata
- shortest-path search with weighted movement costs
- restricted-zone transit that requires two turns
- multi-drone scheduling with turn-based output

## Notes

The project is intentionally structured so that parser, graph logic, and simulation are separate, making it easier to add more advanced routing rules later.