
import unittest
import json
import sys
import os

# Add the parent directory to the Python path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_map_matrix, map_sample_list

class TestMain(unittest.TestCase):
    def test_map_generation(self):
        for map_id in map_sample_list:
            with self.subTest(map_id=map_id):
                # Generate the matrix
                generated_matrix = create_map_matrix(map_id)

                # Load the expected matrix from the JSON file
                file_path = os.path.join(os.path.dirname(__file__), f"{map_id}.json")
                with open(file_path, "r", encoding="utf-8") as f:
                    expected_matrix = json.load(f)

                # Compare the generated matrix with the expected matrix
                self.assertEqual(generated_matrix, expected_matrix)

if __name__ == '__main__':
    unittest.main()
