from enum import IntEnum


def get_language(lang_id, region):
    lang: LanguageCode
    if lang_id == LanguageCode.CHANNEL:
        if str(region) == "japan":
            lang = LanguageCode.JAPANESE
        else:
            lang = LanguageCode.ENGLISH
    elif lang_id == LanguageCode.JAPANESE:
        lang = LanguageCode.JAPANESE
    elif lang_id == LanguageCode.ENGLISH:
        lang = LanguageCode.ENGLISH
    return lang


class MusicStatus(IntEnum):
    EMPTY = 0
    PLAYING = 1
    PAUSED = 2
    LOADING = 3


class LanguageCode(IntEnum):
    CHANNEL = 0
    ENGLISH = 1
    JAPANESE = 2


