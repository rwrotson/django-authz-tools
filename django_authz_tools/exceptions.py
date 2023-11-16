class AuthzToolsException(Exception):
    """
    Base exception for the project.
    """
    pass


class ModelIsNotAbstractException(AuthzToolsException):
    """
    Raised when the model must be abstract, while concrete one is given.
    """
    pass


class ModelIsNotConcreteException(AuthzToolsException):
    """
    Raised when the model must be concrete, while abstract one is given.
    """
    pass
