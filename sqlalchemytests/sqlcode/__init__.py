import inspect
import os
import sys


__this_module = sys.modules[__name__]
__module_dir = os.path.dirname(inspect.getfile(__this_module))

files = {
    "postgre": os.path.join(__module_dir, "postgre.sql"),
}
