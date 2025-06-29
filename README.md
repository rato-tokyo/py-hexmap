# py-hexmap

This project is a Python implementation of the map generation functionality from the game "hexmap". It allows you to generate game maps and output them in JSON format.

## Usage

To generate a map, you can use the `create_map_matrix` function from `main.py`. This function takes a `map_id` (an integer) as input and returns a 2D list representing the map.

```python
from main import create_map_matrix

map_id = 123
map_data = create_map_matrix(map_id)

# You can then save the map data to a JSON file
import json

with open(f"map_{map_id}.json", "w") as f:
    json.dump(map_data, f)
```

## Testing

To run the tests, execute the following command:

```bash
python tests/test_main.py
```
