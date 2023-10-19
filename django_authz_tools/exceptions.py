class ProjectException(Exception):
    """
    Base exception for the project.
    """
    pass


class ModelIsNotAbstractException(ProjectException):
    """
    Raised when the model must be abstract, while concrete one is given.
    """
    pass


class ModelIsNotConcreteException(ProjectException):
    """
    Raised when the model must be concrete, while abstract one is given.
    """
    pass
