
import math
import time
import tracemalloc
import warnings
from functools import lru_cache
import random

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
            color = "green"
            title = "Start"
        elif i == len(path):
            color = "red"
            title = "Final Destination"
        else:
            color = "blue"
            title = f"Stop {i}"
        popup = folium.Popup(f"<b>{title}</b><br>{name}<br>Step {i}", max_width=250)
        folium.Marker([lat, lon], popup=popup, icon=folium.Icon(color=color)).add_to(fmap)

    fmap.save(out_file)
    print(f"Map has been saved to {out_file}. Open this file in a web browser to view the route.")

def genetic_route(pop_size=140, generations=280, mutation_rate=0.18, elite=6, seed=42):
    random.seed(seed)
    start = CITIES[0]
    goal = CITIES[-1]
    middle = CITIES[1:-1]

    def fitness(chrom):
        path = [start] + chrom + [goal]
        return total_distance(path)

    def crossover(a, b):
        left, right = sorted(random.sample(range(len(a)), 2))
        child = [None] * len(a)
        child[left:right+1] = a[left:right+1]
        fill = [x for x in b if x not in child]
        idx = 0
        for i in range(len(child)):
            if child[i] is None:
                child[i] = fill[idx]
                idx += 1
        return child

    def mutate(chrom):
        c = chrom[:]
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(c)), 2)
            c[i], c[j] = c[j], c[i]
        return c

    population = []
    for _ in range(pop_size):
        chrom = middle[:]
        random.shuffle(chrom)
        population.append(chrom)

    best = None
    best_cost = float("inf")
    for _ in range(generations):
        ranked = sorted(population, key=fitness)
        if fitness(ranked[0]) < best_cost:
            best = ranked[0][:]
            best_cost = fitness(best)
        new_pop = [r[:] for r in ranked[:elite]]
        while len(new_pop) < pop_size:
            p1 = random.choice(ranked[:pop_size//3])
            p2 = random.choice(ranked[:pop_size//3])
            child = mutate(crossover(p1, p2))
            new_pop.append(child)
        population = new_pop

    return [start] + best + [goal]


if __name__ == "__main__":
    tracemalloc.start()
    t0 = time.perf_counter()
    path = genetic_route()
    elapsed = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print_steps(path, "Genetic Algorithm (50 Cities)")
    dist = total_distance(path)
    hours = total_travel_hours(path)
    print(f"Total Distance: {dist:.2f} km")
    print(f"Execution Time: {elapsed:.2f} seconds")
    print(f"Memory Consumption: {peak / (1024 * 1024):.2f} MB")
    print(f"Time Taken to reach destination: {hours:.2f} hr")
    save_map(path, "GeneticAlgorithm_50cities_route.html")
