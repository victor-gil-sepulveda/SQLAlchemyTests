import inspect
import os

__module_dir = os.path.dirname(inspect.getfile(inspect))

files = {
    "postgre": os.path.join(__module_dir, "postgre.sql"),
}