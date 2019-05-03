from builtins import str


class AnticipateError(Exception):
    """
    General error for anticipate
    """


class AnticipateErrors(AnticipateError):
    """
    Raised when there are many anticipate errors.
    """
    def __init__(self, message, errors=None):
        """
        Args:
            message (str): Describes the problem
            errors (list): List of errors
        """
        self.errors = errors

        details = []
        for e in self.errors:
            details.append(str(e))

        if details:
            message = message + '\n- ' + '\n- '.join(details)

        super(AnticipateErrors, self).__init__(message)


class AnticipateParamError(AnticipateErrors):
    """
    Raised when a parameter can not be adapted to the anticipated type.
    """
    def __init__(self, message, name, value, anticipated, errors=None):
        """
        Args:
            message (str): Describes the problem
            name (str): Name of the parameter that could not be adapted
            value (mixed): Value that could not be adapted.
            anticipated (type): Type that was expected.
        """
        super(AnticipateParamError, self).__init__(message, errors=errors)
        self.name = name
        self.value = value
        self.anticipated = anticipated