import cmd

# def parse(arg, fn=None):
#     'Convert a series of zero or more numbers to an argument tuple'
#     return tuple(map(int, arg.split()))


class CommandShell(cmd.Cmd):
    intro = 'Welcome to the HVAC terminal.\nType help or ? to list commands.\n'
    prompt = '(control) '
    file = None

    def __init__(self, database):
        super().__init__()
        self.db = database

    # # ----- basic turtle commands -----
    # def do_help(self, arg):
    #     'Move the turtle forward by the specified distance:  FORWARD 10'
    #     # print(*parse(arg))
    #     print(arg)

    def do_exit(self, arg):
        """Exit the program."""
        exit()
        return True

    # def do_start(self, arg):
    #     pass

    # def do_stop(self, arg):
    #     pass

    def do_http(self, arg):
        self.db.set("http_enabled", not self.db["http_enabled"])

    def do_dump(self, arg):
        print(self.db)

    def do_set(self, arg):
        """
        Set a value:
        sp
        threshold
        timeout
        host
        port
        """
        key, value = arg.split()
        #TODO: add value type lookup for type safety
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


# if __name__ == '__main__':
# CommandShell().cmdloop()
