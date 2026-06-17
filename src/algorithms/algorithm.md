
# Algorithm documentation

## Overview

`Algorithm` is the main class that moves drones through a `DroneNetwork`.
It decides which hub to visit next, updates drone positions, tracks edge usage,
and stops when all drones reach the end or when no move is possible.

The class is designed around a greedy strategy:
- compute a heuristic from the end hub with `ReverseDijkstra`
- pick the best neighbor for each drone
- move drones turn by turn
- record positions for later rendering

## Main responsibilities

`Algorithm` handles four main tasks:

1. Create the drones.
2. Choose the next hub for each drone.
3. Move drones across hubs and connections.
4. Store the result of each turn.

## Class initialization

When `Algorithm` is created:

- the network is stored in `self.drone_network`
- heuristic values are computed once in `self.h_value`
- one `Drone` is created for each drone in the network
- empty containers are prepared for:
	- `drone_positions_per_turn`
	- `edge_usage`
	- `result`

This setup makes the run loop faster because the heuristic does not need to be recomputed every turn.

## `set_drones()`

This helper creates all drones at the start hub.

Behavior:

- drones are numbered from `1` to `nb_drones`
- every drone starts at the same initial position

This method is simple and only acts as a factory.

## `get_closest_neighbor()`

This method chooses the best next hub for a drone.

### How it works

For each neighbor of the current hub:

- compare its heuristic value with the current hub
- skip it if the heuristic is not better
- skip it if the connection is not available
- skip it if the hub itself is full or blocked
- compute a score for the candidate

### What influences the score

The candidate score uses:

- heuristic distance from the end
- edge usage
- hub load
- connection load
- zone priority

Lower values are preferred.

### Sorting rule

Candidates are sorted with `sorted()` and the first one is chosen.
The ordering is intentionally made so that priority hubs are favored before normal ones when both are valid.

### Important note

The function only considers neighbors that already have a better heuristic value than the current hub.
So even a priority hub will not be selected if its heuristic is not better than the current position.

## `get_hub_by_pos()`

This helper finds a hub from its `(x, y)` position.

It scans all hubs and returns the one whose position matches the requested coordinates.

### Notes

- simple to understand
- works well for small networks
- can be slower on large networks because it searches linearly

## `move_drone()`

This method performs the actual movement.

It has two modes:

### 1. Drone is leaving a hub

If the drone is not already in a connection:

- restricted hubs are handled with extra checks
- the connection is verified before moving
- the source hub loses one drone
- the destination hub gains one drone
- the drone may be marked as being inside a connection

### 2. Drone is finishing a connection

If the drone is already in a connection:

- the connection counter is decreased
- the drone leaves connection state
- the drone is moved to the target hub

### Returned value

The method returns:

- a move string used for printing
- the new visual position of the drone

## `run()`

This is the main simulation loop.

### Turn flow

Each turn has two phases:

1. Move drones that are already inside a connection.
2. Start new moves for idle drones.

### What is stored

During the run, the algorithm stores:

- printed move strings
- positions for each turn
- edge usage counts

### Stop conditions

The simulation stops when:

- all drones have reached the end
- or no drone can move anymore

## `get_path()`

This method returns the recorded positions for every turn.

The result is a list of dictionaries:

- key: drone id
- value: drone position at that turn

## Useful behavior to know

- The algorithm is greedy, not global-optimal.
- It prefers shorter heuristic paths first.
- Priority zones can influence the tie-breaking order.
- Movement and capacity tracking are updated during the simulation.

## Limitations and points to watch

- repeated hub lookup by position can be slow on large networks
- divisions by capacity values assume the capacities are valid
- `get_path()` returns internal recorded data directly
- the movement logic should be kept consistent with hub and connection capacity rules

## Summary

`Algorithm` is the core runtime controller of the project.
It combines heuristic guidance, load balancing, and turn-based simulation to move drones from the start hub to the end hub in a predictable way.
