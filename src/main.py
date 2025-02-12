""" 
Interface to catch all exceptions and log to file during runtime.
"""
from threads import log_traceback_to_file
try:
    import logging
    from log import set_up_main_logger, change_extension

    set_up_main_logger(change_extension(__file__, ".log"), logging.DEBUG, logging.INFO)

    from app import main
    main()
except Exception as ex:
    log_traceback_to_file(ex, "main-thread")
