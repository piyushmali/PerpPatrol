# Architecture

## Layers
- Data: WebSocket handlers -> `OrderBook` model -> mid, spread, imbalance.
- Engine: `VolEstimator` (realized vol), `QuoteEngine` (width, skew, size), `TIOPT` (tuning).
- Execution: `Executor` (throttled amends), `WOOFiClient` (REST/WS), idempotent order ids.
- Risk: limits, VAR, PnL, drawdown step‑downs, funding budgets.
- Compliance: self‑match prevent, loop detector, rate discipline.
- Telemetry: Prometheus metrics + Streamlit dashboard.

## Flow
MarketData -> QuoteEngine -> PreTradeChecks (Risk+Compliance) -> Executor -> Metrics -> Tuning.
