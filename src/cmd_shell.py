import cmd

# def parse(arg, fn=None):
#     'Convert a series of zero or more numbers to an argument tuple'
#     return tuple(map(int, arg.split()))

# TODO: add logging cmd to pause log events to stdout


class CommandShell(cmd.Cmd):
    intro = 'Welcome to the HVAC cmd terminal.\nType help or ? to list commands.\n'
    prompt = '(hvac cmd) '
    file = None

    def __init__(self, database):
        super().__init__()
        self.db = database

    """
    Help is auto-generated from function comments.
    """

    # def do_help(self, arg):
    # pass

    def do_exit(self, arg):
        """Exit the program."""
        exit()
        return True

    # def do_start(self, arg):
    #     pass

    # def do_stop(self, arg):
    #     pass

    def do_http(self, arg):
        """Toggle HTTP variable.
This has the effect of enabling/disabling control of
the furnace by allowing/blocking http requests
to the furnace relay mcu.\n"""
        self.db.set("http_enabled", not self.db["http_enabled"])

    def do_dump(self, arg):
        """Display all variables.\n"""
        print("-- Available Parameters --")
        print(self.db)

    def do_set(self, arg):
        """Set a variable. Use 'dump' commant to get list
of variable names.\n"""
        key, value = arg.split()
        #TODO: add value type lookup for type safety. See
        try:
            value = int(value)
        except:
            try:
                value = float(value)
            except:
                # Value is a string.
                pass

        if err := self.db.set(key, value):
            print(err)
