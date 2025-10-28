# Technical Implementation Guide

## 🏗️ System Architecture

### Data Flow
```
Market Data → Quote Engine → Risk Checks → Compliance → Execution → Metrics → TI Tuning
```

### Core Modules

#### 1. Quote Engine (`src/bot/engine/quote_engine.py`)
Generates optimal bid/ask quotes with TI awareness:

```python
def compute_quotes(self, symbol: str, ob: OrderBook, inventory: float) -> Quote:
    mid = ob.mid()
    width = self.cfg["strategy"]["width_vol_mult"] * realized_vol * mid
    
    # TI-aware skewing
    inv_skew = inventory_impact(inventory)
    imb_skew = orderbook_imbalance_impact(ob.imbalance())
    
    return Quote(
        bid_px=mid - width * (1 + skew),
        ask_px=mid + width * (1 - skew),
        bid_sz=optimal_size(mid, "buy"),
        ask_sz=optimal_size(mid, "sell")
    )
```

#### 2. TI Optimizer (`src/bot/engine/ti_optimizer.py`)
Adjusts quotes based on transaction cost metrics:

```python
def nudge(self, symbol, ob, quote, executor):
    maker_ratio = self.metrics.maker_ratio(symbol)
    cancel_per_fill = self.metrics.cancels_per_fill(symbol)
    
    if maker_ratio < target_ratio:
        # Widen spreads to improve maker ratio
        quote.bid_px *= 0.999
        quote.ask_px *= 1.001
    
    if cancel_per_fill > threshold:
        # Reduce refresh frequency
        executor.jitter_up()
    
    return quote
```

#### 3. Risk Manager (`src/bot/risk/limits.py`)
Enforces position and loss limits:

```python
def pretrade_ok(self, symbol: str, quote) -> bool:
    # Position limits
    if abs(self.positions[symbol]) >= self.cfg["risk"]["max_symbol_notional"]:
        return False
    
    # Daily loss limits
    if self.daily_loss >= self.cfg["risk"]["daily_loss_limit_usd"]:
        return False
    
    # Minimum notional check
    if quote.bid_px * quote.bid_sz < min_notional:
        return False
    
    return True
```

#### 4. Compliance Engine (`src/bot/compliance/checks.py`)
Prevents loops and ensures regulatory compliance:

```python
def pretrade_ok(self, symbol, quote) -> bool:
    # Loop detection
    if symbol in self.last_fill_time:
        if not self.loop_detector.ok(self.last_fill_time[symbol], now_ms):
            return False
    
    # Rate limiting
    if self.amend_count[symbol] >= max_amends_per_sec:
        return False
    
    return True
```

## 🔌 WOOFi Pro Integration

### Authentication
Uses ed25519 cryptographic signatures:

```python
def _sign_request(self, timestamp, method, path, body=""):
    message = f"{timestamp}{method.upper()}{path}{body}"
    signature = self.signing_key.sign(message.encode()).signature
    return signature.hex()
```

### API Endpoints
- **REST**: Order management, position queries, account info
- **WebSocket**: Real-time market data, order updates, fills

### Configuration
```yaml
exchange:
  name: woofi_pro
  base_url: https://api.woo.org
  ws_url: wss://wss.woo.org
  api_key: ${WOOFI_API_KEY}
  api_secret: ${WOOFI_API_SECRET}

strategy:
  symbols: ["BTC-PERP"]
  base_order_size: 0.001
  max_inventory_usd: 1000
  maker_bias: 1.0
  refresh_min_ms: 400
  refresh_jitter_ms: 200
  width_vol_mult: 1.5
  inv_skew_strength: 0.4
  imbalance_skew_strength: 0.3
  funding_bias_strength: 0.15
  min_quote_notional: 20

risk:
  max_symbol_notional: 2000
  max_portfolio_var_usd: 150
  daily_loss_limit_usd: 200
  drawdown_step_down: true
  drawdown_step_pct: 0.33

compliance:
  self_match_protect: true
  loop_min_holding_ms: 1500
  max_amends_per_sec: 2

ti_proxy:
  target_maker_ratio: 0.7
  max_slippage_frac: 0.3
  min_avg_holding_ms: 2000
  max_cancel_per_fill: 8

dashboard:
  enabled: true
  host: localhost
  port: 8501
```

## 📊 TI Metrics Implementation

### Maker Ratio Calculation
```python
def maker_ratio(self, symbol: str) -> float:
    total_fills = self._maker_fills[symbol] + self._taker_fills[symbol]
    if total_fills == 0:
        return 0.7  # Default assumption
    return self._maker_fills[symbol] / total_fills
```

### Holding Time Tracking
```python
def record_holding_time(self, symbol: str, holding_time_ms: int):
    self._holding_times[symbol].append(holding_time_ms)
    # Keep rolling window of last 100 fills
    if len(self._holding_times[symbol]) > 100:
        self._holding_times[symbol] = self._holding_times[symbol][-100:]
```

### Cancel/Fill Ratio
```python
def cancels_per_fill(self, symbol: str) -> float:
    fills = self._fills[symbol]
    if fills == 0:
        return 3.0  # Default assumption
    return self._cancels[symbol] / fills
```

## 🛡️ Risk Management Implementation

### Position Tracking
```python
def update_position(self, symbol: str, notional: float):
    self.positions[symbol] = notional
    
    # Check against limits
    max_notional = self.cfg["risk"]["max_symbol_notional"]
    if abs(notional) >= max_notional:
        self.log.warning(f"Position limit approached: {symbol}")
```

### Kill Switch Logic
```python
def tripped(self, executor) -> bool:
    # Error rate monitoring
    if self.error_count > 10 and (now - self.last_error_time) < 60:
        return True
    
    # Market data gap detection
    if now - executor._last_market_update > 30:
        return True
    
    return False
```

## 🔄 Event Loop

### Main Trading Loop
```python
async def run():
    while True:
        for symbol in symbols:
            # Get market data
            ob = md.get_orderbook(symbol)
            if not ob or not ob.ready():
                continue
            
            # Generate quotes
            quotes = quote_engine.compute_quotes(symbol, ob, inventory)
            
            # TI optimization
            quotes = ti_optimizer.nudge(symbol, ob, quotes, executor)
            
            # Risk and compliance checks
            if risk.pretrade_ok(symbol, quotes) and compliance.pretrade_ok(symbol, quotes):
                await executor.sync_quotes(symbol, quotes)
            
            # Collect metrics
            metrics.observe(symbol, ob, executor)
        
        # Kill switch check
        if kill_switches.tripped(executor):
            await executor.flatten_all()
            break
        
        await asyncio.sleep(0.2)  # 200ms cycle
```

## 📈 Performance Optimization

### Throttled Order Management
```python
async def sync_quotes(self, symbol: str, quote):
    now = time.time()
    if now - self._last_amend < self._refresh_min:
        return  # Throttle updates
    
    self._last_amend = now
    
    # Update existing orders or place new ones
    if 'bid' in self._orders[symbol]:
        await self.client.replace(order_id, quote.bid_px, quote.bid_sz)
    else:
        order_id = await self.client.place_limit(symbol, "buy", quote.bid_px, quote.bid_sz)
        self._orders[symbol]['bid'] = order_id
```

### Adaptive Refresh Rates
```python
def jitter_up(self):
    # Increase refresh interval when cancel/fill ratio is high
    self._refresh_min = min(1.5, self._refresh_min * 1.1)
```

## 📊 Dashboard Implementation

### Interactive Dashboard Architecture
The dashboard (`src/bot/telemetry/dashboard.py`) provides a comprehensive 4-tab interface:

```python
# Dashboard launcher with proper path setup
python run_dashboard.py
```

### Dashboard Features

#### Tab 1: Live Performance
- Real-time PnL tracking with Plotly charts
- Live order book visualization
- Recent trades history with filtering
- Multi-asset symbol switching

#### Tab 2: Analytics & Charts
- Interactive PnL performance charts
- TI Score gauge (composite metric)
- Trading volume analysis by side
- Real-time performance metrics

#### Tab 3: Bot Configuration
- Live parameter adjustment sliders
- System information display
- Real-time log message streaming
- Configuration persistence

#### Tab 4: Risk Management
- Position limit progress bars
- Compliance status indicators
- Emergency stop controls
- System health monitoring

### Live Data Integration
```python
# Automatic fallback system
if USE_LIVE_DATA:
    # Real WOOFi Pro API integration
    positions = await live_data_manager.get_live_positions()
    trades = await live_data_manager.get_live_trades()
else:
    # Realistic simulation mode
    generate_simulated_data()
```

### Dashboard Launcher
The `run_dashboard.py` script ensures proper environment setup:

```python
# Automatic Python path configuration
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

# Launch with optimal settings
subprocess.run([
    sys.executable, "-m", "streamlit", "run", 
    "src/bot/telemetry/dashboard.py",
    "--server.port", "8501",
    "--server.headless", "false"
])
```

## 🧪 Testing Framework

### Unit Tests
- Quote engine calculations
- Risk limit enforcement
- Compliance rule validation
- Loop detection logic

### Integration Tests
- WOOFi API connectivity
- Order lifecycle management
- Market data processing
- Error handling

### Dashboard Testing
- Interactive component functionality
- Live data integration
- Chart rendering and updates
- Emergency control validation

### Simulation Testing
```python
# Backtest with historical data
python -m src.simulator.run_backtest --config config/settings.example.yaml

# Stress test with volatility spikes
python -m src.simulator.scenario_vol_spike

# Dashboard demo mode (simulation only)
python run_dashboard.py  # Runs in simulation mode without API keys
```

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (REQUIRED for live trading)
cp .env.example .env
# Edit .env with your credentials

# Launch interactive dashboard (recommended)
python run_dashboard.py

# Alternative: Run bot directly
python -m src.bot.app --config config/settings.example.yaml
```

### Production Deployment

#### Docker Deployment
```bash
# Build and run with Docker
docker build -t perppatrol .
docker run -d --env-file .env -p 8501:8501 perppatrol

# Access dashboard at http://localhost:8501
```

#### Heroku Deployment
```bash
# Deploy to Heroku (configured with Procfile)
git push heroku main

# Set environment variables
heroku config:set WOOFI_API_KEY=your_key
heroku config:set WOOFI_API_SECRET=your_secret
```

#### Local Production
```bash
# Run with production settings
export WOOFI_API_KEY=your_key
export WOOFI_API_SECRET=your_secret
python run_dashboard.py
```

### Configuration Management
- Environment variables for secrets (`.env` file)
- YAML configuration for strategy parameters (`config/settings.example.yaml`)
- Hot-reload capability for parameter tuning
- Dashboard-based configuration interface
- Multiple deployment configurations (local, Docker, Heroku)

---

*Technical implementation optimized for WOOFi Pro and hackathon demonstration*
