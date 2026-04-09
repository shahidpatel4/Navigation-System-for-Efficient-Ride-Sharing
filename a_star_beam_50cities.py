
import math
import time
import tracemalloc
import warnings
from functools import lru_cache

warnings.filterwarnings("ignore")

import folium

CITIES = [('San Francisco', 37.7749, -122.4194), ('Oakland', 37.8044, -122.2712), ('Berkeley', 37.8715, -122.273), ('Concord', 37.978, -122.0311), ('Vallejo', 38.1041, -122.2566), ('Hayward', 37.6688, -122.0808), ('Fremont', 37.5485, -121.9886), ('Sunnyvale', 37.3688, -122.0363), ('Santa Clara', 37.3541, -121.9552), ('San Jose', 37.3382, -121.8863), ('Salinas', 36.6777, -121.6555), ('Modesto', 37.6391, -120.9969), ('Stockton', 37.9577, -121.2908), ('Elk Grove', 38.4088, -121.3716), ('Sacramento', 38.5816, -121.4944), ('Roseville', 38.7521, -121.288), ('Santa Rosa', 38.4405, -122.7144), ('Fresno', 36.7378, -119.7871), ('Visalia', 36.3302, -119.2921), ('Bakersfield', 35.3733, -119.0187), ('Lancaster', 34.6868, -118.1542), ('Palmdale', 34.5794, -118.1165), ('Santa Clarita', 34.3917, -118.5426), ('Simi Valley', 34.2694, -118.7815), ('Thousand Oaks', 34.1706, -118.8376), ('Oxnard', 34.1975, -119.1771), ('Glendale', 34.1425, -118.2551), ('Pasadena', 34.1478, -118.1445), ('Fullerton', 33.8704, -117.9242), ('Anaheim', 33.8366, -117.9143), ('Garden Grove', 33.7743, -117.9379), ('Santa Ana', 33.7455, -117.8677), ('Orange', 33.7879, -117.8531), ('Irvine', 33.6846, -117.8265), ('Huntington Beach', 33.6595, -117.9988), ('Long Beach', 33.7701, -118.1937), ('Torrance', 33.8358, -118.3406), ('Pomona', 34.0551, -117.749), ('Ontario', 34.0633, -117.6509), ('Rancho Cucamonga', 34.1064, -117.5931), ('Fontana', 34.0922, -117.435), ('San Bernardino', 34.1083, -117.2898), ('Riverside', 33.9806, -117.3755), ('Moreno Valley', 33.9425, -117.2297), ('Victorville', 34.5361, -117.2912), ('Oceanside', 33.1959, -117.3795), ('Escondido', 33.1192, -117.0864), ('San Diego', 32.7157, -117.1611), ('Chula Vista', 32.6401, -117.0842), ('Los Angeles', 34.0522, -118.2437)]

def haversine(city1, city2):
    _, lat1, lon1 = city1
    _, lat2, lon2 = city2
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def traffic_intensity(hour):
    return 1.5 if hour in [7, 8, 9, 17, 18, 19] else 1.0

def total_distance(path):
    return sum(haversine(path[i], path[i + 1]) for i in range(len(path) - 1))

def total_travel_hours(path, avg_speed_kmph=150.0):
    weighted = sum(haversine(path[i], path[i + 1]) * traffic_intensity(12) for i in range(len(path) - 1))
    return weighted / avg_speed_kmph

def print_steps(path, title):
    print(f"{title}:")
    print(f"Path: {path}")
    print("\nDetailed Route Steps:")
    for i, city in enumerate(path, start=1):
        name, lat, lon = city
        if i == 1:
            print(f"  Step {i}: Start from {name} at ({lat:.4f}, {lon:.4f})")
        elif i == len(path):
            print(f"  Step {i}: Reach final destination {name} at ({lat:.4f}, {lon:.4f})")
        else:
            print(f"  Step {i}: Travel to {name} at ({lat:.4f}, {lon:.4f})")

def save_map(path, out_file):
    start = path[0]
    fmap = folium.Map(location=[start[1], start[2]], zoom_start=6)
    folium.PolyLine([(c[1], c[2]) for c in path], weight=5, opacity=0.8).add_to(fmap)
    for i, city in enumerate(path, start=1):
        name, lat, lon = city
        if i == 1:
            color = "green"; title = "Start"
        elif i == len(path):
            color = "red"; title = "Final Destination"
        else:
            color = "blue"; title = f"Stop {i}"
        popup = folium.Popup(f"<b>{title}</b><br>{name}<br>Step {i}", max_width=250)
        folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(fmap)
    fmap.save(out_file)
    print(f"Map has been saved to {out_file}. Open this file in a web browser to view the route.")

@lru_cache(maxsize=None)
def mst_cost(indices):
    idxs = list(indices)
    if len(idxs) <= 1:
        return 0.0
    remaining = set(idxs[1:])
    tree = {idxs[0]}
    cost = 0.0
    while remaining:
        best = None
        best_d = float("inf")
        for a in tree:
            for b in remaining:
                d = haversine(CITIES[a], CITIES[b])
                if d < best_d:
                    best_d = d
                    best = b
        cost += best_d
        tree.add(best)
        remaining.remove(best)
    return cost

def heuristic(current_idx, unvisited_fs):
    goal_idx = len(CITIES) - 1
    if not unvisited_fs:
        return haversine(CITIES[current_idx], CITIES[goal_idx])
    unvisited = list(unvisited_fs)
    to_unvisited = min(haversine(CITIES[current_idx], CITIES[i]) for i in unvisited)
    from_unvisited_to_goal = min(haversine(CITIES[i], CITIES[goal_idx]) for i in unvisited)
    return to_unvisited + mst_cost(tuple(sorted(unvisited))) + from_unvisited_to_goal

def beam_astar_route(beam_width=6, expansion_limit=3000):
    n = len(CITIES)
    start_idx = 0
    goal_idx = n - 1
    all_mid = frozenset(range(1, goal_idx))
    frontier = [(start_idx, all_mid, [start_idx], 0.0)]
    expanded = 0

    for depth in range(1, n + 2):
        candidates = []
        for current, unvisited, path, g in frontier:
            expanded += 1
            if expanded > expansion_limit:
                best = min(frontier, key=lambda s: s[3] + heuristic(s[0], s[1]))
                current, unvisited, path, g = best
                full_path = path[:]
                remaining = set(unvisited)
                while remaining:
                    nxt = min(remaining, key=lambda i: haversine(CITIES[full_path[-1]], CITIES[i]))
                    full_path.append(nxt)
                    remaining.remove(nxt)
                if full_path[-1] != goal_idx:
                    full_path.append(goal_idx)
                print(f"Expanded states before cutoff: {expanded}")
                return [CITIES[i] for i in full_path]

            if not unvisited:
                final_path = path + ([goal_idx] if path[-1] != goal_idx else [])
                print(f"Expanded states: {expanded}")
                return [CITIES[i] for i in final_path]

            # expand a restricted promising set first
            ordered_next = sorted(
                unvisited,
                key=lambda i: haversine(CITIES[current], CITIES[i]) + 0.4 * haversine(CITIES[i], CITIES[goal_idx])
            )[:max(beam_width * 2, 8)]

            for nxt in ordered_next:
                new_unvisited = frozenset(x for x in unvisited if x != nxt)
                new_g = g + haversine(CITIES[current], CITIES[nxt])
                f = new_g + heuristic(nxt, new_unvisited)
                candidates.append((f, nxt, new_unvisited, path + [nxt], new_g))

        candidates.sort(key=lambda x: x[0])
        frontier = [(nxt, unvisited, path, g) for f, nxt, unvisited, path, g in candidates[:beam_width]]

    raise RuntimeError("No route found")

if __name__ == "__main__":
    tracemalloc.start()
    t0 = time.perf_counter()
    path = beam_astar_route()
    elapsed = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print_steps(path, "A* Algorithm (50 Cities, beam-search variant)")
    dist = total_distance(path)
    hours = total_travel_hours(path)
    print(f"Total Distance: {dist:.2f} km")
    print(f"Execution Time: {elapsed:.2f} seconds")
    print(f"Memory Consumption: {peak / (1024 * 1024):.2f} MB")
    print(f"Time Taken to reach destination: {hours:.2f} hr")
    save_map(path, "AStar_beam_50cities_route.html")
