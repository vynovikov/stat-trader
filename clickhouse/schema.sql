CREATE TABLE trades_real (
  id            UInt64,
  open_time     DateTime,
  close_time    DateTime,
  symbol        LowCardinality(String),
  timeframe     LowCardinality(String),
  reason        LowCardinality(String),
  engine_id     Enum8('engine_rev_v5' = 0, 'engine_con_v6' = 1),
  candle_action Enum8('none' = 0, 'buy' = 1, 'sell' = 2),
  entry_price   Float64,
  stop_loss     Float64,
  take_profit   Float64,
  volume        Float64,
  profit        Float64
)
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(open_time)
ORDER BY (symbol, engine_id, open_time, id);

CREATE TABLE candles_all (
  symbol       LowCardinality(String),
  timeframe    LowCardinality(String),
  open         Float64,
  high         Float64,
  low          Float64,
  close        Float64,
  open_time    DateTime,
  close_time   DateTime,
  volume       Float64
)
ENGINE = ReplacingMergeTree()
PARTITION BY (symbol, toYYYYMM(close_time))
ORDER BY (symbol, timeframe, close_time);

CREATE TABLE candles_traded (
  symbol       LowCardinality(String),
  timeframe    LowCardinality(String),
  engine_id    LowCardinality(String),
  open         Float64,
  high         Float64,
  low          Float64,
  close        Float64,
  open_time    DateTime,
  close_time   DateTime,
  volume       Float64,
  trade_id     Nullable(UInt64)
)
ENGINE = ReplacingMergeTree()
PARTITION BY (symbol, toYYYYMM(close_time))
ORDER BY (symbol, timeframe, close_time);

CREATE TABLE trades_historical (
  id            UInt64,
  open_time     DateTime,
  close_time    DateTime,
  symbol        LowCardinality(String),
  timeframe     LowCardinality(String),
  reason        LowCardinality(String),
  engine_id     Enum8('engine_rev_v5' = 0, 'engine_con_v6' = 1),
  candle_action Enum8('none' = 0, 'buy' = 1, 'sell' = 2),
  entry_price   Float64,
  stop_loss     Float64,
  take_profit   Float64,
  volume        Float64,
  profit        Float64
)
ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(open_time)
ORDER BY (symbol, engine_id, open_time, id);

CREATE TABLE candles_historical (
  symbol       LowCardinality(String),
  timeframe    LowCardinality(String),
  engine_id    LowCardinality(String),
  open         Float64,
  high         Float64,
  low          Float64,
  close        Float64,
  open_time    DateTime,
  close_time   DateTime,
  volume       Float64,
  trade_id     Nullable(UInt64)
)
ENGINE = ReplacingMergeTree()
PARTITION BY (symbol, toYYYYMM(close_time))
ORDER BY (symbol, timeframe, close_time);

CREATE TABLE logs (
  created_at    DateTime,
  log_level     LowCardinality(String),
  service_name  LowCardinality(String),
  log_string    String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, service_name);