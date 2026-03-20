from config.config import Config

_cfg = Config.from_env()


class Constants:
    BUY_TP = _cfg.BUY_TP
    SELL_TP = _cfg.SELL_TP
    BUY_LOSS = _cfg.BUY_LOSS
    SELL_LOSS = _cfg.SELL_LOSS
    BUY_SL = _cfg.BUY_SL
    SELL_SL = _cfg.SELL_SL
    BUY_CANCEL = _cfg.BUY_CANCEL
    SELL_CANCEL = _cfg.SELL_CANCEL


BUY_TP = Constants.BUY_TP
SELL_TP = Constants.SELL_TP
BUY_LOSS = Constants.BUY_LOSS
SELL_LOSS = Constants.SELL_LOSS
BUY_SL = Constants.BUY_SL
SELL_SL = Constants.SELL_SL
BUY_CANCEL = Constants.BUY_CANCEL
SELL_CANCEL = Constants.SELL_CANCEL
