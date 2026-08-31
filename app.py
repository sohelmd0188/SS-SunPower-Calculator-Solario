import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pydeck as pdk
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. Page Configuration & Professional UI Styling
# ==========================================
st.set_page_config(
    page_title="Solario • Next-Gen Smart Solar CAD & ROI Engine",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Theme Adjustments */
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important;
        border-radius: 14px;
        padding: 16px 20px !important;
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-left: 6px solid #F59E0B !important;
        min-height: 105px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }

    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: #FFFFFF;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 11px;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.5);
        transform: translateY(-1px);
    }

    /* Hero Banner Component */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.95)), 
                    url('https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 18px;
        padding: 40px 30px;
        margin-bottom: 30px;
        box-shadow: 0 12px 30px -6px rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .hero-title {
        color: #FFFFFF !important;
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #CBD5E1 !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
    }
    .hero-badge {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B !important;
        border: 1px solid rgba(245, 158, 11, 0.4);
        font-weight: 700;
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

API_KEY = "f95798b74fd5bd53dd615f40cdf88312"

# ==========================================
# 2. Header & Localization Section
# ==========================================
lang = st.radio("🌐 Language / ভাষা:", ["English", "বাংলা"], horizontal=True)

if lang == "English":
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ NEXT-GEN SOLAR CAD & ANALYTICS</span>
        <div class="hero-title">Solario • Smart Solar CAD & ROI Engine</div>
        <div class="hero-subtitle">Transform commercial and residential rooftops into clean energy powerhouses with precision load modeling, 3D CAD layouts, and live weather telemetry.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ সোলার ক্যাড ও অ্যানালিটিক্স</span>
        <div class="hero-title">স্মার্ট বাণিজ্যিক সোলার ক্যালকুলেটর ও ড্যাশবোর্ড</div>
        <div class="hero-subtitle">বাসাবাড়ি বা শিল্প প্রতিষ্ঠানের সোলার লোড, আনুমানিক খরচ, ব্র্যান্ড ও রিয়েল-টাইম বিদ্যুৎ উৎপাদন হিসেব করুন।</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. Sidebar Configuration & Load Profiles
# ==========================================
if "appliance_list" not in st.session_state:
    st.session_state.appliance_list = {
        "Ceiling Fan (75W)": {"watt": 75, "qty": 5, "type": "regular", "hours": 8.0},
        "LED Light (15W)": {"watt": 15, "qty": 10, "type": "regular", "hours": 8.0},
        "Refrigerator (200W)": {"watt": 200, "qty": 1, "type": "regular", "hours": 8.0},
        "Smart TV (80W)": {"watt": 80, "qty": 1, "type": "regular", "hours": 8.0},
        "Oven (1200W)": {"watt": 1200, "qty": 1, "type": "heavy", "hours": 1.0},
        "1 HP Submersible Pump (750W)": {"watt": 750, "qty": 1, "type": "heavy", "hours": 1.5}
    }

EXTRA_APPLIANCES = {
    "1.5 Ton Inverter AC (1500W)": {"watt": 1500, "type": "heavy", "default_hours": 6.0},
    "1 Ton Non-Inverter AC (1200W)": {"watt": 1200, "type": "heavy", "default_hours": 6.0},
    "2 Ton AC (2200W)": {"watt": 2200, "type": "heavy", "default_hours": 6.0},
    "Washing Machine (500W)": {"watt": 500, "type": "heavy", "default_hours": 1.0},
    "Geyser / Water Heater (2000W)": {"watt": 2000, "type": "heavy", "default_hours": 1.0},
    "Microwave Oven (1000W)": {"watt": 1000, "type": "heavy", "default_hours": 0.5},
    "Computer / Desktop (250W)": {"watt": 250, "type": "regular", "default_hours": 8.0},
    "Laptop Charger (65W)": {"watt": 65, "type": "regular", "default_hours": 8.0},
    "Iron Box (1000W)": {"watt": 1000, "type": "heavy", "default_hours": 0.5},
    "Induction Cooker (1800W)": {"watt": 1800, "type": "heavy", "default_hours": 2.0}
}

st.sidebar.header("🔌 1. Appliance Quantities & Load" if lang == "English" else "🔌 ১. সরঞ্জামের পরিমাণ ও লোড")

with st.sidebar.expander("💡 Regular Loads (Standard)", expanded=True):
    for app_name, app_data in list(st.session_state.appliance_list.items()):
        if app_data.get("type", "regular") == "regular":
            col_app, col_del = st.columns([4, 1])
            with col_app:
                new_qty = st.number_input(f"{app_name}", min_value=0, max_value=100, value=app_data["qty"], step=1, key=f"qty_{app_name}")
                st.session_state.appliance_list[app_name]["qty"] = new_qty
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{app_name}"):
                    del st.session_state.appliance_list[app_name]
                    st.rerun()

with st.sidebar.expander("⚡ Heavy / High Power Loads", expanded=True):
    for app_name, app_data in list(st.session_state.appliance_list.items()):
        if app_data.get("type") == "heavy":
            col_app, col_del = st.columns([4, 1])
            with col_app:
                new_qty = st.number_input(f"{app_name} (Qty)", min_value=0, max_value=50, value=app_data["qty"], step=1, key=f"qty_{app_name}")
                st.session_state.appliance_list[app_name]["qty"] = new_qty
                custom_hours = st.number_input(f"⏱️ {app_name} (Hrs/Day)", min_value=0.1, max_value=24.0, value=float(app_data.get("hours", 1.0)), step=0.5, key=f"hrs_{app_name}")
                st.session_state.appliance_list[app_name]["hours"] = custom_hours
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_heavy_{app_name}"):
                    del st.session_state.appliance_list[app_name]
                    st.rerun()

st.sidebar.subheader("➕ Add Appliance" if lang == "English" else "➕ ডিভাইস যুক্ত করুন")
selected_extra = st.sidebar.selectbox("Select Appliance:", options=list(EXTRA_APPLIANCES.keys()), key="selected_extra_appliance")
if st.sidebar.button("➕ Add to List", use_container_width=True):
    if selected_extra not in st.session_state.appliance_list:
        info = EXTRA_APPLIANCES[selected_extra]
        st.session_state.appliance_list[selected_extra] = {"watt": info["watt"], "qty": 1, "type": info["type"], "hours": info["default_hours"]}
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⏱️ 2. Regular Load Usage")
avg_running_hours = st.sidebar.slider("Avg Daily Hours for Regular Loads", 1, 24, 8)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. Equipment & Brand Selection")
system_type = st.sidebar.radio("Select System Type:", ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"])

if "With Battery" in system_type:
    autonomy_days = st.sidebar.slider("Backup Autonomy Days:", 1, 3, 1)
    dod_limit = st.sidebar.slider("Depth of Discharge (DoD %):", 50, 90, 80)

panel_brand = st.sidebar.selectbox("Solar Panel Brand:", ["Longi Solar (Tier-1)", "Jinko Solar (Tier-1)", "Canadian Solar", "Standard Brand"])
inverter_brand = st.sidebar.selectbox("Inverter Brand:", ["Growatt", "Deye", "Huawei", "Must / Standard"])

if "With Battery" in system_type:
    battery_type = st.sidebar.selectbox("Battery Type:", ["LiFePO4 Lithium Battery", "Tubular Lead-Acid Battery"])

st.sidebar.markdown("---")
st.sidebar.header("💵 Net Metering & Tariff Plan")
tariff_type = st.sidebar.selectbox("Select Tariff Slab:", ["Residential Tiered (Avg BDT 9.5/kWh)", "Commercial Flat Rate (BDT 12.0/kWh)", "Industrial Peak/Off-Peak (BDT 10.5/kWh)"])

electricity_rate = 12.0 if "Commercial" in tariff_type else (10.5 if "Industrial" in tariff_type else 9.5)
brand_multiplier = 1.15 if "Tier-1" in panel_brand or "Huawei" in inverter_brand or "Deye" in inverter_brand else 1.0

st.sidebar.markdown("---")
st.sidebar.header("🏠 Roof Area Calculator")
roof_sqft = st.sidebar.number_input("Available Roof Area (Sq. Ft):", min_value=0, value=300)
max_possible_kwp = (roof_sqft / 100) * 1.0

# ==========================================
# 4. Calculation Engine Logic
# ==========================================
running_watts = sum(d["watt"] * d["qty"] for d in st.session_state.appliance_list.values())
surge_watts = sum(
    (d["watt"] * d["qty"]) * (2.5 if "Refrigerator" in n else (3.0 if "Pump" in n else (1.5 if "AC" in n else 1.0)))
    for n, d in st.session_state.appliance_list.items()
)
daily_wh = sum(
    (d["watt"] * d["qty"]) * (d.get("hours", 1.0) if d.get("type") == "heavy" else avg_running_hours)
    for d in st.session_state.appliance_list.values()
)

daily_kwh = daily_wh / 1000.0
inverter_kva = (surge_watts * 1.25) / 1000
solar_kwp = (daily_wh / 4.0 / 0.85) / 1000 if daily_wh > 0 else 0
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0
required_roof_sqft = math.ceil(solar_kwp * 100)

panel_unit_price = 28 * brand_multiplier if "Tier-1" in panel_brand else 25
panel_cost = (panels_count * 550) * panel_unit_price

inverter_cost = (50000 if inverter_kva <= 3.5 else (75000 if inverter_kva <= 5.5 else 110000)) * brand_multiplier

if "With Battery" in system_type:
    battery_ah = ((daily_wh * autonomy_days) / (48 * (dod_limit / 100.0)))
    battery_cost = (battery_ah / 100) * (130000 if "LiFePO4" in battery_type else 75000)
else:
    battery_ah = 0
    battery_cost = 0

subtotal = panel_cost + inverter_cost + battery_cost
installation_cost = subtotal * 0.10
total_cost = subtotal + installation_cost

monthly_savings = daily_kwh * 30 * electricity_rate
yearly_savings = monthly_savings * 12
payback_years = total_cost / yearly_savings if yearly_savings > 0 else 0

# ==========================================
# 5. Metrics Display Grid
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load", f"{running_watts} W")
col2.metric("Peak Surge Load", f"{surge_watts:.0f} W")
col3.metric("Daily Usage", f"{daily_kwh:.2f} kWh")
col4.metric("Total Budget", f"BDT {total_cost:,.0f}")

st.markdown("---")

if solar_kwp > max_possible_kwp:
    st.warning(f"⚠️ **Roof Space Notice:** Your required system ({solar_kwp:.2f} kWp) needs ~{required_roof_sqft} Sq. Ft. Your roof is {roof_sqft} Sq. Ft (Max capacity: ~{max_possible_kwp:.2f} kWp).")

c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 System Specifications & Brands")
    st.info(f"⚡ **Inverter:** {max(3, round(inverter_kva))} KVA/KW ({inverter_brand})")
    st.info(f"☀️ **Solar Panels:** {solar_kwp:.2f} kWp ({panels_count}x 550W - {panel_brand})")
    st.info(f"🏠 **Roof Space Needed:** ~{required_roof_sqft} Sq. Ft (Available: {roof_sqft} Sq. Ft)")
    if "With Battery" in system_type:
        st.info(f"🔋 **Battery Bank:** {battery_ah:.0f} Ah 48V ({battery_type})")
    else:
        st.warning("🔋 **Battery:** Not required for On-Grid system.")

with c2:
    st.subheader("💰 Cost Breakdown & Financial ROI")
    st.write(f"• **Solar Panels ({panel_brand}):** BDT {panel_cost:,.0f}")
    st.write(f"• **Inverter ({inverter_brand}):** BDT {inverter_cost:,.0f}")
    if "With Battery" in system_type:
        st.write(f"• **Battery Bank:** BDT {battery_cost:,.0f}")
    st.write(f"• **Installation & Wiring (10%):** BDT {installation_cost:,.0f}")
    st.markdown("---")
    st.write(f"💵 **Est. Monthly Savings:** BDT {monthly_savings:,.0f} / month")
    st.write(f"📈 **Estimated Payback Period (ROI):** ~**{payback_years:.1f} Years**")

st.markdown("---")

# ==========================================
# 6. CAD & Solar Layout Options
# ==========================================
st.subheader("📐 Auto Solar CAD & Custom Location Design")
cad_mode = st.radio("Choose Design View Level:", ["Level 1: 2D Blueprint (Matplotlib)", "Level 2: 3D Interactive Model (Pydeck)", "Level 3: Custom Satellite Roof Placement"], horizontal=True)

if panels_count > 0 and roof_sqft > 0:
    roof_w = np.sqrt(roof_sqft * 1.5)
    roof_l = roof_sqft / roof_w
    p_w, p_l = 3.5, 6.5
    cols = max(1, int(roof_w // (p_w + 0.5)))
    rows = int(np.ceil(panels_count / cols))

    if "Level 1" in cad_mode:
        fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        roof_rect = patches.Rectangle((0, 0), roof_w, roof_l, linewidth=2, edgecolor='#F59E0B', facecolor='#1E293B', linestyle='--')
        ax.add_patch(roof_rect)
        
        placed, start_x, start_y = 0, 1.0, 1.0
        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    x = start_x + c * (p_w + 0.5)
                    y = start_y + r * (p_l + 0.5)
                    if (x + p_w <= roof_w) and (y + p_l <= roof_l):
                        panel_patch = patches.Rectangle((x, y), p_w, p_l, linewidth=1, edgecolor='#38BDF8', facecolor='#0284C7', alpha=0.85)
                        ax.add_patch(panel_patch)
                        placed += 1

        ax.set_xlim(-4, roof_w + 4)
        ax.set_ylim(-4, roof_l + 4)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title(f"2D Blueprint: {placed} Panels Placed ({panels_count} Required)", fontsize=10, fontweight='bold', color='#F8FAFC', pad=10)
        st.pyplot(fig, use_container_width=True)

    elif "Level 2" in cad_mode:
        c1, c2 = st.columns(2)
        base_lat = c1.number_input("Latitude", value=23.8103, format="%.4f")
        base_lon = c2.number_input("Longitude", value=90.4125, format="%.4f")

        building_data = [{"coordinates": [[base_lon - 0.0001, base_lat - 0.0001], [base_lon + 0.0001, base_lat - 0.0001], [base_lon + 0.0001, base_lat + 0.0001], [base_lon - 0.0001, base_lat + 0.0001]], "height": 15, "fill_color": [30, 41, 59, 200]}]
        panel_data = []
        placed = 0
        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    ox, oy = (c - cols/2) * 0.00002, (r - rows/2) * 0.00002
                    panel_data.append({"coordinates": [[base_lon + ox, base_lat + oy], [base_lon + ox + 0.000015, base_lat + oy], [base_lon + ox + 0.000015, base_lat + oy + 0.000015], [base_lon + ox, base_lat + oy + 0.000015]], "height": 15.8, "fill_color": [2, 132, 199, 255]})
                    placed += 1

        roof_layer = pdk.Layer("PolygonLayer", building_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True)
        panels_layer = pdk.Layer("PolygonLayer", panel_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True)
        st.pydeck_chart(pdk.Deck(layers=[roof_layer, panels_layer], initial_view_state=pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=19, pitch=55, bearing=30)))

    elif "Level 3" in cad_mode:
        st.info("🗺️ Click on the Satellite Map to position your solar array.")
        c1, c2 = st.columns(2)
        base_lat = c1.number_input("Latitude", value=22.376735, format="%.6f", key="sat_lat")
        base_lon = c2.number_input("Longitude", value=91.839035, format="%.6f", key="sat_lon")

        sat_data = st_folium(folium.Map(location=[base_lat, base_lon], zoom_start=20, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite'), height=500, width=900, key="sat_map_input")
        click_lat = sat_data["last_clicked"]["lat"] if sat_data and sat_data.get("last_clicked") else base_lat
        click_lon = sat_data["last_clicked"]["lng"] if sat_data and sat_data.get("last_clicked") else base_lon

        viz_map = folium.Map(location=[click_lat, click_lon], zoom_start=21, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')
        folium.Marker([click_lat, click_lon], icon=folium.Icon(color="red", icon="home")).add_to(viz_map)
        
        placed_count = 0
        for r in range(rows):
            for c in range(cols):
                if placed_count < panels_count:
                    folium.Rectangle(bounds=[[click_lat + ((r - rows/2) * 0.000022), click_lon + ((c - cols/2) * 0.000022)], [click_lat + ((r - rows/2) * 0.000022) + 0.000018, click_lon + ((c - cols/2) * 0.000022) + 0.000018]], color="#38BDF8", fill=True, fill_color="#0284C7", fill_opacity=0.85).add_to(viz_map)
                    placed_count += 1
        st_folium(viz_map, height=500, width=900, key=f"viz_map_{click_lat}_{click_lon}")

st.markdown("---")

# ==========================================
# 7. 24-Hour Generation Chart & Environmental Metrics
# ==========================================
st.subheader("📊 24-Hour Solar Generation Simulation")
hours = list(range(24))
generation_curve = [0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.85, 0.95, 1.0, 0.98, 0.90, 0.75, 0.5, 0.2, 0.05, 0, 0, 0, 0, 0, 0]
fig = px.area(pd.DataFrame({'Time': [f"{h:02d}:00" for h in hours], 'Generation (kW)': [solar_kwp * f for f in generation_curve]}), x='Time', y='Generation (kW)', color_discrete_sequence=['#F59E0B'])
fig.update_layout(template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("🌱 Environmental Impact & CO2 Reduction")
annual_kwh_gen = daily_kwh * 365
annual_co2 = (annual_kwh_gen * 0.5) / 1000.0
eq_trees = int(annual_co2 * 45)

e1, e2, e3 = st.columns(3)
e1.metric("Annual Clean Generation", f"{annual_kwh_gen:,.0f} kWh")
e2.metric("Annual CO2 Reduction", f"{annual_co2:.2f} Tons")
e3.metric("Equivalent Trees Planted", f"{eq_trees:,} Trees")

st.markdown("---")

# ==========================================
# 8. Advanced Engineering Studio (BOQ Table)
# ==========================================
st.subheader("⚙️ Advanced Solar Engineering Studio (BOQ)")
df_boq = pd.DataFrame({
    "Item Description": [f"Solar PV Modules (550W Tier-1)", f"Solar Inverter ({max(3, round(inverter_kva))} KVA)", "Solar Cable & Wiring", "Aluminum Mounting Structure", "DC/AC Distribution Box", "Earthing & Protection", "Installation Charges"],
    "Quantity": [f"{panels_count} Pcs", "1 Unit", "30 Meters", "1 Set", "1 Set", "2 Sets", "1 Job"],
    "Est. Price (BDT)": [panel_cost, inverter_cost, 5400, panels_count * 2500, 18000, 14000, installation_cost]
})
st.dataframe(df_boq, use_container_width=True)
st.markdown(f"#### **Total Engineering Cost: BDT {df_boq['Est. Price (BDT)'].sum():,.0f}**")

st.markdown("---")

# ==========================================
# 9. Live Weather Tracker
# ==========================================
st.subheader("🌦️ Live Weather-Based Solar Tracker")
selected_city = st.selectbox("Select a City in Bangladesh:", ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barishal", "Rangpur"])
if st.button("Check Live Solar Output"):
    res = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={selected_city},BD&appid={API_KEY}&units=metric")
    if res.status_code == 200:
        data = res.json()
        eff = 1.0 - ((data['clouds']['all'] / 100.0) * 0.80)
        w1, w2, w3 = st.columns(3)
        w1.metric("Temperature", f"{data['main']['temp']} °C")
        w2.metric("Cloudiness", f"{data['clouds']['all']}%")
        w3.metric("Condition", data['weather'][0]['description'].title())
        st.success(f"⚡ **Estimated Live Output for {selected_city}:** {solar_kwp * eff:.2f} kW (Efficiency: {eff*100:.1f}%)")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #94A3B8; padding: 10px;'>Designed by <b>Mohammad Sohel</b></div>", unsafe_allow_html=True)
