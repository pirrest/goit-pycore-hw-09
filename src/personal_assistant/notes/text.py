from personal_assistant.common import RequiredText


class Text(RequiredText):
    """Required note text, must not be empty."""

    ERROR_MESSAGE = "Text cannot be empty."
