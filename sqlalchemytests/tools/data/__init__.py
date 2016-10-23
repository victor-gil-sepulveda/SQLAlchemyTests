import inspect
import os

__module_dir = os.path.dirname(inspect.getfile(inspect))

files = {
    "names": os.path.join(__module_dir, "names_list.txt"),
    "professions": os.path.join(__module_dir, "professions.txt"),
    "team_names": os.path.join(__module_dir, "team_names.txt")
}

