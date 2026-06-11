from contextlib import redirect_stdout
from io import StringIO
from src.parsers.parsers import Parsers
from src.algorithms.algorithm import Algorithm

net = Parsers("maps/challenger/01_the_impossible_dream.txt").read_line()
buf = StringIO()
with redirect_stdout(buf):
    Algorithm(net).run()
out = [line for line in buf.getvalue().splitlines() if line.strip()]
final_turn = int(out[-1])
move_lines = out[:-1]

neighbors = {name: set(net.connections.get(name, set())) for name in net.hubs}
hub_cap = {name: hub.metadata.max_drones for name, hub in net.hubs.items()}
conn_cap = {
    name: conn.max_link_capacity for name, conn in net.raw_connection.items()
}
positions = {i: net.start_hub for i in range(1, net.nb_drones + 1)}
in_transit = {i: None for i in range(1, net.nb_drones + 1)}
hub_count = {name: 0 for name in net.hubs}
hub_count[net.start_hub] = net.nb_drones
conn_count = {name: 0 for name in net.raw_connection}


def conn_key(a, b):
    for k in net.raw_connection:
        x, y = k.split("-")
        if {x, y} == {a, b}:
            return k
    return None


errors = []
for turn, line in enumerate(move_lines):
    seen = set()
    for token in line.split():
        parts = token.split("-")
        did = int(parts[0][1:])
        if did in seen:
            errors.append(f"turn {turn}: drone {did} moved twice")
        seen.add(did)
        cur = positions[did]
        if len(parts) == 2:
            dest = parts[1]
            if in_transit[did] is not None:
                if dest != in_transit[did]:
                    errors.append(
                        f"turn {turn}: drone {did} transit finish expected {in_transit[did]} got {dest}"
                    )
                else:
                    positions[did] = dest
                    in_transit[did] = None
                    conn_count[conn_key(cur, dest)] -= 1
            else:
                if dest not in neighbors[cur]:
                    errors.append(f"turn {turn}: no edge {cur}->{dest}")
                    continue
                if hub_count[dest] + 1 > hub_cap[dest]:
                    errors.append(f"turn {turn}: hub cap exceeded at {dest}")
                hub_count[cur] -= 1
                hub_count[dest] += 1
                positions[did] = dest
        elif len(parts) == 3:
            old, dest = parts[1], parts[2]
            if cur != old:
                errors.append(
                    f"turn {turn}: drone {did} current pos {cur} != {old}"
                )
                continue
            if dest not in neighbors[cur]:
                errors.append(f"turn {turn}: no edge {cur}->{dest}")
                continue
            ckey = conn_key(cur, dest)
            if ckey is None:
                errors.append(f"turn {turn}: missing connection {cur}-{dest}")
                continue
            if net.hubs[dest].metadata.zone.value != "restricted":
                errors.append(f"turn {turn}: dest {dest} not restricted")
            if conn_count[ckey] + 1 > conn_cap[ckey]:
                errors.append(f"turn {turn}: connection cap exceeded {ckey}")
            if hub_count[dest] + 1 > hub_cap[dest]:
                errors.append(f"turn {turn}: hub cap exceeded entering {dest}")
            hub_count[cur] -= 1
            hub_count[dest] += 1
            conn_count[ckey] += 1
            in_transit[did] = dest
        else:
            errors.append(f"turn {turn}: bad token {token}")

arrived = sum(1 for p in positions.values() if p == net.end_hub)
transiting = sum(1 for x in in_transit.values() if x is not None)
print("FINAL_TURN", final_turn)
print("ARRIVED", arrived)
print("TRANSITING", transiting)
print("ERRORS", len(errors))
print(
    "VALID"
    if arrived == net.nb_drones and transiting == 0 and not errors
    else "INVALID"
)
for e in errors[:10]:
    print("ERR", e)
