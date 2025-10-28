import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="PerpPatrol - TI-Aware Market Making Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-good { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-danger { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🎯 PerpPatrol Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">TI-Aware Market Making Bot for WOOFi Pro</p>', unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("🎛️ Bot Controls")

# Bot status simulation
bot_status = st.sidebar.selectbox("Bot Status", ["🟢 Running", "🟡 Paused", "🔴 Stopped"], index=0)
trading_mode = st.sidebar.selectbox("Trading Mode", ["🔴 Live Trading", "🟡 Simulation"], index=1)

st.sidebar.markdown("---")
st.sidebar.header("📊 Configuration")

# Configuration controls
symbol = st.sidebar.selectbox("Symbol", ["BTC-PERP", "ETH-PERP", "SOL-PERP"], index=0)
base_size = st.sidebar.slider("Base Order Size", 0.001, 0.1, 0.001, 0.001)
max_inventory = st.sidebar.slider("Max Inventory (USD)", 100, 5000, 1000, 100)
refresh_rate = st.sidebar.slider("Refresh Rate (ms)", 200, 2000, 400, 100)

# Main dashboard
col1, col2, col3, col4 = st.columns(4)

# Generate mock real-time data
current_time = datetime.now()

# Mock metrics
with col1:
    st.metric("💰 Unrealized PnL", "$127.45", "12.3%", delta_color="normal")
    st.metric("📈 Total Trades", "1,247", "23")

with col2:
    st.metric("🎯 Maker Ratio", "73.2%", "2.1%", delta_color="normal")
    st.metric("⚡ Avg Fill Time", "2.3s", "-0.2s", delta_color="inverse")

with col3:
    st.metric("🛡️ Risk Score", "Low", "Stable", delta_color="off")
    st.metric("📊 Active Orders", "2", "0")

with col4:
    st.metric("🔄 Cancel/Fill Ratio", "3.2", "-0.8", delta_color="inverse")
    st.metric("💎 Inventory", "$234", "+$45")

# Charts section
st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 PnL Performance")
    
    # Generate mock PnL data
    dates = pd.date_range(start=current_time - timedelta(hours=24), end=current_time, freq='5min')
    pnl_data = np.cumsum(np.random.randn(len(dates)) * 2) + 100
    
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(
        x=dates, 
        y=pnl_data,
        mode='lines',
        name='Cumulative PnL',
        line=dict(color='#1f77b4', width=2)
    ))
    fig_pnl.update_layout(
        title="24h PnL Trajectory",
        xaxis_title="Time",
        yaxis_title="PnL (USD)",
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig_pnl, use_container_width=True)

with col_right:
    st.subheader("🎯 TI Metrics")
    
    # TI metrics gauge
    fig_ti = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=("Maker Ratio", "Holding Time", "Slippage", "Cancel Ratio")
    )
    
    # Maker ratio gauge
    fig_ti.add_trace(go.Indicator(
        mode="gauge+number",
        value=73.2,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Maker %"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkblue"},
               'steps': [{'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 70}}
    ), row=1, col=1)
    
    fig_ti.update_layout(height=400)
    st.plotly_chart(fig_ti, use_container_width=True)

# Order book visualization
st.markdown("---")
st.subheader("📚 Live Order Book")

col_ob_left, col_ob_right = st.columns(2)

with col_ob_left:
    st.markdown("**🔴 Asks (Sell Orders)**")
    asks_data = {
        'Price': [100.25, 100.24, 100.23, 100.22, 100.21],
        'Size': [0.5, 1.2, 0.8, 2.1, 1.5],
        'Total': [0.5, 1.7, 2.5, 4.6, 6.1]
    }
    asks_df = pd.DataFrame(asks_data)
    st.dataframe(asks_df, use_container_width=True)

with col_ob_right:
    st.markdown("**🟢 Bids (Buy Orders)**")
    bids_data = {
        'Price': [100.20, 100.19, 100.18, 100.17, 100.16],
        'Size': [1.1, 0.9, 1.8, 0.7, 2.3],
        'Total': [1.1, 2.0, 3.8, 4.5, 6.8]
    }
    bids_df = pd.DataFrame(bids_data)
    st.dataframe(bids_df, use_container_width=True)

# Recent trades
st.markdown("---")
st.subheader("📋 Recent Trades")

trades_data = {
    'Time': [
        current_time - timedelta(seconds=30),
        current_time - timedelta(seconds=45),
        current_time - timedelta(seconds=67),
        current_time - timedelta(seconds=89),
        current_time - timedelta(seconds=120)
    ],
    'Symbol': ['BTC-PERP', 'BTC-PERP', 'BTC-PERP', 'BTC-PERP', 'BTC-PERP'],
    'Side': ['Buy', 'Sell', 'Buy', 'Sell', 'Buy'],
    'Price': [100.21, 100.23, 100.19, 100.25, 100.18],
    'Size': [0.001, 0.002, 0.001, 0.0015, 0.001],
    'Type': ['Maker', 'Maker', 'Maker', 'Maker', 'Maker'],
    'PnL': ['+$2.34', '+$1.87', '+$3.21', '+$2.95', '+$1.76']
}

trades_df = pd.DataFrame(trades_data)
st.dataframe(trades_df, use_container_width=True)

# Risk monitoring
st.markdown("---")
st.subheader("🛡️ Risk Monitoring")

col_risk1, col_risk2, col_risk3 = st.columns(3)

with col_risk1:
    st.markdown("**Position Limits**")
    st.progress(0.23, text="23% of max inventory")
    st.progress(0.15, text="15% of daily loss limit")

with col_risk2:
    st.markdown("**Compliance Status**")
    st.success("✅ Loop detection: Active")
    st.success("✅ Self-match protection: Active")
    st.success("✅ Rate limiting: Within bounds")

with col_risk3:
    st.markdown("**Kill Switches**")
    st.info("🟢 All systems operational")
    st.info("🟢 Market data: Live")
    st.info("🟢 API connection: Stable")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🏆 <strong>PerpPatrol</strong> - Built for DeFrenz x WOO x GoMining Hackathon</p>
    <p>Real-time TI-aware market making with advanced risk management</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if st.sidebar.button("🔄 Refresh Data"):
    st.experimental_rerun()

# Auto-refresh every 5 seconds
time.sleep(0.1)  # Small delay to prevent too frequent updates
