
import unittest
import json
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from py_hexmap import generate_map_data

# A list of sample map IDs used for testing purposes.
# This ensures that the map generation logic is tested against a variety of seeds.
map_sample_list=[0,10,1000,123456,9999,99999,999999]

class TestMain(unittest.TestCase):
    def test_map_generation(self):
        # Define default dimensions for testing
        default_x_max = 20
        default_y_max = 11

        for map_id in map_sample_list:
            with self.subTest(map_id=map_id):
                # Generate the map data with default dimensions
                generated_map_data = generate_map_data(map_id, default_x_max, default_y_max)

                # Load the expected map data from the JSON file
                file_path = os.path.join(os.path.dirname(__file__), f"{map_id}.json")
                with open(file_path, "r", encoding="utf-8") as f:
                    expected_map_data = json.load(f)

                # Compare the generated map data with the expected map data
                self.assertEqual(generated_map_data, expected_map_data)

if __name__ == '__main__':
    # Regenerate test data with default dimensions
    default_x_max = 20
    default_y_max = 11
    for map_id in map_sample_list:
        file_path = os.path.join(os.path.dirname(__file__), f"{map_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(generate_map_data(map_id, default_x_max, default_y_max), f, indent=4)

    # Run tests
    unittest.main()
