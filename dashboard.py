import streamlit as st
import pandas as pd
import pickle
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. SETUP & LOAD
# ==========================================
st.set_page_config(page_title="Eco-Grid AI", layout="wide", page_icon="⚡")

try:
    df = pd.read_csv("eco_grid_data.csv")
    with open('nilm_model.pkl', 'rb') as f:
        model = pickle.load(f)
except:
    st.error("🚨 Error: Run 'data_generator.py' and 'ai_engine.py' first!")
    st.stop()

# CRITICAL: Convert Time to "Real Time" for the Zoom Feature
try:
    df['Datetime'] = pd.to_datetime(df['Time'], format='%H:%M')
except:
    df['Datetime'] = pd.to_datetime(df['Time'])

# ==========================================
# 2. SIDEBAR
# ==========================================
st.sidebar.title("⚡ Eco-Grid Controls")
sim_speed = st.sidebar.slider("Simulation Speed", 0.01, 0.5, 0.05)
auto_scroll = st.sidebar.checkbox("Auto-Scroll Graph", value=True)

peak_start = "18:00"
peak_end = "21:00"

# ==========================================
# 3. MAIN UI
# ==========================================
st.title("Eco-Grid: AI-Driven Energy Monitor")
placeholder = st.empty() # This ensures we replace content instead of stacking it
cost_saved = 0.0

# ==========================================
# 4. SIMULATION LOOP
# ==========================================
for i in range(1, len(df), 5):
    row = df.iloc[i]
    prev_row = df.iloc[i-1]
    
    # --- A. AI PREDICTION (Fixed for Warning) ---
    power_delta = row['Total_Power_W'] - prev_row['Total_Power_W']
    # We wrap the input in a DataFrame so the model stops complaining
    input_df = pd.DataFrame([[power_delta]], columns=['Power_Change'])
    prediction = model.predict(input_df)[0]
    
    # --- B. OPTIMIZATION LOGIC ---
    current_time = row['Time']
    current_power = row['Total_Power_W']
    is_peak = (current_time >= peak_start) and (current_time <= peak_end)
    
    status = "✅ Normal"
    if is_peak and ("AC" in prediction or "Heater" in prediction or "AC" in str(row.get('True_Label', ''))):
        status = f"⚠️ PEAK SHAVING ACTIVE: Paused {prediction}"
        current_power = 0 
        cost_saved += 5.5 
    
    # --- C. UPDATE DISPLAY (Simple View + Pro Graph) ---
    with placeholder.container():
        # 1. Metrics (The Clean Look)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Time", current_time)
        k2.metric("Live Load", f"{int(current_power)} W", delta=int(power_delta))
        k3.metric("AI Detected", prediction)
        k4.metric("Savings", f"₹ {cost_saved:.2f}")
        
        if status != "✅ Normal":
            st.error(status)
        else:
            st.success(f"System Status: Stable | Last Event: {prediction}")

        # 2. The Advanced Graph (Zoomable & Dragging Enabled)
        # We take history up to current point 'i'
        history = df.iloc[:i]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=history['Datetime'], # Using the real datetime column
            y=history['Total_Power_W'],
            mode='lines',
            name='Power',
            line=dict(color='#00CC96', width=2),
            fill='tozeroy'
        ))

        fig.update_layout(
            title="Real-Time Energy Consumption",
            xaxis=dict(
                type="date", 
                rangeslider=dict(visible=True), # This adds the bottom drag bar
            ),
            yaxis=dict(title="Watts", range=[0, 3500]),
            height=450,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # Logic: If Auto-Scroll is ON, force view to last 2 hours.
        # If OFF, you can drag/zoom freely.
        if auto_scroll:
            last_time = history['Datetime'].iloc[-1]
            start_view = last_time - pd.Timedelta(hours=2)
            fig.update_xaxes(range=[start_view, last_time])

        st.plotly_chart(fig, use_container_width=True)
        
    time.sleep(sim_speed)