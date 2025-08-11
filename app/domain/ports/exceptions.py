class RepositoryException(Exception):
    pass


class EntityNotFound(RepositoryException):
    pass


class EntityAlreadyExists(RepositoryException):
    pass
