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

    def do_start(self, arg):
        pass

    def do_stop(self, arg):
        pass

    def do_http(self, arg):
        self.db["http_enabled"] = not self.db["http_enabled"]

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
        try:
            value = int(value)
        except:
            try:
                value = float(value)
            except:
                # value is a string
                pass

        if err:=self.db.set_existing(key, value):
            print(err)
        # match key:
        #     case "sp":
        #         self.set_sp(value)
        #     case "threshold":
        #         self.set_threshold(value)
        #     case "timeout":
        #         self.set_timeout(value)
        #     case "host":
        #         self.set_host(value)
        #     case "port":
        #         self.set_port(value)

    # # ----- record and playback -----
    # def do_record(self, arg):
    #     'Save future commands to filename:  RECORD rose.cmd'
    #     self.file = open(arg, 'w')
    # def do_playback(self, arg):
    #     'Playback commands from a file:  PLAYBACK rose.cmd'
    #     self.close()
    #     with open(arg) as f:
    #         self.cmdqueue.extend(f.read().splitlines())
    # def precmd(self, line):
    #     line = line.lower()
    #     if self.file and 'playback' not in line:
    #         print(line, file=self.file)
    # return line


if __name__ == '__main__':
    CommandShell(print, print, print, print, print, print).cmdloop()
