from enum import IntEnum


class Background(IntEnum):
    BEARISH_CON_REV = -3
    BEARISH_CON = -2
    BEARISH_REV = -1
    FLAT_REV = 0
    BULLISH_REV = 1
    BULLISH_CON = 2
    BULLISH_CON_REV = 3
