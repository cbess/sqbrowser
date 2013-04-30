# provide logic for the json query runner
# docs: https://github.com/shaung/jsondb/blob/master/tests/test_bookstore.py

import jsondb
import json
import tempfile


class JSONBase:
    def __init__(self, json_path):
        self.path = json_path

    def get_json(self):
        """
        Gets the JSON from the path
        """
        pass

    def execute(self):
        pass