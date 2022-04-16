import re


def onlydigits(text: str) -> str:
    """
    Remove all non-digits from string
    """
    return re.sub('[^\d]', '', text)
