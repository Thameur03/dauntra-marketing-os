from enum import StrEnum


class Platform(StrEnum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    X = "x"
    FACEBOOK = "facebook"
    REDDIT = "reddit"


class Market(StrEnum):
    GLOBAL = "GLOBAL"


class Language(StrEnum):
    EN = "en"


class ContentFamily(StrEnum):
    C01 = "C01"
    C02 = "C02"
    C03 = "C03"
    C04 = "C04"


class ContentFormat(StrEnum):
    CAROUSEL = "carousel"
    VIDEO = "video"
    TEXT = "text"
    THREAD = "thread"
    DISCUSSION = "discussion"
    IMAGE = "image"


class Decision(StrEnum):
    DOUBLE_DOWN = "DOUBLE_DOWN"
    KEEP_TESTING = "KEEP_TESTING"
    PAUSE = "PAUSE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class QAResult(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class QAGate(StrEnum):
    SCHEMA = "SCHEMA"
    PRODUCT_CAPABILITY = "PRODUCT_CAPABILITY"
    FACTUAL = "FACTUAL"
    HEALTH_CLAIM = "HEALTH_CLAIM"
    BRAND = "BRAND"
    DUPLICATE = "DUPLICATE"
    VISUAL = "VISUAL"
    PLATFORM_FORMAT = "PLATFORM_FORMAT"
    HUMAN_REVIEW = "HUMAN_REVIEW"
