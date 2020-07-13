from enum import IntEnum


class MusicStatus(IntEnum):
    EMPTY = 0
    PLAYING = 1
    PAUSED = 2
    LOADING = 3


class LanguageCode(IntEnum):
    CHANNEL = 0
    ENGLISH = 1
    JAPANESE = 2


