"""
Bazaar exceptions.
"""

class BazaarError(Exception):
    """
    Abstract, basic class for all Bazaar exceptions.
    """
    pass


class MappingError(BazaarError):
    """
    Abstract, basic class for all mapping exceptions.

    @ivar cls: Application class.

    @see: L{bazaar.exc.ColumnMappingError} L{bazaar.exc.RelationMappingError}
    """
    def __init__(self, msg, cls):
        """
        Create mapping exception.

        @param msg: Exception message.
        @param cls: Application class.
        """
        BazaarError.__init__(self, msg)
        self.cls = cls


class RelationMappingError(MappingError):
    """
    Database relation mapping exception. Exception is thrown on mapping
    database relation to application class error, i.e. empty relation
    name.
    """
    pass


class ColumnMappingError(MappingError):
    """
    Relation column mapping exception. Exception is thrown on mapping
    relation column to application class attribute error, i.e. empty
    attribute name.

    @ivar col: Application class column object.
    """
    def __init__(self, msg, cls, col):
        """
        Create relation column mapping exception.

        @param msg: Exception message.
        @param cls: Application class.
        @param col: Application class column object.
        """
        MappingError.__init__(self, msg, cls)
        self.col = col


class AssociationError(BazaarError):
    """
    Association exception.

    @ivar asc: Association object.
    @ivar obj: Application object.
    @ivar value: Referenced object.
    """
    def __init__(self, msg, asc, obj, value):
        """
        Create association exception.

        @param msg: Exception message.
        @param asc: Association object.
        @param obj: Application object.
        @param value: Referenced object.
        """
        BazaarError.__init__(self, msg)
        self.asc = asc
        self.obj = obj
        self.value = value
