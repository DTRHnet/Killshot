import json

class MenuManager:
    @staticmethod
    def read_menu_from_json(file_path):
        """
        Reads a menu structure from a JSON file.
        :param file_path: Path to the JSON file.
        :return: Menu structure as a dictionary.
        """
        with open(file_path, 'r') as file:
            menu_data = json.load(file)
        return menu_data

    @staticmethod
    def write_menu_to_json(menu_data, file_path):
        """
        Writes the menu structure to a JSON file.
        :param menu_data: Menu structure as a dictionary.
        :param file_path: Path to the JSON file.
        """
        with open(file_path, 'w') as file:
            json.dump(menu_data, file, indent=4)
