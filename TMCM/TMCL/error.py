
class TMCLError(Exception):
    pass


class TMCLStatusError(TMCLError):

    def __init__(self, command, status):
        self.command = command
        self.status = status

    def __str__(self):
        return "{}: got status: {}".format(self.command, self.status)


class TMCLMissingElement(TMCLError):

    def __init__(self, command, kind, element, container):
        self.command = command
        self.kind = kind
        self.element = element
        self.container = container

    def __str__(self):
            return "{}: {} {} not in {}".format(self.command, self.kind, self.element, self.container)


class TMCLKeyError(TMCLMissingElement):

    def __init__(self, command, kind, key, dictionary):
        super(TMCLKeyError, self).__init__(command, kind, key, dictionary.keys())
        self.key = key
        self.dictionary = dictionary


class TMCLRangeError(TMCLMissingElement):

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


