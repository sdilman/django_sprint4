from enum import Flag, auto


class PostFlags(Flag):
    PUBLISHED = auto()
    RELATED = auto()
    SORTED = auto()
    ANNOTATED = auto()
