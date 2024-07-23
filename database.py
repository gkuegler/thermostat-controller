import json
import os
import logging
from threading import Lock

from typing import TypeAlias

Serializable: TypeAlias = int | float | dict | list | str

########################################################################
#                           Helper Functions                           #
########################################################################


def load_json_from_file(path, allow_integers_as_keys=False):
    with open(path, "r") as f:
        # Note: JSON treats keys as strings.
        if allow_integers_as_keys:
            return json.load(f,
                             object_hook=lambda d: {
                                 int(k) if k.isdigit() else k: v
                                 for k, v in d.items()
                             })
        else:
            return json.load(f)


def write_json_to_file(path, data):
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def does_folder_exist(folder):
    return os.path.isdir(folder)


# make database access use dotted key scheme with sub dictionaries?
class Database:
    """
    In process database class. Each instance if intended to have its own file
    in the data folder.
    """

    def __init__(self,
                 name: str,
                 sample_data: dict | None = None,
                 overwrite_with_sample_data: bool = False,
                 use_file: bool = True,
                 allowed_to_write: bool = True,
                 log_level: str = "info",
                 allow_integers_as_keys: bool = True):
        """
        Constructor.

        :param      filename:     Unique name of the database.
        :type       filename:     str
        :param      sample_data:  Sample data to be used as a template in the event the file could not be loaded.
        :type       sample_data:  dict
        """

        self.logger = logging.Logger(f"database.{name}", level=logging.INFO)
        self.name = name
        self.file_path = name + ".json"
        self.use_file = use_file
        self.allowed_to_write = use_file and allowed_to_write
        self.allow_integers_as_keys = allow_integers_as_keys
        self.mutex = Lock()

        sample_data = sample_data if sample_data else {}

        self.data = {}  # underlying database data
        """
        Scenarios:
        - file doesn't exist -> create if using a file
        - file failed to load -> create recovery if using a file
        - overwrite existing file with sample data

        """
        if not overwrite_with_sample_data or not self.load():
            self.data = sample_data

        self.save()

    def __setitem__(self, key, value):
        if not self.allow_integers_as_keys and isinstance(key, (int, float)):
            self.logger.error(
                f"'{key}' type '{type(key)}' not allowed as a key in a JSON backed database."
            )
            return
        self.logger.debug(
            f"setting database item ->\nkey '{key}' - type '{type(key)}'\nvalue '{value}' - type '{type(value)}'"
        )
        with self.lock:
            self.data[key] = value
            
        self.save()

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key: int | str, default) -> Serializable:
        self.logger.debug(f"get(): key: {key}")
        with self.lock:
            try:
                return self.data[key]
            except KeyError:
                self.logger.warning(
                    f"'{key}' key not found in {self}. Using default value '{default}'."
                )
                return default

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def update(self, d: dict[str | int, Serializable]):
        self.data.update(d)

    def set_defaults(self, d: dict):
        for key, value in d.items():
            try:
                self.data[key]
            except KeyError:
                self.data[key] = value
        self.save()

    def load(self):
        try:
            self.data = load_json_from_file(
                self.file_path,
                allow_integers_as_keys=self.allow_integers_as_keys)
            return True
        # If the file does not exist load in the sample data.
        # A new data file should be created whenever the key is
        # set through a voice command.
        except FileNotFoundError:
            print(f"{self.name} database -> Loading sample data.\n" +
                  f"Couldn't find file: {self.file_path}")
            return False
        return False

    def save(self):
        self.logger.debug("saving data to file")
        if self.use_file and self.allowed_to_write:
            write_json_to_file(self.file_path, self.data)

    def erase(self):
        self.data = {}
        self.save()

    def __str__(self):
        return f"Database(\"{self.name}\")"


########################################################################
#                               Testing                                #
########################################################################

if __name__ == "__main__":
    test = Database("test", sample_data={"blue": 5})
    print(test.data)
    test.update({"red": 4})
    print(test.data)
