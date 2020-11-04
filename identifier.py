from enum import IntEnum
import time
import datetime


def parse_delta_to_seconds(delta):
    time = 0
    delta_list = str(delta).split(":")
    if len(delta_list) == 1:
        time += int(delta_list[0])
    elif len(delta_list) == 2:
        time += int(delta_list[1]) + int(delta_list[0]) * 60
    elif len(delta_list) == 3:
        time += int(delta_list[2]) + int(delta_list[1]) * 60 + int(delta_list[0]) * 3600
    return time


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


def get_language_name(lang_id, region):
    lang: str
    if lang_id == LanguageCode.CHANNEL:
        if str(region) == "japan":
            lang = "サーバーの地域"
        else:
            lang = "ServerRegion"
    elif lang_id == LanguageCode.JAPANESE:
        lang = "日本語"
    elif lang_id == LanguageCode.ENGLISH:
        lang = "English"
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


class MusicElapsedTime:
    def __init__(self):
        self.start_point = time.time()
        self.cached_time = 0

    def pause(self):
        self.cached_time += time.time() - self.start_point
        self.start_point = None

    def resume(self):
        self.start_point = time.time()

    def get_time(self):
        return_time = ""
        if self.start_point is None:
            play_time = self.cached_time
        else:
            play_time = time.time() - self.start_point + self.cached_time
        return datetime.timedelta(seconds=int(play_time))


