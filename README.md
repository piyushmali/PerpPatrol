# PerpPatrol — TI‑Aware Perp Market‑Making Bot (WOOFi Pro)

A production‑ready, compliance‑first trading bot designed for the **WOOFi ✖ DeFrens ✖ GoMining — Trading‑Bot Competition**.
It implements an inventory‑aware quoting strategy with adaptive risk controls, comprehensive compliance layer,
and TI-optimized execution. The bot includes a simple simulator, tests, and a telemetry dashboard.

> Milestones covered: **M1 Safe MM skeleton**, **M2 Quality & Risk**, **M3 TI Tuning & Multi‑Market**

---

## Features at a glance
- Inventory‑aware quoting with volatility‑adaptive widths and order‑book imbalance skew
- Maker‑first execution with queue‑aware placement and throttled cancel/replace
- Risk layer: per‑symbol and portfolio limits, PnL guards, VAR cap, kill‑switches
- Compliance layer: self‑match prevention, loop detector, rate/health discipline
- TI proxy metrics: maker ratio, holding time, slippage vs mid, spread at fill, cancel/fill, distinct counterparties
- Simulator & backtests for quick iteration; Streamlit dashboard for live metrics
- Clean config files for **three milestones** that you can run incrementally

> **Note**: This repository ships with a **reference client** stub for WOOFi Pro. You must
  fill in REST/WebSocket endpoints and authentication per your credentials and the event’s API docs.
  The interfaces are already defined — just implement the TODOs in `woofi_client.py`.

---

## Quickstart

### 1) Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cp config/settings.example.yaml config/settings.yaml
# choose a milestone config (m1/m2/m3) and copy its overrides if you like:
cp config/milestones/m1.yaml config/overrides.yaml
```

### 2) Run simulator (no keys required)
```bash
python -m src.simulator.run_backtest --config config/settings.yaml --overrides config/overrides.yaml
```

### 3) Run live bot (after filling WOOFi client)
```bash
python -m src.bot.app --config config/settings.yaml --overrides config/overrides.yaml
```

### 4) Optional dashboard
```bash
streamlit run src/bot/telemetry/dashboard.py
```

---

## Milestones

- **M1: Safe MM skeleton** — Single‑symbol quoting, basic inventory cap, throttled amends, hard self‑match block, simple logging.
- **M2: Quality & Risk** — Volatility‑aware widths, imbalance skew, funding bias, loss limits, VAR cap, kill‑switch matrix, TI proxy panel.
- **M3: TI tuning & Multi‑Market** — Auto‑tuner for width/skew/size/refresh; rotation across 2–4 symbols; Streamlit dashboard polish.

Each milestone has a config file under `config/milestones/` and a short README in `milestones/`.

---

## Repo layout
```
src/
  bot/                     # live trading runtime
    engine/                # quoting, vol, TI optimizer
    execution/             # exchange clients & order executor
    risk/                  # limits, VAR, PnL tracking, kill switches
    compliance/            # self-match, loop detector, rate/health guards
    data/                  # market data streams, order book model
    telemetry/             # metrics + dashboard
    utils/                 # misc helpers
    app.py                 # entry point (live)
    main.py                # wiring
  simulator/               # reproducible backtests
docs/                      # full documentation set
config/                    # settings and milestone overrides
tests/                     # unit tests for critical components
milestones/                # milestone explainers
docker/                    # Dockerfile
```

---

## License
MIT — see `LICENSE`.
