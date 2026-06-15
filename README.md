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


# Instruction:

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

# Ressources:

- Peer learning
- [MAPF wikidedia](hhps://en.widipedia.org/wiki/Multi-agent_pathfinding)
- [Prioritized Planning](https://www.youtube.com/watch?v=9XIPCn4CzOA)
- [A star Algorithm](hhps://en.widipedia.org/wiki/A*_search_algorithm)

## AI usage:

AI was mainly used to help with debugging specific problem like the rendering or the parsing part, It also help me verify why my approach is wrong and what to improve.

# Extras:

## Algorithm choice:

I used a two main implementation with this project.

First, to check the estimated turn to go to the end, I used the reverse dijkstra method, It is a variant of the dijkstra method.

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

The second algorithm I used is the.


## Visual feature:

For this project, I used the most popular library for visualization in python called pygame (precisely the pygame-ce or pygame community edition). It is an easy library to learn and has a lot of feature like song, text with font, image importation, etc.

My program has two screen, the home screen and the main program which simulate all the drone.

For the home screen, It has some UI like `Start` to start the program, and `Exit` to end the program. The home screen also have some helpful tips to enhance the user experience like how to move the drone, reset the drone, etc.

For the main program, A lot of implementation was added to make the life of the user easier like 5 **Buttons** to move the drone, some **Help UI** to help the user know how every hub are (position, connection, ...).

Especially for this project, I added background sound and some SFX to make the vibe more pleasing and hopefully get the **Outstanding** for the evaluation XD.
