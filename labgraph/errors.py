class NotFoundInDatabaseError(ValueError):
    """Raised when a requested entry is not found in the database"""

    pass


class AlreadyInDatabaseError(ValueError):
    """Raised when a requested entry is already in the database"""

    pass
