# dataclass.py
import os
import csv
import json
from keydb import KeyDB
from dataclasses import dataclass, field
from typing import List, Set, Tuple

@dataclass
class CSVData:
    """Represents a row of data from a TCGplayer CSV File."""
    tcg_id: str
    set_name: str
    product_name: str
    condition: str
    quantity: int
    filepath: str
    row_nuber: int

    def to_json(self):
        """Serialize obj -> str."""
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_str):
        """Deserialize str -> obj."""
        data = json.loads(json_str)
        return cls(**data)
    

@dataclass
class SearchResult:
    """Represents a search result."""
    csv_data: CSVData
    matching_file: str
    matching_row: int


@dataclass
class SearchResults:
    """Represents a collection of search results."""
    results: List[SearchResult] = field(default_factory=list)

    def to_json(self):
        """Serialize obj -> str."""
        return json.dumps([result.__dict__ for result in self.results])
    
    @classmethod
    def from_json(cls, json_str):
        """Deserialize str -> obj."""
        data = json.loads(json_str)
        results = [SearchResult(**result) for result in data]
        return cls(results)
    

@dataclass
class InvertedIndex:
    """Inverted Index for card location lookup."""
    def __init__(self, host="localhost", port=6379):
        self.db = KeyDB(host=host, port=port)

    def index_csv(self, csv_data: CSVData) -> None:
        """Indexes a CSVData object."""
        key = f"term:{csv_data.set_name.lower()}"
        value = f"{csv_data.filepath}:{csv_data.row_number}"
        self.db.set(key, value)

    def index_directory(self, directory: str) -> None:
        """Indexes all CSV files in a directory."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".csv"):
                    self.index_csv(os.path.join(root, file))

    def search(self, term: str) -> SearchResults:
        """Searches Index for the input term."""
        results = SearchResults()
        keys = self.db.keys(f"term:{term.lower()}")
        for key in keys:
            value = self.db.get(key)
            filepath, row_number = value.decode().split(":")
            csv_data = CSVData.from_json(open(filepath, "r").readlines()[int(row_number)])
            search_result = SearchResult(csv_data, filepath, row_number)
            results.results.append(search_result)
        return results


    