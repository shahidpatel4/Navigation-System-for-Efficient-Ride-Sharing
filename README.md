# Navigation-System-for-Efficient-Ride-Sharing
Ride-sharing helps reduce traffic and carbon emissions by combining passengers traveling along similar routes. This paper presents a navigation system that uses Greedy Best First Search, A*, Ant Colony Optimization, and Genetic Algorithm to generate optimized routes based on pickup/drop-off locations, traffic conditions, and allow route deviations.

##  Algorithms Implemented

- Greedy Best First Search  
- A* Search (Beam Search Variant)  
- Ant Colony Optimization (ACO)  
- Genetic Algorithm (GA)  

Each algorithm is evaluated based on:
- Total Distance (km)  
- Execution Time  
- Memory Usage  
- Travel Time (with traffic simulation)  

---

##  Features

- Real-world geographic coordinates (50 cities)  
- Distance calculation using Haversine formula  
- Traffic simulation based on time of day  
- Interactive route visualization using Folium maps  
- Graph-based performance comparison  
- AI-based optimization techniques  

---

##  Project Structure

```
├── a_star_beam_50cities.py
├── greedy_best_first_search_50cities.py
├── ant_colony_optimization_50cities.py
├── genetic_50cities.py

├── AStar_beam_50cities_route.html
├── GreedyBestFirst_50cities_route.html
├── AntColony_50cities_route.html
├── GeneticAlgorithm_50cities_route.html

├── images/
│   ├── beam.png
│   ├── ant.png
│   ├── genetic.png
│   ├── greedy.png
│   └── final_distance_style_graph.png
```

---

## ▶️ How to Run

### 1. Install Dependencies
```
pip install folium
```

### 2. Run Any Algorithm
Example:
```
python3 a_star_beam_50cities.py
```

### 3. Open Output Map

After running, open the generated HTML file in your browser:
```
AStar_beam_50cities_route.html
```

---

## Key Observations

- Genetic Algorithm produced the shortest route → best performance  
- A* provided a good balance between efficiency and accuracy  
- Greedy was fastest but gave poor results  
- ACO showed moderate performance  

---

##  Future Improvements

- Integrate real-time traffic data  
- Improve heuristic functions  
- Scale to larger datasets (100+ cities)  
- Explore hybrid algorithms  

---

##  Author

Shahidafreedi Patel  

---

##  License

This project is for academic purposes only.
