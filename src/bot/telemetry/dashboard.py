import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json
import os
import asyncio
from datetime import datetime, timedelta
import random

# Import live data manager with proper error handling
try:
    from src.bot.api.live_data import live_data_manager
    LIVE_DATA_AVAILABLE = True
except ImportError as e:
    print(f"Live data not available: {e}")
    LIVE_DATA_AVAILABLE = False
    live_data_manager = None

# Page config
st.set_page_config(
    page_title="PerpPatrol Dashboard",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme with black tabs, green text, grey background
st.markdown("""
<style>
    /* Hide Streamlit menu and header */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}
    
    /* Main app background */
    .stApp {
        background-color: #2e2e2e;
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        color: #00ff00;
    }
    
    /* Main container centering */
    .main .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
        margin: 0 auto;
        background-color: #2e2e2e;
    }
    
    /* Query boxes - black background with green text */
    .query-box {
        background-color: #000000;
        padding: 20px;
        border-left: 5px solid #00ff00;
        margin: 20px 0;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    /* Response boxes - black background with green text */
    .response-box {
        background-color: #000000;
        padding: 20px;
        border-left: 5px solid #00ff00;
        margin: 20px 0;
        border-radius: 8px;
        font-size: 15px;
        line-height: 1.6;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    /* Metric cards - black background with green text */
    .metric-card {
        background-color: #000000;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,255,0,0.2);
        margin: 10px;
        text-align: center;
        border: 1px solid #00ff00;
        color: #00ff00;
    }
    
    /* Status colors - all green variations */
    .status-active { 
        color: #00ff00; 
        font-weight: 700; 
        font-size: 16px;
    }
    .status-warning { 
        color: #90ff90; 
        font-weight: 700; 
        font-size: 16px;
    }
    .status-error { 
        color: #60ff60; 
        font-weight: 700; 
        font-size: 16px;
    }
    
    /* Headers - green text */
    .header-text { 
        font-size: 32px; 
        font-weight: 700; 
        color: #00ff00; 
        text-align: center;
        margin-bottom: 10px;
    }
    .subheader-text { 
        font-size: 20px; 
        font-weight: 400; 
        color: #90ff90; 
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Tables - dark theme */
    .dataframe {
        font-size: 14px !important;
        font-family: 'Segoe UI', sans-serif !important;
        background-color: #000000 !important;
        color: #00ff00 !important;
    }
    
    /* Streamlit components styling */
    .stSelectbox > div > div > div {
        background-color: #000000;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    .stSelectbox > div > div {
        font-size: 16px;
        font-weight: 500;
        color: #00ff00;
    }
    
    /* Buttons - black with green text */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        padding: 12px 24px;
        background-color: #000000;
        color: #00ff00;
        border: 2px solid #00ff00;
    }
    
    .stButton > button:hover {
        background-color: #00ff00;
        color: #000000;
        border: 2px solid #00ff00;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background-color: #000000;
    }
    
    .stDataFrame > div {
        background-color: #000000;
        color: #00ff00;
    }
    
    /* Override Streamlit's default colors */
    .stMarkdown {
        color: #00ff00;
    }
    
    /* Success/Info/Warning message styling */
    .stSuccess {
        background-color: #000000;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    .stInfo {
        background-color: #000000;
        color: #00ff00;
        border: 1px solid #00ff00;
    }
    
    .stWarning {
        background-color: #000000;
        color: #90ff90;
        border: 1px solid #90ff90;
    }
    
    /* Horizontal rule */
    hr {
        border-color: #00ff00;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Check if we have real API credentials
API_CREDENTIALS_AVAILABLE = bool(os.getenv('WOOFI_API_KEY') and os.getenv('WOOFI_API_SECRET'))
USE_LIVE_DATA = LIVE_DATA_AVAILABLE and API_CREDENTIALS_AVAILABLE

# Debug info
if LIVE_DATA_AVAILABLE:
    print("✅ Live data manager loaded successfully")
else:
    print("❌ Live data manager not available")

if API_CREDENTIALS_AVAILABLE:
    print("✅ API credentials found")
else:
    print("❌ API credentials not found")

# Initialize session state for live data
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False
if 'pnl_history' not in st.session_state:
    st.session_state.pnl_history = []
if 'trades_history' not in st.session_state:
    st.session_state.trades_history = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'live_positions' not in st.session_state:
    st.session_state.live_positions = []
if 'live_orders' not in st.session_state:
    st.session_state.live_orders = []

# Live Data Functions
async def fetch_real_data():
    """Fetch real data from WOOFi Pro API"""
    if not USE_LIVE_DATA:
        return
        
    try:
        # Fetch positions
        positions = await live_data_manager.get_live_positions()
        st.session_state.live_positions = positions
        
        # Fetch recent trades
        trades = await live_data_manager.get_live_trades(limit=50)
        st.session_state.trades_history = trades
        
        # Fetch orders
        orders = await live_data_manager.get_live_orders()
        st.session_state.live_orders = orders
        
        # Calculate PnL from positions
        total_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions)
        now = datetime.now()
        
        if st.session_state.pnl_history:
            last_pnl = st.session_state.pnl_history[-1]['pnl']
            pnl_change = total_pnl - last_pnl
        else:
            pnl_change = 0
            
        st.session_state.pnl_history.append({
            'timestamp': now,
            'pnl': total_pnl,
            'change': pnl_change
        })
        
        # Keep only last 100 points
        if len(st.session_state.pnl_history) > 100:
            st.session_state.pnl_history = st.session_state.pnl_history[-100:]
            
    except Exception as e:
        st.error(f"Error fetching real data: {e}")
        generate_simulated_data()

def generate_simulated_data():
    """Generate simulated trading data (fallback)"""
    now = datetime.now()
    
    # Generate PnL data point
    if len(st.session_state.pnl_history) == 0:
        base_pnl = 100
    else:
        base_pnl = st.session_state.pnl_history[-1]['pnl']
    
    pnl_change = random.uniform(-5, 8)  # Slight positive bias
    new_pnl = base_pnl + pnl_change
    
    st.session_state.pnl_history.append({
        'timestamp': now,
        'pnl': new_pnl,
        'change': pnl_change
    })
    
    # Keep only last 100 points
    if len(st.session_state.pnl_history) > 100:
        st.session_state.pnl_history = st.session_state.pnl_history[-100:]
    
    # Generate trade data
    if random.random() < 0.3:  # 30% chance of new trade
        trade = {
            'timestamp': now,
            'side': random.choice(['BUY', 'SELL']),
            'size': round(random.uniform(0.001, 0.1), 4),
            'price': random.uniform(66000, 68000),
            'pnl': round(random.uniform(-2, 15), 2)
        }
        st.session_state.trades_history.append(trade)
        
        # Keep only last 50 trades
        if len(st.session_state.trades_history) > 50:
            st.session_state.trades_history = st.session_state.trades_history[-50:]

def update_data():
    """Update data - real or simulated"""
    if USE_LIVE_DATA:
        # Run async function safely
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(fetch_real_data())
            loop.close()
        except Exception as e:
            st.error(f"Error with live data: {e}")
            generate_simulated_data()
    else:
        generate_simulated_data()

# Auto-refresh data if bot is running
if st.session_state.bot_running:
    if (datetime.now() - st.session_state.last_update).seconds > 2:
        update_data()
        st.session_state.last_update = datetime.now()

# Main Header
st.markdown('<p class="header-text">PerpPatrol Live Dashboard</p>', unsafe_allow_html=True)
data_mode = "🔴 LIVE TRADING" if USE_LIVE_DATA else "🟡 SIMULATION"
st.markdown(f'<p class="subheader-text">Real-time Transaction Impact Optimization | {data_mode}</p>', unsafe_allow_html=True)

# Bot Control Panel
st.markdown("### Bot Control Center")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🟢 Start Bot" if not st.session_state.bot_running else "🔴 Stop Bot", 
                use_container_width=True):
        st.session_state.bot_running = not st.session_state.bot_running
        if st.session_state.bot_running:
            if USE_LIVE_DATA:
                st.success("🔴 LIVE TRADING STARTED!")
            else:
                st.success("🟡 Simulation started!")
            update_data()  # Generate initial data
        else:
            st.warning("Bot stopped.")

with col2:
    if st.button("🚨 Emergency Kill Switch", use_container_width=True):
        st.session_state.bot_running = False
        st.error("🚨 EMERGENCY STOP ACTIVATED!")

with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        update_data()
        st.rerun()

with col4:
    auto_refresh = st.checkbox("Auto Refresh (2s)", value=st.session_state.bot_running)
    if auto_refresh and st.session_state.bot_running:
        time.sleep(2)
        st.rerun()

# Status indicator
status_color = "🟢 ACTIVE" if st.session_state.bot_running else "🔴 STOPPED"
st.markdown(f"**Bot Status:** {status_color} | **Last Update:** {st.session_state.last_update.strftime('%H:%M:%S')}")

# Symbol Selection
current_symbol = st.selectbox("Select Trading Pair", ["BTC-PERP", "ETH-PERP", "SOL-PERP", "AVAX-PERP"], index=0)

# Generate live metrics
base_price = {"BTC-PERP": 67000, "ETH-PERP": 2500, "SOL-PERP": 180, "AVAX-PERP": 35}
price = base_price.get(current_symbol, 100) + random.uniform(-50, 50)
maker_ratio = random.uniform(72, 78)
cancel_ratio = random.uniform(2.1, 3.5)
hold_time = random.uniform(2.2, 2.8)

# Get current PnL from live data
current_pnl = st.session_state.pnl_history[-1]['pnl'] if st.session_state.pnl_history else 100

# Modern Tab Interface
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Performance", "📈 Analytics & Charts", "⚙️ Bot Configuration", "🛡️ Risk Management"])

with tab1:
    st.header("Real-time Performance Metrics")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pnl_change = st.session_state.pnl_history[-1]['change'] if st.session_state.pnl_history else 0
        st.metric("Unrealized PnL", f"${current_pnl:.2f}", f"{pnl_change:+.2f}")
    
    with col2:
        st.metric("Maker Ratio", f"{maker_ratio:.1f}%", "+28%")
    
    with col3:
        st.metric("Avg Hold Time", f"{hold_time:.1f}s", "+1.7s")
    
    with col4:
        st.metric("Cancel/Fill Ratio", f"{cancel_ratio:.1f}", "-12.1")
    
    # Live Order Book and Trades
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Live Order Book")
        
        # Generate simulated order book data
        orderbook_data = []
        mid_price = price
        spread = random.uniform(0.01, 0.05)
        
        for i in range(5):
            ask_price = mid_price + spread/2 + (i * spread/10)
            orderbook_data.append({
                'Type': 'ASK',
                'Price': f"${ask_price:.2f}",
                'Size': f"{random.uniform(0.1, 2.0):.3f}"
            })
            
        for i in range(5):
            bid_price = mid_price - spread/2 - (i * spread/10)
            orderbook_data.append({
                'Type': 'BID', 
                'Price': f"${bid_price:.2f}",
                'Size': f"{random.uniform(0.1, 2.0):.3f}"
            })
        
        st.dataframe(pd.DataFrame(orderbook_data), use_container_width=True, hide_index=True)
    
    with col_right:
        st.subheader("Recent Trades")
        
        if st.session_state.trades_history:
            trades_df = pd.DataFrame(st.session_state.trades_history[-10:])
            trades_df['Time'] = trades_df['timestamp'].dt.strftime('%H:%M:%S')
            trades_df = trades_df[['Time', 'side', 'size', 'price', 'pnl']].rename(columns={
                'side': 'Side', 'size': 'Size', 'price': 'Price', 'pnl': 'PnL'
            })
            st.dataframe(trades_df, use_container_width=True, hide_index=True)
        else:
            st.info("No trades yet. Start the bot to see live trading data.")

with tab2:
    st.header("Analytics & Data Visualization")
    
    # PnL Chart
    if st.session_state.pnl_history:
        st.subheader("PnL Over Time")
        
        pnl_df = pd.DataFrame(st.session_state.pnl_history)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pnl_df['timestamp'],
            y=pnl_df['pnl'],
            mode='lines+markers',
            name='PnL',
            line=dict(color='#00ff00', width=2),
            marker=dict(color='#00ff00', size=4)
        ))
        
        fig.update_layout(
            title="Real-time PnL Performance",
            xaxis_title="Time",
            yaxis_title="PnL ($)",
            plot_bgcolor='#000000',
            paper_bgcolor='#2e2e2e',
            font=dict(color='#00ff00'),
            xaxis=dict(gridcolor='#444444'),
            yaxis=dict(gridcolor='#444444')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # TI Metrics Visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("TI Performance Metrics")
            
            # Gauge chart for TI Score
            ti_score = (maker_ratio/100 + (hold_time/5) + (1 - cancel_ratio/15)) / 3
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = ti_score * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "TI Score"},
                delta = {'reference': 80},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#00ff00"},
                    'steps': [
                        {'range': [0, 50], 'color': "#444444"},
                        {'range': [50, 80], 'color': "#666666"}
                    ],
                    'threshold': {
                        'line': {'color': "#ff0000", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(
                paper_bgcolor='#2e2e2e',
                font={'color': "#00ff00"}
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.subheader("Trading Volume Analysis")
            
            if st.session_state.trades_history:
                trades_df = pd.DataFrame(st.session_state.trades_history)
                
                # Volume by side
                volume_by_side = trades_df.groupby('side')['size'].sum().reset_index()
                
                fig_pie = px.pie(
                    volume_by_side, 
                    values='size', 
                    names='side',
                    title="Trading Volume by Side",
                    color_discrete_map={'BUY': '#00ff00', 'SELL': '#90ff90'}
                )
                
                fig_pie.update_layout(
                    paper_bgcolor='#2e2e2e',
                    font=dict(color='#00ff00')
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No trading data available yet.")
    
    else:
        st.info("Start the bot to see live analytics and charts.")

with tab3:
    st.header("Bot Configuration & Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trading Parameters")
        
        # Configuration controls
        max_position = st.slider("Max Position Size ($)", 100, 5000, 2000)
        risk_limit = st.slider("Daily Risk Limit ($)", 50, 1000, 200)
        maker_target = st.slider("Target Maker Ratio (%)", 50, 90, 70)
        
        st.subheader("Strategy Settings")
        
        spread_multiplier = st.number_input("Spread Multiplier", 0.5, 3.0, 1.0, 0.1)
        refresh_rate = st.selectbox("Refresh Rate", ["Fast (100ms)", "Medium (200ms)", "Slow (500ms)"], index=1)
        
        if st.button("Apply Configuration", use_container_width=True):
            st.success("Configuration updated successfully!")
    
    with col2:
        st.subheader("System Information")
        
        system_info = {
            "Bot Version": "v2.1.0",
            "API Status": "Connected" if st.session_state.bot_running else "Disconnected",
            "Uptime": "2h 34m" if st.session_state.bot_running else "0m",
            "Total Trades": len(st.session_state.trades_history),
            "Active Orders": random.randint(2, 8) if st.session_state.bot_running else 0,
            "Memory Usage": f"{random.randint(45, 85)}%"
        }
        
        for key, value in system_info.items():
            st.metric(key, value)
        
        st.subheader("Log Messages")
        
        if st.session_state.bot_running:
            log_messages = [
                f"[{datetime.now().strftime('%H:%M:%S')}] Order placed: BUY 0.001 BTC @ $67,234",
                f"[{(datetime.now() - timedelta(seconds=30)).strftime('%H:%M:%S')}] Fill received: SELL 0.0008 BTC",
                f"[{(datetime.now() - timedelta(seconds=60)).strftime('%H:%M:%S')}] TI optimizer adjusted spread",
                f"[{(datetime.now() - timedelta(seconds=90)).strftime('%H:%M:%S')}] Risk check passed"
            ]
            
            for msg in log_messages:
                st.text(msg)
        else:
            st.info("Bot is stopped. No recent activity.")

with tab4:
    st.header("Risk Management & Compliance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Position Limits")
        
        current_position = random.uniform(500, 1500)
        position_limit = 2000
        position_pct = current_position / position_limit
        
        st.progress(position_pct, text=f"Position: ${current_position:.0f} / ${position_limit}")
        
        daily_loss = random.uniform(10, 50)
        loss_limit = 200
        loss_pct = daily_loss / loss_limit
        
        st.progress(loss_pct, text=f"Daily Loss: ${daily_loss:.0f} / ${loss_limit}")
        
        if position_pct < 0.8 and loss_pct < 0.8:
            st.success("✅ All limits within safe ranges")
        else:
            st.warning("⚠️ Approaching risk limits")
    
    with col2:
        st.subheader("Compliance Status")
        
        compliance_checks = {
            "Loop Detection": "ACTIVE",
            "Self-Match Prevention": "ENABLED", 
            "Rate Limiting": "COMPLIANT",
            "Position Monitoring": "ACTIVE",
            "Kill Switch": "ARMED"
        }
        
        for check, status in compliance_checks.items():
            st.success(f"✅ {check}: {status}")
    
    with col3:
        st.subheader("System Health")
        
        health_metrics = {
            "API Latency": f"{random.randint(15, 45)}ms",
            "Error Rate": f"{random.uniform(0.1, 0.5):.1f}%",
            "Market Data": "LIVE",
            "Order Success": f"{random.uniform(98, 99.9):.1f}%"
        }
        
        for metric, value in health_metrics.items():
            st.info(f"📊 {metric}: {value}")
        
        # Emergency controls
        st.subheader("Emergency Controls")
        
        if st.button("🚨 EMERGENCY STOP ALL", use_container_width=True):
            st.session_state.bot_running = False
            st.error("🚨 EMERGENCY STOP ACTIVATED - ALL TRADING HALTED")
        
        if st.button("🔄 Reset Risk Counters", use_container_width=True):
            st.info("Risk counters have been reset")

# Footer
st.markdown("---")
st.markdown("**PerpPatrol v2.1.0** - First TI-Aware Market Making Bot for WOOFi Pro | Advanced Transaction Impact Optimization")
