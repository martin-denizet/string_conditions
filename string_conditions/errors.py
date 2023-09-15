class StringConditionError(Exception):
    pass


class UnsupportedSyntaxError(StringConditionError):
    pass


class UnknownVariableError(StringConditionError):
    pass


class BadSyntaxError(StringConditionError):
    pass

class InvalidContextError(Exception):
    pass
