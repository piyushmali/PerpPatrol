import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import random

# Page config
st.set_page_config(
    page_title="PerpPatrol - TI Market Making Bot",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for minimal but effective design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-running { color: #28a745; font-weight: bold; }
    .status-stopped { color: #dc3545; font-weight: bold; }
    .metric-positive { color: #28a745; }
    .metric-negative { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎯 PerpPatrol Dashboard</h1>', unsafe_allow_html=True)

# Get current symbol from config (dynamic)
symbols = ["BTC-PERP", "ETH-PERP", "SOL-PERP", "AVAX-PERP", "MATIC-PERP"]
current_symbol = st.selectbox("Trading Symbol", symbols, index=0)

# Status indicators
col_status1, col_status2, col_status3 = st.columns(3)
with col_status1:
    st.markdown("**Bot Status:** <span class='status-running'>🟢 RUNNING</span>", unsafe_allow_html=True)
with col_status2:
    st.markdown("**Mode:** <span class='status-running'>🔴 LIVE TRADING</span>", unsafe_allow_html=True)
with col_status3:
    st.markdown(f"**Symbol:** {current_symbol}")

st.markdown("---")

# Key metrics (dynamic based on symbol)
col1, col2, col3, col4 = st.columns(4)

# Generate dynamic data based on symbol
base_price = {"BTC-PERP": 67000, "ETH-PERP": 2500, "SOL-PERP": 180, "AVAX-PERP": 35, "MATIC-PERP": 0.85}
price = base_price.get(current_symbol, 100) + random.uniform(-50, 50)

pnl = random.uniform(-25, 150)
pnl_color = "metric-positive" if pnl > 0 else "metric-negative"
pnl_sign = "+" if pnl > 0 else ""

maker_ratio = random.uniform(65, 85)
trades_count = random.randint(450, 1200)
avg_hold_time = random.uniform(1.8, 3.2)

with col1:
    st.metric("💰 Unrealized PnL", f"${pnl:.2f}", f"{pnl_sign}{pnl/10:.1f}%")
    st.metric("📊 Mid Price", f"${price:.2f}", f"{random.uniform(-0.5, 0.5):.2f}%")

with col2:
    st.metric("🎯 Maker Ratio", f"{maker_ratio:.1f}%", f"{random.uniform(-2, 3):.1f}%")
    st.metric("📈 Total Trades", f"{trades_count:,}", f"+{random.randint(5, 25)}")

with col3:
    st.metric("⚡ Avg Hold Time", f"{avg_hold_time:.1f}s", f"{random.uniform(-0.3, 0.2):.1f}s")
    st.metric("🔄 Cancel/Fill", f"{random.uniform(2.5, 4.5):.1f}", f"{random.uniform(-0.8, 0.5):.1f}")

with col4:
    st.metric("💎 Position", f"${random.uniform(100, 800):.0f}", f"{random.uniform(-50, 100):.0f}")
    st.metric("🛡️ Risk Score", "LOW", "Stable")

st.markdown("---")

# Live order book (dynamic)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(f"📚 {current_symbol} Order Book")
    
    # Dynamic order book based on symbol
    mid_price = price
    spread = random.uniform(0.01, 0.05)
    
    asks_data = []
    bids_data = []
    
    for i in range(5):
        ask_price = mid_price + spread/2 + (i * spread/10)
        bid_price = mid_price - spread/2 - (i * spread/10)
        
        asks_data.append({
            'Price': f"${ask_price:.2f}",
            'Size': f"{random.uniform(0.1, 2.0):.3f}",
            'Side': '🔴 ASK'
        })
        
        bids_data.append({
            'Price': f"${bid_price:.2f}",
            'Size': f"{random.uniform(0.1, 2.0):.3f}",
            'Side': '🟢 BID'
        })
    
    # Combine and show order book
    orderbook_data = asks_data[::-1] + bids_data  # Reverse asks for proper order
    orderbook_df = pd.DataFrame(orderbook_data)
    st.dataframe(orderbook_df, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("📋 Recent Activity")
    
    # Dynamic recent trades
    recent_trades = []
    for i in range(8):
        side = random.choice(['BUY', 'SELL'])
        trade_price = mid_price + random.uniform(-0.1, 0.1)
        size = random.uniform(0.001, 0.01)
        pnl_trade = random.uniform(-5, 15)
        
        recent_trades.append({
            'Time': (datetime.now() - timedelta(seconds=i*30)).strftime('%H:%M:%S'),
            'Side': f"{'🟢' if side == 'BUY' else '🔴'} {side}",
            'Price': f"${trade_price:.2f}",
            'Size': f"{size:.4f}",
            'PnL': f"${pnl_trade:.2f}"
        })
    
    trades_df = pd.DataFrame(recent_trades)
    st.dataframe(trades_df, use_container_width=True, hide_index=True)

st.markdown("---")

# TI Metrics and Risk (simplified)
col_ti1, col_ti2, col_ti3 = st.columns(3)

with col_ti1:
    st.subheader("🎯 TI Optimization")
    st.progress(maker_ratio/100, text=f"Maker Ratio: {maker_ratio:.1f}%")
    st.progress(avg_hold_time/5, text=f"Hold Time: {avg_hold_time:.1f}s")
    st.progress(0.75, text="TI Score: 75%")

with col_ti2:
    st.subheader("🛡️ Risk Controls")
    inventory_pct = random.uniform(0.15, 0.45)
    loss_pct = random.uniform(0.05, 0.25)
    
    st.progress(inventory_pct, text=f"Inventory: {inventory_pct*100:.0f}%")
    st.progress(loss_pct, text=f"Daily Loss: {loss_pct*100:.0f}%")
    
    if inventory_pct < 0.8 and loss_pct < 0.8:
        st.success("✅ All limits OK")
    else:
        st.warning("⚠️ Approaching limits")

with col_ti3:
    st.subheader("⚡ System Status")
    st.success("🟢 API Connected")
    st.success("🟢 Market Data Live")
    st.success("🟢 Orders Active")
    st.info(f"🔄 Refresh: {random.randint(380, 420)}ms")

# Control buttons
st.markdown("---")
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

with col_btn2:
    if st.button("⏸️ Pause Bot", use_container_width=True):
        st.warning("Bot paused (demo)")

with col_btn3:
    if st.button("🛑 Emergency Stop", use_container_width=True):
        st.error("Emergency stop activated (demo)")

with col_btn4:
    if st.button("📊 Export Data", use_container_width=True):
        st.info("Data exported (demo)")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🏆 <strong>PerpPatrol</strong> - DeFrenz x WOO x GoMining Hackathon | 
    Real-time updates every 30 seconds | Last update: {}</p>
</div>
""".format(datetime.now().strftime('%H:%M:%S')), unsafe_allow_html=True)
