import inspect
import os
import sys

__this_module = sys.modules[__name__]
__module_dir = os.path.dirname(inspect.getfile(__this_module))

files = {
    "names": os.path.join(__module_dir, "names_list.txt"),
    "professions": os.path.join(__module_dir, "professions.txt"),
    "team_names": os.path.join(__module_dir, "team_names.txt")
}

