from modules.model import Model
from models.post import Post
from modules.validations import is_required, is_one_of


class Flag(Post):
    """A proposal to delete a property."""
    reason = Field(
        validate=(is_required, (
            is_one_of, 'offensive', 'irrelevant', 'incorrect',
                       'unpublished', 'duplicate', 'inaccessible'
        ))
    )
    status = Field(
        validate=(is_required, (
            is_one_of, 'pending', 'blocked', 'accepted', 'declined'
        )),
        default='pending'
    )

    def __init__(self, fields=None):
        """

        """
        Model.__init__(self, fields)
        self['kind'] = 'flag'

    # Only one flag per entity per reason is allowed.
    # Otherwise, its a vote for the existing flag proposal for that reason.