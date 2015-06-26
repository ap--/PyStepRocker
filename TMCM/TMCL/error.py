
class TMCLError(Exception):
    """Base TMCL exception"""

    def __init__(self, command=None, message=None):
        super(TMCLError, self).__init__(command, message)
        self.command = command
        self.message = message

    def __str__(self):
        if self.message is None:
            return "TMCL: {}".format(self.command)
        else:
            return "{}: {}".format(self.command, self.message)


class TMCLStatusError(TMCLError):
    """TMCL exception for non-OK statuses"""

    def __init__(self, command, status):
        message = "got status: {}".format(status)
        super(TMCLStatusError, self).__init__(command, message)
        self.status = status


class TMCLMissingElement(TMCLError):
    """Base TMCL exception for missing elements in containers"""

    def __init__(self, command, kind, element, container):
        message = "{} {} not in {}".format(kind, element, container)
        super(TMCLMissingElement, self).__init__(command, message)
        self.kind = kind
        self.element = element
        self.container = container


class TMCLKeyError(TMCLMissingElement):
    """TMCL exception for missing key in dictionary"""

    def __init__(self, command, kind, key, dictionary):
        super(TMCLKeyError, self).__init__(command, kind, key, dictionary.keys())
        self.key = key
        self.dictionary = dictionary


class TMCLRangeError(TMCLMissingElement):
    """TMCL exception for missing value in range"""

    def __init__(self, command, kind, value, limit, other_limit=None):

        if other_limit is None:
            srange = str(limit)
        else:
            limit, other_limit = sorted((limit, other_limit))
            srange = "{}, {}".format(limit, other_limit)

        srange = "range({})".format(srange)

        super(TMCLRangeError, self).__init__(command, kind, value, srange)
        self.value = value
        self.range_min = limit
        self.range_max = other_limit


