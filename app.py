import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import math

# ==========================================
# 1. Page Configuration & Custom UI Styling
# ==========================================
st.set_page_config(
    page_title="Smart Solar Dashboard & Calculator",
    page_icon="☀️",
    layout="wide"
)

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
""", unsafe_allow_html=True)

# OpenWeatherMap API Key
API_KEY = "f95798b74fd5bd53dd615f40cdf88312"

# ==========================================
# 2. Header Section & Multi-language Option
# ==========================================
st.title("☀️ Smart Commercial Solar Calculator & Dashboard")
st.caption("Calculate household/industrial solar load, ROI, equipment brands, and real-time solar output.")

# Language Switcher
lang = st.radio("🌐 Language / ভাষা:", ["English", "বাংলা"], horizontal=True)

st.markdown("---")

# ==========================================
# 3. Sidebar Inputs
# ==========================================
st.sidebar.header("🔌 1. Appliance Quantities" if lang == "English" else "🔌 ১. সরঞ্জামের পরিমাণ")
fan_qty = st.sidebar.number_input("Ceiling Fan (75W)", min_value=0, value=5)
light_qty = st.sidebar.number_input("LED Light (15W)", min_value=0, value=10)
fridge_qty = st.sidebar.number_input("Refrigerator (200W)", min_value=0, value=1)
tv_qty = st.sidebar.number_input("Smart TV (80W)", min_value=0, value=1)
oven_qty = st.sidebar.number_input("Oven (1200W)", min_value=0, value=1)
pump_qty = st.sidebar.number_input("1 HP Submersible Pump (750W)", min_value=0, value=1)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ 2. Daily Usage (Hours)" if lang == "English" else "⏱️ ২. দৈনিক ব্যবহার (ঘণ্টা)")
fan_hours = st.sidebar.slider("Fan (Hours)", 0, 24, 10)
light_hours = st.sidebar.slider("Light (Hours)", 0, 24, 8)
fridge_hours = st.sidebar.slider("Refrigerator (Hours)", 0, 24, 24)
tv_hours = st.sidebar.slider("TV (Hours)", 0, 24, 5)
oven_hours = st.sidebar.slider("Oven (Minutes)", 0, 120, 30) / 60
pump_hours = st.sidebar.slider("Pump (Hours)", 0, 10, 1)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. Equipment & Brand Selection" if lang == "English" else "⚙️ ৩. ব্র্যান্ড নির্বাচন")

system_type = st.sidebar.radio("Select System Type:", ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"])

panel_brand = st.sidebar.selectbox("Solar Panel Brand:", ["Longi Solar (Tier-1)", "Jinko Solar (Tier-1)", "Canadian Solar", "Standard Brand"])
inverter_brand = st.sidebar.selectbox("Inverter Brand:", ["Growatt", "Deye", "Huawei", "Must / Standard"])

if "With Battery" in system_type:
    battery_type = st.sidebar.selectbox("Battery Type:", ["LiFePO4 Lithium Battery", "Tubular Lead-Acid Battery"])

# Brand-based pricing multipliers
brand_multiplier = 1.15 if "Tier-1" in panel_brand or "Huawei" in inverter_brand or "Deye" in inverter_brand else 1.0

# ==========================================
# 4. Roof Area Calculator Component
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🏠 Roof Area Calculator" if lang == "English" else "🏠 ছাদের আয়তন দিয়ে হিসেব")
roof_sqft = st.sidebar.number_input("Available Roof Area (Sq. Ft):", min_value=0, value=300)
max_possible_kwp = (roof_sqft / 100) * 1.0  # Approx 100 sqft per 1kWp

# ==========================================
# 5. Backend Calculations & ROI Logic
# ==========================================
running_watts = (fan_qty * 75) + (light_qty * 15) + (fridge_qty * 200) + (tv_qty * 80) + (oven_qty * 1200) + (pump_qty * 750)
surge_watts = (fan_qty * 75) + (light_qty * 15) + (tv_qty * 80) + (oven_qty * 1200) + (fridge_qty * 200 * 2.5) + (pump_qty * 750 * 3)

daily_wh = (fan_qty * 75 * fan_hours) + (light_qty * 15 * light_hours) + \
           (fridge_qty * 200 * 12) + (tv_qty * 80 * tv_hours) + \
           (oven_qty * 1200 * oven_hours) + (pump_qty * 750 * pump_hours)
daily_kwh = daily_wh / 1000

inverter_kva = (surge_watts * 1.25) / 1000
solar_kwp = (daily_wh / 4.0 / 0.85) / 1000
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0

# Cost Calculation with Brand Pricing
panel_unit_price = 28 * brand_multiplier if "Tier-1" in panel_brand else 25
panel_cost = (panels_count * 550) * panel_unit_price

if inverter_kva <= 3.5:
    inverter_cost = 50000 * brand_multiplier
elif inverter_kva <= 5.5:
    inverter_cost = 75000 * brand_multiplier
else:
    inverter_cost = 110000 * brand_multiplier

if "With Battery" in system_type:
    battery_ah = (daily_wh * 0.5) / (48 * 0.8)
    if battery_type == "LiFePO4 Lithium Battery":
        battery_cost = (battery_ah / 100) * 130000
    else:
        battery_cost = (battery_ah / 100) * 75000
else:
    battery_ah = 0
    battery_cost = 0

subtotal = panel_cost + inverter_cost + battery_cost
installation_cost = subtotal * 0.10
total_cost = subtotal + installation_cost

# Financial ROI Calculations
electricity_rate = 9.5  # Average BDT per kWh unit in Bangladesh
monthly_savings = daily_kwh * 30 * electricity_rate
yearly_savings = monthly_savings * 12
payback_years = total_cost / yearly_savings if yearly_savings > 0 else 0

# ==========================================
# 6. Main Dashboard Rendering
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load", f"{running_watts} W")
col2.metric("Peak Surge Load", f"{surge_watts:.0f} W")
col3.metric("Daily Usage", f"{daily_kwh:.2f} kWh")
col4.metric("Total Budget", f"BDT {total_cost:,.0f}")

st.markdown("---")

# Roof Fitting Alert
if solar_kwp > max_possible_kwp:
    st.warning(f"⚠️ **Roof Space Notice:** Your required system ({solar_kwp:.2f} kWp) needs ~{solar_kwp*100:.0f} Sq. Ft. Your roof is {roof_sqft} Sq. Ft (Max capacity: ~{max_possible_kwp:.2f} kWp).")

# Hardware Specs & Cost Summary
c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 System Specifications & Brands")
    st.info(f"⚡ **Inverter:** {max(3, round(inverter_kva))} KVA/KW ({inverter_brand})")
    st.info(f"☀️ **Solar Panels:** {solar_kwp:.2f} kWp ({panels_count}x 550W - {panel_brand})")
    if "With Battery" in system_type:
        st.info(f"🔋 **Battery:** {battery_ah:.0f} Ah 48V ({battery_type})")
    else:
        st.warning("🔋 **Battery:** Not required for On-Grid system.")

with c2:
    st.subheader("💰 Cost Breakdown & Financial ROI")
    st.write(f"• **Solar Panels ({panel_brand}):** BDT {panel_cost:,.0f}")
    st.write(f"• **Inverter ({inverter_brand}):** BDT {inverter_cost:,.0f}")
    if "With Battery" in system_type:
        st.write(f"• **Battery Bank:** BDT {battery_cost:,.0f}")
    st.write(f"• **Installation & Wiring (10%):** BDT {installation_cost:,.0f}")
    st.write("---")
    st.write(f"💵 **Est. Monthly Savings:** BDT {monthly_savings:,.0f} / month")
    st.write(f"📈 **Estimated Payback Period (ROI):** ~**{payback_years:.1f} Years**")

st.markdown("---")

# ==========================================
# 7. 24-Hour Solar Generation Chart
# ==========================================
st.subheader("📊 24-Hour Solar Generation Simulation")
hours = list(range(24))
generation_curve = [0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.85, 0.95, 1.0, 0.98, 0.90, 0.75, 0.5, 0.2, 0.05, 0, 0, 0, 0, 0, 0]
power_output = [solar_kwp * factor for factor in generation_curve]

df_solar = pd.DataFrame({'Time': [f"{h:02d}:00" for h in hours], 'Generation (kW)': power_output})
fig = px.area(df_solar, x='Time', y='Generation (kW)', 
              title=f"Estimated Daily Solar Generation Curve ({solar_kwp:.2f} kWp System)",
              color_discrete_sequence=['#F59E0B'])
fig.update_layout(template="plotly_white", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 8. Live Weather Solar Tracker (City & Map)
# ==========================================
st.subheader("🌦️ Live Weather-Based Solar Tracker")

track_type = st.radio("Select Location Mode:", ["Bangladesh City List", "Select Location on Map"], horizontal=True)

if track_type == "Bangladesh City List":
    bd_cities = ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barishal", "Rangpur", "Mymensingh", "Cox's Bazar", "Cumilla", "Gazipur"]
    selected_city = st.selectbox("Select a City in Bangladesh:", bd_cities)
    
    if st.button("Check Live Solar Output"):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={selected_city},BD&appid={API_KEY}&units=metric"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            cloudiness = data['clouds']['all']
            temp = data['main']['temp']
            weather_desc = data['weather'][0]['description'].title()
            
            efficiency = 1.0 - ((cloudiness / 100.0) * 0.80)
            current_kw = solar_kwp * efficiency
            
            w1, w2, w3 = st.columns(3)
            w1.metric("Temperature", f"{temp} °C")
            w2.metric("Cloudiness", f"{cloudiness}%")
            w3.metric("Condition", weather_desc)
            st.success(f"⚡ **Estimated Live Output for {selected_city}:** {current_kw:.2f} kW (Efficiency: {efficiency*100:.1f}%)")
        else:
            st.error("Error fetching weather data!")

else:
    st.info("🗺️ **Click anywhere on the map to pick a location:**")
    import folium
    from streamlit_folium import st_folium

    m = folium.Map(location=[23.8103, 90.4125], zoom_start=7)
    folium.LatLngPopup().add_to(m)

    map_data = st_folium(m, height=350, width=700)

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        
        st.write(f"📌 **Selected Location:** Lat {lat:.4f}, Lon {lon:.4f}")
        
        if st.button("Check Live Solar Output for Selected Location"):
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                cloudiness = data['clouds']['all']
                temp = data['main']['temp']
                weather_desc = data['weather'][0]['description'].title()
                
                efficiency = 1.0 - ((cloudiness / 100.0) * 0.80)
                current_kw = solar_kwp * efficiency
                
                w1, w2, w3 = st.columns(3)
                w1.metric("Temperature", f"{temp} °C")
                w2.metric("Cloudiness", f"{cloudiness}%")
                w3.metric("Condition", weather_desc)
                st.success(f"⚡ **Estimated Live Output:** {current_kw:.2f} kW (Efficiency: {efficiency*100:.1f}%)")
            else:
                st.error("Error fetching weather data for coordinates!")

# ==========================================
# 9. Footer Section
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748B; padding: 10px;">
        Designed by <b>Mohammad Sohel</b>
    </div>
    """,
    unsafe_allow_html=True
)
