""" 
Interface to catch all exceptions and log to file during runtime.
"""
from threads import log_traceback_to_file

try:
    from app import main
    main()
except Exception as ex:
    log_traceback_to_file(ex, "main-thread")
