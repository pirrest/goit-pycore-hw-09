class Field:
    """Base class for record fields."""

    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)
