"""
No-op semantic model definition.
"""

from penman.types import BasicTriple
from penman.model import Model


class NoOpModel(Model):
    """
    A no-operation model that mostly leaves things alone.

    This model is like the default :class:`~penman.model.Model` except
    that :meth:`NoOpModel.deinvert` always returns the original
    triple, even if it was inverted.
    """
    def deinvert(self, triple: BasicTriple) -> BasicTriple:
        """Return *triple* (does not deinvert)."""
        return triple


model = NoOpModel()
