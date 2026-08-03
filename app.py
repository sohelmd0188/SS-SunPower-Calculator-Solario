import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import math

# ==========================================
# 1. Page Configuration & Custom UI Styling
# ==========================================
# Custom CSS for Modern UI
st.markdown("""
<style>
.main { background-color: #F8FAFC; }

/* Metric Box Styling with Dark Text */
div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    padding: 15px 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #F59E0B;
}

/* Force dark text for metric box */
div[data-testid="stMetric"] * {
    color: #0F172A !important;
}

.stButton>button {
    width: 100%;
    background-color: #F59E0B;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 10px;
}
.stButton>button:hover {
    background-color: #D97706;
    color: white;
}
</style>
""", unsafe_allow_html=True).stButton>button {
    width: 100%;
    background-color: #F59E0B;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 10px;
}
.stButton>button:hover {
    background-color: #D97706;
    color: white;
}
</style>
""", unsafe_allow_html=True)
    .stButton>button {
        width: 100%;
        background-color: #F59E0B;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #D97706;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Header Section
# ==========================================
st.title("☀️ Smart All-in-One Solar App")
st.caption("Calculate household solar load, estimated budget, 24-hour generation curve, and real-time weather-based solar tracking.")

st.markdown("---")

# ==========================================
# 3. Sidebar Inputs (Appliances & Backup)
# ==========================================
st.sidebar.header("🔌 1. Appliance Quantities")
fan_qty = st.sidebar.number_input("Ceiling Fan (75W)", min_value=0, value=5)
light_qty = st.sidebar.number_input("LED Light (15W)", min_value=0, value=10)
fridge_qty = st.sidebar.number_input("Refrigerator (200W)", min_value=0, value=1)
tv_qty = st.sidebar.number_input("Smart TV (80W)", min_value=0, value=1)
oven_qty = st.sidebar.number_input("Oven (1200W)", min_value=0, value=1)
pump_qty = st.sidebar.number_input("1 HP Submersible Pump (750W)", min_value=0, value=1)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ 2. Daily Usage (Hours)")
fan_hours = st.sidebar.slider("Fan (Hours)", 0, 24, 10)
light_hours = st.sidebar.slider("Light (Hours)", 0, 24, 8)
fridge_hours = st.sidebar.slider("Refrigerator (Hours)", 0, 24, 24)
tv_hours = st.sidebar.slider("TV (Hours)", 0, 24, 5)
oven_hours = st.sidebar.slider("Oven (Minutes)", 0, 120, 30) / 60
pump_hours = st.sidebar.slider("Pump (Hours)", 0, 10, 1)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. Solar System Type")
system_type = st.sidebar.radio("Select System Type:", ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"])

# OpenWeatherMap API Key (Set your key here if available)
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

# ==========================================
# 4. Backend Logic & Calculations
# ==========================================
# Total Running Load
running_watts = (fan_qty * 75) + (light_qty * 15) + (fridge_qty * 200) + (tv_qty * 80) + (oven_qty * 1200) + (pump_qty * 750)

# Peak Surge Load (3x surge for motor/compressor loads)
surge_watts = (fan_qty * 75) + (light_qty * 15) + (tv_qty * 80) + (oven_qty * 1200) + (fridge_qty * 200 * 2.5) + (pump_qty * 750 * 3)

# Daily Total Energy Consumption (Watt-Hours)
daily_wh = (fan_qty * 75 * fan_hours) + (light_qty * 15 * light_hours) + \
           (fridge_qty * 200 * 12) + (tv_qty * 80 * tv_hours) + \
           (oven_qty * 1200 * oven_hours) + (pump_qty * 750 * pump_hours)

daily_kwh = daily_wh / 1000

# Required Inverter, Solar Panel & Battery Capacity
inverter_kva = (surge_watts * 1.25) / 1000
solar_kwp = (daily_wh / 4.0 / 0.85) / 1000
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0
battery_ah = (daily_wh * 0.5) / (48 * 0.8) if "With Battery" in system_type else 0

# Cost Estimation (BDT)
panel_cost = (panels_count * 550) * 26

if inverter_kva <= 3.5:
    inverter_cost = 45000
elif inverter_kva <= 5.5:
    inverter_cost = 65000
else:
    inverter_cost = 95000

battery_cost = (battery_ah / 100) * 120000 if "With Battery" in system_type else 0
subtotal = panel_cost + inverter_cost + battery_cost
installation_cost = subtotal * 0.10
total_cost = subtotal + installation_cost

# ==========================================
# 5. Main Dashboard Rendering
# ==========================================

# Top Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load", f"{running_watts} W")
col2.metric("Peak Surge Load", f"{surge_watts:.0f} W")
col3.metric("Daily Usage", f"{daily_kwh:.2f} kWh")
col4.metric("Total Estimated Budget", f"BDT {total_cost:,.0f}")

st.markdown("---")

# Two-Column Layout: Hardware Specs & Cost Summary
c1, c2 = st.columns(2)

with c1:
    st.subheader("📋 Required System Specifications")
    st.info(f"⚡ **Recommended Inverter:** {max(3, round(inverter_kva))} KVA / KW (Hybrid 48V)")
    st.info(f"☀️ **Solar Panels:** {solar_kwp:.2f} kWp (**{panels_count} Units** of 550W Monocrystalline Panels)")
    if "With Battery" in system_type:
        st.info(f"🔋 **Battery Bank:** {battery_ah:.0f} Ah (48V LiFePO4 Lithium Battery)")
    else:
        st.warning("🔋 **Battery Bank:** Not required for On-Grid systems.")

with c2:
    st.subheader("💰 Cost Breakdown (BDT)")
    st.write(f"• **Solar Panels ({panels_count}x 550W):** BDT {panel_cost:,.0f}")
    st.write(f"• **Inverter ({max(3, round(inverter_kva))} KVA):** BDT {inverter_cost:,.0f}")
    if "With Battery" in system_type:
        st.write(f"• **Lithium Battery (48V):** BDT {battery_cost:,.0f}")
    st.write(f"• **Wiring, Mounting & Fitting:** BDT {installation_cost:,.0f}")
    st.markdown("---")
    st.success(f"### **Total Budget: BDT {total_cost:,.0f}**")

st.markdown("---")

# ==========================================
# 6. 24-Hour Solar Generation Plotly Chart
# ==========================================
st.subheader("📊 24-Hour Solar Generation Simulation")

hours = list(range(24))
generation_curve = [0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.85, 0.95, 1.0, 0.98, 0.90, 0.75, 0.5, 0.2, 0.05, 0, 0, 0, 0, 0, 0]
power_output = [solar_kwp * factor for factor in generation_curve]

df_solar = pd.DataFrame({'Time': [f"{h:02d}:00" for h in hours], 'Generation (kW)': power_output})

fig = px.area(
    df_solar, x='Time', y='Generation (kW)',
    title=f"Estimated Daily Solar Power Curve ({solar_kwp:.2f} kWp System)",
    labels={'Generation (kW)': 'Power Output (kW)', 'Time': 'Hour of Day'},
    color_discrete_sequence=['#F59E0B']
)
fig.update_layout(xaxis_title="Time of Day", yaxis_title="Power (kW)", hovermode="x unified", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 7. Live Weather Solar Tracker Section
# ==========================================
st.subheader("🌦️ Live Weather-Based Solar Tracker")

city = st.text_input("Enter City Name:", value="Dhaka")

if st.button("Check Live Solar Output"):
    if API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        st.info("💡 **Simulation Mode:** No OpenWeatherMap API Key provided. Displaying sample weather data below:")
        cloudiness = 25  # 25% sample cloud coverage
        temp = 32
        weather_desc = "Few Clouds"
    else:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            cloudiness = data['clouds']['all']
            temp = data['main']['temp']
            weather_desc = data['weather'][0]['description'].title()
        else:
            st.error("City not found!")
            cloudiness = None

    if cloudiness is not None:
        efficiency = 1.0 - ((cloudiness / 100.0) * 0.80)
        current_kw = solar_kwp * efficiency

        w1, w2, w3 = st.columns(3)
        w1.metric("Temperature", f"{temp} °C")
        w2.metric("Cloudiness", f"{cloudiness}%")
        w3.metric("Condition", weather_desc)

        st.success(f"⚡ **Estimated Live Output:** {current_kw:.2f} kW (System Efficiency: {efficiency*100:.1f}%)")
