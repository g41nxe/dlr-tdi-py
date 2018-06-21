from abc import ABCMeta, abstractmethod, abstractproperty

class Package():
    __metaclass__ = ABCMeta

    @abstractproperty
    def types(self):
        pass

    @abstractproperty
    def MSG_LENGTH(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @staticmethod
    @abstractmethod
    def from_string(self, str):
       pass

class Command(Package):
    """
    ------------------------------------------------------------
   | length (2)      | Command.type (4-5)   | value (0-16)      |
    ------------------------------------------------------------
    ------------------------------------------------------------
   | 4-8             | freq                 | value (4)         |
    ------------------------------------------------------------
   | 5               | start                | (0)               |
    ------------------------------------------------------------
   | 4-20            | stop                 | identifier (0-16) |
    ------------------------------------------------------------
    """

    MSG_LENGTH = 2

    types = {"freq", "start", "stop", "save"}

    def __init__(self, command, value):

        self.command = command
        self.value   = value

        if self.command not in self.types: raise (ValueError("Unknown type"));

        return

    def __str__(self):
        msg = ".".join(map(lambda x: str(x), (self.command, self.value)))
        l = str(format(len(msg), '02'))

        if len(l) != self.MSG_LENGTH:
            raise AssertionError("Message length cannot be > 2 characters")

        return l + msg

    @staticmethod
    def from_string(string):
        parts = string.split(".")

        if len(parts) is not 2:
            raise ValueError("invalid argument")

        return Command(parts[0], parts[1])

class Response(Package):
    """
     ------------------------------------------------
    | length | Command.type | value  | Response.type |
     ------------------------------------------------
    | 11-28  | 4-5          | 0-16   | 7             |
     ------------------------------------------------
    """

    MSG_LENGTH = 2

    types =  {"success" , "failure"}

    def __init__(self, package, response):

        self.value    = package.value
        self.command  = package.command
        self.response = "success" if response is True else "failure"

        if self.command not in Command.types:
            raise (ValueError("Unknown type"))

        if self.response not in self.types:
            raise (ValueError("Unknown type"))

    def __str__(self):
        msg = ".".join(map(lambda x: str(x), (self.command, self.value , self.response)))
        l = str(format(len(msg), '02'))

        if len(l) != self.MSG_LENGTH:
            raise AssertionError("Message length cannot be > 2 characters")

        return l + msg

    @staticmethod
    def from_string(string):
        parts = string.split(".")

        if len(parts) is not 3:
            raise ValueError("invalid argument")

        return Response(Command(parts[0], parts[1]), True if parts[2] == "true" else False)