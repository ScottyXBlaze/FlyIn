*This project has been created as part of the 42 curriculum by nyramana.* 

# FlyIn

> Finishing is not the most important thing.

# Description:

**FLyIn** is a 42 project that consist of guiding drone from a start zone to a end zone with a lot of limitation for connection, capacity and much more.

## Goal:

The goal of this project is to learn Multi Agent Path Finding or known as MAPF and how we can handle multiple agent in a given map and manipulate them in the most stable and efficient way.

## Brief Overview:

The Map consist of 3 different entity:

- Drone: Entity that we manipulate
- Hub: Zone that can store drone (can have max_capacity and zonetype of priority, normal, blocked and restricted)
- Connection: Zone that serve to move across hub (Can have max_capacity)

Each drone as an ID (D1, D2, ...) and to move them, we just tell where they would like to go each turn (D1-paris). And if we need to go in a connection, we write the two hub that contain the connection (D1-paris-madagascar).

Each turn is one line in the output, and if we want to move multiple drone, we separate each drone instruction with a line.

### Example:

nb_drone: 2


```Bash
       x
      / \
HUB: a   c
      \ /
       b

D1-x D2-b
D1-c D2-c
```


# Instructions:

## Makefile instruction:

To install all the depedency:

```bash
make install
```

To run the program:

```bash
make run MAP=<mapfile>
```

To run the program with visual:

```bash
make run_visual MAP=<mapfile>
```

> [!IMPORTANT]
> Make sure to add the MAP=<mapfile> because we need a map to run the program.

To debug the program:

```bash
make debug MAP=<mapfile>
```

To clean cache and temporary file

```bash
make clean
```

To check basic linting

```bash
make lint
```

To check linting in a strict way

```bash
make lint-strict
```

## Manual Instruction:

> [!TIP]
> We used UV here because it is faster and easier than the traditional way of using pip

To install the dependency:

```bash
uv sync
```

To run the program:

```bash
uv run main.py <mapfile>
```

To run the program with visual:

```bash
uv run main.py <mapfile> --visual
```

## Program usage for visual:

Check below.

## Example:

Create a file and insert these configuration in it:

```bash
# This initialize the number of drones
# Should be at the top
nb_drones: 5

# This is where every drone starts
# Expected syntax:
# start_hub: name x y [metadata]
# start_hub: name x y [metadata]
start_hub: start 0 0

# This is where every drone should end
# Expected syntax:
# end_hub: name x y [metadata]
end_hub: end 4 0

# You can add other hub
# Expected syntax:
# hub: name x y [metadata]
hub: hub1 1 0 [zone=restricted max_drones=2]
hub: hub2 2 0 [max_drones=3]
hub: hub3 3 0 [color=blue]

# To link the hub, we use connection:
# Expected syntax:
# connection: <hubname>-<hubname> [metadata]
connection: start-hub1 [max_link_capacity=2]
connection: hub1-hub2
connection: hub2-hub3
connection: hub3-end
```

Then run `make run MAP=<mapfile>`

The output should be like this:

```bash

D1-start-hub1 D2-start-hub1
D1-hub1 D2-hub1
D1-hub2 D2-hub2 D3-start-hub1 D4-start-hub1
D3-hub1 D4-hub1 D1-hub3
D1-end D2-hub3 D3-hub2 D4-hub2 D5-start-hub1
D5-hub1 D2-end D3-hub3
D3-end D4-hub3 D5-hub2
D4-end D5-hub3
D5-end

Total Turn: 9

```

D<ID>-hubname means Drone with ID <ID> moved to the hub `hubname`
D<ID>-hubname1-hubname2 means Drone with ID <ID> moved to the `connection`` between the two hubname.
Drone that does not show in the output means two things, he doesn't want to move or he arrived in the end.

# Ressources:

- Peer learning
- [MAPF wikidedia](hhps://en.widipedia.org/wiki/Multi-agent_pathfinding)
- [Prioritized Planning](https://www.youtube.com/watch?v=9XIPCn4CzOA)
- [A star Algorithm](hhps://en.widipedia.org/wiki/A*_search_algorithm)

## AI usage:

AI was mainly used to help with debugging specific problem like the rendering or the parsing part, It also help me verify why my approach is wrong and what to improve for the algorithm.

# Extras:

## Algorithm choice:

I used a two main implementation with this project.

First, to check the estimated turn to go to the end, I used the reverse dijkstra method, It is a variant of the dijkstra method.

### Behavior

**dijkstra** is a popular algorithm for finding the fastest path from one position to another one. It work especially with weighted graph where each zone or hub have different cost and the least amount of cost from the start to end is the fastest one.

*Example:* 
```bash
   x(2) - y(1)
   /    |    \  
a(1) -  b(5) - c(2)
```

- Here with the dijkstra algorithm, the shortest path from a to c is a - x - y - c because a(1) + x(2) + y(1) + c(2) = 6 is less than a(1) - b(5) - c(2) = 8.

The reverse dijkstra is almost the same, but instead of finding the shortest path from one source to all other nodes, **Reverse dijkstra** find the shortest path from all node to all direction. 

*Example:*
```bash
   x(2) - y(1)
   /    |    \  
a(1) -  b(5) - c(2)
```

 - We have the destination C, To do the reverse dijkstra, we calculate the cost of every zone or hub to go to the zone C
 - Like the B have a cost of b(5) + c(2) = 7, Y has a cost of y(1) + c(2) = 3, etc.

This algorithm is used because we can have a maximum of 1000 agents. And using the dijkstra method each turn for each agent is not performant at all. But because we know the end target of our agent, we can calculate the cost of each hub at the start of the program and store them so that if we want to check the possible shortest path to the end hub, we can just check every cost of the neighbors of a hub and take the less one.


Second, I adapted the A* algorithm into an A*-like controller that follows the project rules. It repeatedly selects the best neighbor for each drone using a heuristic plus congestion and zone penalties, moves drones in two steps (enter → arrive), and records the simulation until completion or deadlock.

### Behavior

  - Each turn has two phases:
    1. Finish moves for drones currently in a connection (they arrive at the target hub).
    2. Move idle drones to their next hub (choose and enter a neighbor).

- Neighbor selection uses a score combining:
  - heuristic distance to the goal,
  - edge usage frequency,
  - hub congestion,
  - connection congestion,
  - zone type (priority/normal/restricted).
- Movement
  - Entering a connection marks the drone as “in connection” and places it midway between hubs.
  - On the next pass the drone completes the move and reaches the hub.
- Termination
  - Stops when all drones reach the end hub or when no drone can move.


## Visual feature:

Especially for this project, I added background sound and some SFX to make the vibe more pleasing and hopefully get the **Outstanding** for the evaluation XD.

I used the most popular library for visualization in python called pygame (precisely the pygame-ce or pygame community edition). It is an easy library to learn and has a lot of feature like song, text with font, image importation, etc.

### Main Feature

This project has a lot of feature, First is buttons that helps you manipulate the program easily than pressing keyboard and remembering them, But keyboard can also be used to manipulate the program like this:

- `N/P` Next and Previous turn for the drone.
- `A/X` Auto next and auto previous so that you don't need to spam buttons.
- `R` Reset the Turn to be zero.
- `Q` Quit the program and switch to the main screen.

### Screens:

My program has two screen, the home screen and the main program which simulate all the drone.

For the home screen, It has some UI like `Start` to start the program, and `Exit` to end the program. The home screen also have some helpful tips to enhance the user experience like how to move the drone, reset the drone, etc.

For the main program, A lot of implementation was added to make the life of the user easier like 5 **Buttons** to move the drone, some **Help UI** to help the user know how every hub are (position, connection, ...).

