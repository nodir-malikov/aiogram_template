import re


def onlydigits(text: str) -> str:
    """
    Remove all non-digits from string
    """
    return re.sub('[^\d]', '', text)


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
