""" 
Interface to catch all exceptions during runtime.
"""

import traceback
import os

try:
    from app import main
    main()
except Exception as ex:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def format_traceback(ex):
        s = "-------- start exception traceback --------\n"
        s += "".join(traceback.format_exception(ex))
        s += "-------- end exception traceback --------\n"
        return s

    with open(os.path.join(dir_path, 'traceback.log'), 'wt') as f:
        f.write(format_traceback(ex))
