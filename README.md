[Русская версия](README.ru.md)

# What is stat-trader?
Exchange trading is a high-yield activity that comes with several significant challenges:

* Market Monitoring: Requires constant, 24/7 price tracking to remain effective
* Technical Expertise: Demands extensive experience in interpreting price charts
* Strategy Reliance: Requires a robust trading strategy for consistent performance
* Emotional Bias: Maintaining the discipline to follow a strategy during drawdowns is psychologically taxing

As a result, 98% of market participants lose money.

Stat-trader is an algorithmic trading system designed to address these challenges:

* Operates 24/7: Continuously processes every new [candle](#candle) without interruption
* Ensures Disciplined Execution: Strictly follows a predefined [trading strategy](#trading_strategy)
* Identifies a Statistical Edge: Waits for high-probability entry points and decides whether to execute a trade or pass
* Automates Trade Planning: Calculates execution levels, including stop-loss and take-profit
* Optimizes Position Sizing: Determines the exact volume for each trade based on integrated [risk management](#risk_management)
* Tracks Performance: Maintains comprehensive trade statistics and visualizes candlestick charts

# Stat-trader
Stat-trader is built as a suite of interoperating microservices.

<img src="assets/stat-trader.gif" alt="Demo">

*Arrows indicate data flow direction*

***Click the diagram to activate animation***

* [**Stock-interactor**](#stock_interactor): An exchange interface service. It consumes data via WebSockets and utilizes exchange APIs for order execution. Additionally, it fetches historical data for specified intervals. Built with Golang.
* [**Trade-engine**](#trade_engine): The decision-making core. It processes each [candle](#candle) immediately upon closing to evaluate entry signals. It calculates all trade parameters, including order type, direction, entry price, stop-loss, and take-profit. Built with Python.
* [**Monitoring**](#logging_and_monitoring).: Powered by Grafana, with Prometheus and ClickHouse as data sources. The system tracks metrics, detailed trading statistics, and logs.

The architecture focuses on flexibility and maintainability. Components are loosely coupled, ensuring system resilience: if one service fails, others remain operational. Updates are isolated to individual components; for instance, changing an asset or an exchange only requires reconfiguring the Stock-interactor, leaving the rest of the stack untouched.

<a id="stock_interactor"></a>

# Stock-interactor

The diagram below shows the service receiving a [candle](#candle) and passing it through the pipeline.

<img src="assets/stock-interactor.gif" alt="Demo">

***Click the diagram to activate animation***

<a id="timing_requirements"></a>
In this workflow, timing is critical. Data transmission is triggered 500ms before the current candle closes. This provides a sufficient buffer for end-to-end processing (including internal communication) and HTTP request delivery to the exchange.
The worker identifies the [candle](#candle) close time and schedules the data transfer. Meanwhile, it streams data from WebSockets into a thread-safe cache, which is then flushed to the appropriate channel at the scheduled time.

Key Technical Features:

* **Clean Architecture**: Functional logic is organized into layers, decoupled via interfaces
* **Asynchronous Data Ingestion**: The ticker layer employs multiple workers synchronized through channels
* **Self-Healing**: WebSocket workers feature automatic reconnection logic to handle stream interruptions
* **Environment-Driven Configuration**: All parameters are managed via environment variables and mapped to a configuration struct in [env.go](stock-interactor/internal/config/env.go)
* **Graceful Shutdown**: The service ensures a clean exit by closing external connections and terminating worker channels properly
* Observability: Integrated [**metrics**](stock-interactor/internal/metrics/collector.go) collection and structured **logging**

```golang
logger := slog.New(pkgLogger.NewPrettyHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelDebug,
	}))

...

if err != nil {
	logger.ErrorContext(ctx, fmt.Sprintf("Error: %v", err))
}
```

* Robust Error Handling: Errors are **wrapped** with context for better traceability

```golang

import emperror "emperror.dev/errors"

...

if err != nil {
	return emperror.Wrapf(err, "application.Start")
}
```

<a id="trade_engine"></a>

# Trade-engine

The diagram below illustrates the service's state transitions.

<img src="assets/trade-engine.gif" alt="Demo">

***Click the diagram to activate animation***

Implementing the core logic as a Finite State Machine (FSM) provides an elegant way to represent code with distinct states and transitions, ensuring clarity and predictability.

Key Technical Features

* **State Machine Implementation**: The core classes are organized as an FSM, enabling complex logic while maintaining high readability and testability.
* **Cascading Pattern**: To handle multiple transitions within a single state, a custom "cascades" pattern was implemented. This acts as a specialized form of recursion with a fixed number of re-entrant calls and modified transition logic.

```python
def handle_first(...) -> ...
    ... ## states/transitions logic

    return handle_second(...)

def handle_second(...) -> ...
    ... ## states/transitions logic

    return ...
```

* Extensive [Testing](trade-engine/tests): The test suite utilizes **parameterized tests** that serve as a declarative specification for the codebase.
* **Strategy Pattern**: Following Go-inspired best practices, logic is decoupled through interfaces to ensure modularity.
* **Clean Architecture**: Like the Stock-interactor, the engine follows a strictly layered architecture.
* **Validated Configuration**: Parameters are injected via environment variables and managed through a validated [Config](trade-engine/config/config.py) class.
* **Structured Logging**: Features a configurable LoggerAdapter for detailed console output.

```python
    base_logger = logging.getLogger(cfg.VERSION)
    base_logger.setLevel(logging.INFO)
    base_logger.addHandler(stream_handler)

    logger = logging.LoggerAdapter(base_logger, {"engine_id": cfg.VERSION})

    ...

    self.logger.info(
                    "%s | %s -> (%s) -> %s",
                    last_close_time,
                    source.id,
                    event,
                    self.current_state.id,
                )
```

* **Observability & Performance**: Logs and trade statistics are persisted in Grafana via a [**Metric Repository**](trade-engine/services/metric_repository/clickhouse_metric_repository.py). To meet strict [**timing requirements**](#timing_requirements), the repository operates in **asynchronous** mode.
* **Historical Backtesting**: The engine includes a [backtesting module](trade-engine/services/tester/) to verify profitability. It fetches historical data for a specified interval and replays the candles through the FSM to generate performance reports in Grafana.

<a id="logging_and_monitoring"></a>
# Logging and monitoring
The system uses Grafana to visualize service operations and trading performance. Data is aggregated from two primary sources: Prometheus and ClickHouse.

Trade Visualization Example:
<img src="assets/trades.jpg">

Clicking on a specific trade displays the processed candles or associated logs.

Candlestick Chart Example:
<img src="assets/candles.jpg">

Log View Example:
<img src="assets/logs.jpg">

<a id="candle"></a>

# Candle

A candlestick (or trading candle) is a compact representation of price action over a specific time interval.

<img src="assets/candle.png">

* High: The maximum price reached.
* Low: The minimum price reached.
* Open: The price at the start of the interval.
* Close: The price at the end of the interval.

If Open < Close, it is a Bullish candle (typically green).

If Open > Close, it is a Bearish candle (typically red).

<a id="trading_strategy"></a>

# Trading strategy

A set of predefined rules designed to answer the following core questions:

* Market Definition: Which market, asset, and timeframe are being traded?
* Entry Signals: What conditions trigger a trade? Which signals should be ignored?
* Position Sizing & Parameters: What is the order type, entry price, and volume? Where are the Stop-Loss and Take-Profit levels?
* Trade Management: Should the position remain open? What is the exit signal?
* Loss Management: When should trading be suspended? Is a re-entry required?

Without a strategy, long-term profitability is nearly impossible. With a strategy, the primary challenge is the discipline to follow it consistently.

<a id="risk_management"></a>

# Risk management

Every trade is protected by a Stop-Loss — a price level where the trade's logic is invalidated and the position is closed at a loss.

The engine enforces a strict rule: each trade is capped at a 0.5% loss of the total account equity.

This fundamental rule ensures long-term survival, allowing the system to withstand a series of losing trades without blowing the account.

Example: The Compounding Effect of Losses

Suppose the system encounters a losing streak:

* 1st loss: Account drops by 0.5%.
* 2nd loss: The 0.5% risk is calculated from the new balance. The loss is 0.4975%. Total drawdown: 0.9975%.
* 10th loss: The loss is 0.478%. Total cumulative drawdown: 4.889%.
* 100th loss: Total cumulative drawdown: 39.35%.

In other words, even an improbable streak of 100 consecutive losses will not result in a total loss of capital.
