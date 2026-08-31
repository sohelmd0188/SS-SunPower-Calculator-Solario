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
# 1. Page Configuration & Custom UI Styling
# ==========================================
st.set_page_config(
    page_title="Solario • Next-Gen Smart Solar CAD & ROI Engine",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional UI Styling (Glassmorphism & Clean Executive Vibe)
st.markdown("""
<style>
    /* Global & Metric Card Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important;
        border-radius: 14px;
        padding: 16px 20px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-left: 6px solid #F59E0B !important;
        min-height: 100px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
    }

    /* Modern Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 11px 20px;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.5);
        transform: translateY(-1px);
    }

    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.95)), 
                    url('https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 40px 30px;
        margin-bottom: 25px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
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
        font-size: 1.05rem !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
    }
    .hero-badge {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B !important;
        border: 1px solid rgba(245, 158, 11, 0.4);
        font-weight: 700;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        margin-bottom: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# OpenWeatherMap API Key
API_KEY = "f95798b74fd5bd53dd615f40cdf88312"

# ==========================================
# 2. Header Section & Multi-language Option
# ==========================================
lang = st.radio("🌐 Language / ভাষা:", ["English", "বাংলা"], horizontal=True)

if lang == "English":
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ Enterprise Solar CAD & Analytics</span>
        <div class="hero-title">Solario • Next-Gen Smart Solar CAD & ROI Engine</div>
        <div class="hero-subtitle">Transform rooftops into clean energy powerhouses — Calculate precise solar loads, 3D CAD blueprints, and live weather output seamlessly.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ এন্টারপ্রাইজ সোলার ক্যাড ও অ্যানালিটিক্স</span>
        <div class="hero-title">স্মার্ট বাণিজ্যিক সোলার ক্যালকুলেটর ও ড্যাশবোর্ড</div>
        <div class="hero-subtitle">বাসাবাড়ি বা শিল্প প্রতিষ্ঠানের সোলার লোড, আনুমানিক খরচ, ব্র্যান্ড ও রিয়েল-টাইম বিদ্যুৎ উৎপাদন খুব সহজেই নিখুঁতভাবে হিসেব করুন।</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. Sidebar Inputs & Categorized Appliances (Loop-driven)
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

# Render Regular and Heavy loads cleanly using loops
for load_type, title_en, title_bn in [
    ("regular", "💡 Regular Loads (Standard)", "💡 সাধারণ লোড (নিয়মিত ব্যবহার)"),
    ("heavy", "⚡ Heavy / High Power Loads", "⚡ হেভি ও হাই-ওয়াট লোড (আলাদা সময়)")
]:
    st.sidebar.subheader(title_en if lang == "English" else title_bn)
    for app_name, app_data in list(st.session_state.appliance_list.items()):
        if app_data.get("type", "regular") == load_type:
            col_app, col_del = st.sidebar.columns([4, 1])
            with col_app:
                new_qty = st.number_input(
                    f"{app_name}",
                    min_value=0,
                    max_value=100,
                    value=app_data["qty"],
                    step=1,
                    key=f"qty_{app_name}"
                )
                st.session_state.appliance_list[app_name]["qty"] = new_qty
                
                if load_type == "heavy":
                    custom_hours = st.number_input(
                        f"⏱️ Hours/Day",
                        min_value=0.1,
                        max_value=24.0,
                        value=float(app_data.get("hours", 1.0)),
                        step=0.5,
                        key=f"hrs_{app_name}"
                    )
                    st.session_state.appliance_list[app_name]["hours"] = custom_hours
                
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{app_name}", help=f"Remove {app_name}"):
                    del st.session_state.appliance_list[app_name]
                    st.rerun()
    st.sidebar.markdown("---")

# Add Extra Appliance Section
st.sidebar.subheader("➕ Add Extra Appliance" if lang == "English" else "➕ অতিরিক্ত ডিভাইস যুক্ত করুন")
selected_extra = st.sidebar.selectbox(
    "Select Appliance:" if lang == "English" else "ডিভাইস বেছে নিন:",
    options=list(EXTRA_APPLIANCES.keys()),
    key="selected_extra_appliance"
)

if st.sidebar.button("➕ Add to List" if lang == "English" else "➕ তালিকায় যুক্ত করুন", use_container_width=True):
    if selected_extra not in st.session_state.appliance_list:
        info = EXTRA_APPLIANCES[selected_extra]
        st.session_state.appliance_list[selected_extra] = {
            "watt": info["watt"], 
            "qty": 1, 
            "type": info["type"],
            "hours": info["default_hours"]
        }
        st.sidebar.success(f"Added {selected_extra}!")
        st.rerun()
    else:
        st.sidebar.warning("Already in your list!" if lang == "English" else "ইতিমধ্যে তালিকায় আছে!")

st.sidebar.markdown("---")
st.sidebar.header("⏱️ 2. Regular Load Usage" if lang == "English" else "⏱️ ২. সাধারণ লোড ব্যবহারের সময়")
avg_running_hours = st.sidebar.slider(
    "Avg Daily Hours for Regular Loads" if lang == "English" else "সাধারণ লোড সমূহের দৈনিক গড় সময় (ঘণ্টা)", 
    1, 24, 8
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. Equipment & Brand Selection" if lang == "English" else "⚙️ ৩. যন্ত্রপাতি ও ব্র্যান্ড নির্বাচন")

system_type = st.sidebar.radio(
    "Select System Type:" if lang == "English" else "সিস্টেম টাইপ নির্বাচন করুন:", 
    ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"]
)

if "With Battery" in system_type:
    st.sidebar.markdown("---")
    st.sidebar.header("🔋 Battery & Storage Optimization")
    autonomy_days = st.sidebar.slider("Backup Autonomy Days (Cloudy Days):", 1, 3, 1)
    dod_limit = st.sidebar.slider("Depth of Discharge (DoD %):", 50, 90, 80)

panel_brand = st.sidebar.selectbox(
    "Solar Panel Brand:" if lang == "English" else "সোলার প্যানেল ব্র্যান্ড:", 
    ["Longi Solar (Tier-1)", "Jinko Solar (Tier-1)", "Canadian Solar", "Standard Brand"]
)
inverter_brand = st.sidebar.selectbox(
    "Inverter Brand:" if lang == "English" else "ইনভার্টার ব্র্যান্ড:", 
    ["Growatt", "Deye", "Huawei", "Must / Standard"]
)

if "With Battery" in system_type:
    battery_type = st.sidebar.selectbox(
        "Battery Type:" if lang == "English" else "ব্যাটারি টাইপ:", 
        ["LiFePO4 Lithium Battery", "Tubular Lead-Acid Battery"]
    )

st.sidebar.markdown("---")
st.sidebar.header("💵 Net Metering & Tariff Plan")
tariff_type = st.sidebar.selectbox(
    "Select Electricity Tariff Slab:",
    ["Residential Tiered (Avg BDT 9.5/kWh)", "Commercial Flat Rate (BDT 12.0/kWh)", "Industrial Peak/Off-Peak (BDT 10.5/kWh)"]
)

electricity_rate = 12.0 if "Commercial" in tariff_type else (10.5 if "Industrial" in tariff_type else 9.5)
brand_multiplier = 1.15 if "Tier-1" in panel_brand or "Huawei" in inverter_brand or "Deye" in inverter_brand else 1.0

st.sidebar.markdown("---")
st.sidebar.header("🏠 Roof Area Calculator" if lang == "English" else "🏠 ছাদের আয়তন দিয়ে হিসেব")
roof_sqft = st.sidebar.number_input(
    "Available Roof Area (Sq. Ft):" if lang == "English" else "খালি ছাদের আয়তন (বর্গফুট):", 
    min_value=0, 
    value=300
)
max_possible_kwp = (roof_sqft / 100) * 1.0

# ==========================================
# 4. Backend Calculations & Load Logic
# ==========================================
running_watts = 0
surge_watts = 0
daily_wh = 0.0

for app_name, app_data in st.session_state.appliance_list.items():
    qty = app_data["qty"]
    watt = app_data["watt"]
    app_type = app_data.get("type", "regular")
    
    total_app_watt = watt * qty
    running_watts += total_app_watt
    
    if app_type == "heavy":
        daily_wh += total_app_watt * app_data.get("hours", 1.0)
    else:
        daily_wh += total_app_watt * avg_running_hours
    
    if "Refrigerator" in app_name:
        surge_watts += total_app_watt * 2.5
    elif "Pump" in app_name:
        surge_watts += total_app_watt * 3.0
    elif "AC" in app_name:
        surge_watts += total_app_watt * 1.5
    else:
        surge_watts += total_app_watt

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
# 5. Main Dashboard Rendering Metrics
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load" if lang == "English" else "চলমান লোড", f"{running_watts} W")
col2.metric("Peak Surge Load" if lang == "English" else "সর্বোচ্চ স্টার্ট লোড", f"{surge_watts:.0f} W")
col3.metric("Daily Usage" if lang == "English" else "দৈনিক ব্যবহার", f"{daily_kwh:.2f} kWh")
col4.metric("Total Budget" if lang == "English" else "মোট বাজেট", f"BDT {total_cost:,.0f}")

st.markdown("---")

if solar_kwp > max_possible_kwp:
    msg = f"⚠️ **Roof Space Notice:** Your required system ({solar_kwp:.2f} kWp) needs ~{required_roof_sqft} Sq. Ft. Your roof is {roof_sqft} Sq. Ft (Max capacity: ~{max_possible_kwp:.2f} kWp)." if lang == "English" else f"⚠️ **ছাদের জায়গার সতর্কতা:** আপনার প্রয়োজনীয় সিস্টেমের ({solar_kwp:.2f} kWp) জন্য অন্তত ~{required_roof_sqft} বর্গফুট ছাদ প্রয়োজন। আপনার দেওয়া ছাদের ক্ষেত্রফল {roof_sqft} বর্গফুট (সর্বোচ্চ ক্ষমতা: ~{max_possible_kwp:.2f} kWp)।"
    st.warning(msg)

c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 System Specifications & Brands" if lang == "English" else "📋 যন্ত্রপাতির বিবরণ ও ব্র্যান্ড")
    st.info(f"⚡ **Inverter / ইনভার্টার:** {max(3, round(inverter_kva))} KVA/KW ({inverter_brand})")
    st.info(f"☀️ **Solar Panels / প্যানেল:** {solar_kwp:.2f} kWp ({panels_count}x 550W - {panel_brand})")
    st.info(f"🏠 **Roof Space Needed / ছাদের জায়গা:** ~{required_roof_sqft} Sq. Ft (Available: {roof_sqft} Sq. Ft)")
    if "With Battery" in system_type:
        st.info(f"🔋 **Battery / ব্যাটারি:** {battery_ah:.0f} Ah 48V ({battery_type})")
    else:
        st.warning("🔋 **Battery:** Not required for On-Grid system." if lang == "English" else "🔋 **ব্যাটারি:** অন-গ্রিড সিস্টেমের জন্য ব্যাটারির প্রয়োজন নেই।")

with c2:
    st.subheader("💰 Cost Breakdown & Financial ROI" if lang == "English" else "💰 আনুমানিক ব্যয় ও সাশ্রয় (ROI)")
    st.write(f"• **Solar Panels ({panel_brand}):** BDT {panel_cost:,.0f}" if lang == "English" else f"• **সোলার প্যানেল ({panel_brand}):** BDT {panel_cost:,.0f}")
    st.write(f"• **Inverter ({inverter_brand}):** BDT {inverter_cost:,.0f}" if lang == "English" else f"• **ইনভার্টার ({inverter_brand}):** BDT {inverter_cost:,.0f}")
    if "With Battery" in system_type:
        st.write(f"• **Battery Bank:** BDT {battery_cost:,.0f}" if lang == "English" else f"• **ব্যাটারি ব্যাকআপ:** BDT {battery_cost:,.0f}")
    st.write(f"• **Installation & Wiring (10%):** BDT {installation_cost:,.0f}" if lang == "English" else f"• **ইনস্টলেশন ও ওয়্যারিং (১০%):** BDT {installation_cost:,.0f}")
    st.write("---")
    st.write(f"💵 **Est. Monthly Savings:** BDT {monthly_savings:,.0f} / month" if lang == "English" else f"💵 **মাসিক আনুমানিক বিল সাশ্রয়:** BDT {monthly_savings:,.0f} / মাস")
    st.write(f"📈 **Estimated Payback Period (ROI):** ~**{payback_years:.1f} Years**" if lang == "English" else f"📈 **মূল্য ফেরত আসার আনুমানিক সময় (ROI):** ~**{payback_years:.1f} বছর**")

st.markdown("---")

# ==========================================
# 6. CAD & Solar Layout Options
# ==========================================
st.subheader("📐 Auto Solar CAD & Custom Location Design" if lang == "English" else "📐 সোলার ক্যাড ও নিজস্ব লোকেশন ডিজাইন")

cad_mode = st.radio(
    "Choose Design View Level:" if lang == "English" else "ডিজাইন ভিউ বেছে নিন:",
    ["Level 1: 2D Blueprint (Matplotlib)", "Level 2: 3D Interactive Model (Pydeck)", "Level 3: Custom Satellite Roof Placement"],
    horizontal=True
)

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
        
        placed = 0
        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    x = 1.0 + c * (p_w + 0.5)
                    y = 1.0 + r * (p_l + 0.5)
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

        building_data = [{
            "coordinates": [[base_lon - 0.0001, base_lat - 0.0001], [base_lon + 0.0001, base_lat - 0.0001], [base_lon + 0.0001, base_lat + 0.0001], [base_lon - 0.0001, base_lat + 0.0001]],
            "height": 15, "fill_color": [30, 41, 59, 200]
        }]
        
        panel_data = []
        placed = 0
        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    panel_data.append({
                        "coordinates": [[base_lon + (c - cols/2)*0.00002, base_lat + (r - rows/2)*0.00002], [base_lon + (c - cols/2)*0.00002 + 0.000015, base_lat + (r - rows/2)*0.00002], [base_lon + (c - cols/2)*0.00002 + 0.000015, base_lat + (r - rows/2)*0.00002 + 0.000015], [base_lon + (c - cols/2)*0.00002, base_lat + (r - rows/2)*0.00002 + 0.000015]],
                        "height": 15.8, "fill_color": [2, 132, 199, 255]
                    })
                    placed += 1

        st.pydeck_chart(pdk.Deck(
            layers=[
                pdk.Layer("PolygonLayer", building_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True),
                pdk.Layer("PolygonLayer", panel_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True)
            ],
            initial_view_state=pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=19, pitch=55, bearing=30)
        ))

    elif "Level 3" in cad_mode:
        c1, c2 = st.columns(2)
        base_lat = c1.number_input("Latitude", value=22.376735, format="%.6f", key="sat_lat")
        base_lon = c2.number_input("Longitude", value=91.839035, format="%.6f", key="sat_lon")

        sat_map = folium.Map(location=[base_lat, base_lon], zoom_start=20, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')
        sat_data = st_folium(sat_map, height=500, width=900, key="sat_map_input")

        click_lat = sat_data["last_clicked"]["lat"] if sat_data and sat_data.get("last_clicked") else base_lat
        click_lon = sat_data["last_clicked"]["lng"] if sat_data and sat_data.get("last_clicked") else base_lon

        viz_map = folium.Map(location=[click_lat, click_lon], zoom_start=21, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')
        folium.Marker([click_lat, click_lon], tooltip="Selected Roof", icon=folium.Icon(color="red", icon="home")).add_to(viz_map)

        placed_count = 0
        for r in range(rows):
            for c in range(cols):
                if placed_count < panels_count:
                    folium.Rectangle(
                        bounds=[[click_lat + (r - rows/2)*0.000022, click_lon + (c - cols/2)*0.000022], [click_lat + (r - rows/2)*0.000022 + 0.000018, click_lon + (c - cols/2)*0.000022 + 0.000018]],
                        color="#38BDF8", fill=True, fill_color="#0284C7", fill_opacity=0.85
                    ).add_to(viz_map)
                    placed_count += 1
        st_folium(viz_map, height=500, width=900, key=f"viz_map_{click_lat}_{click_lon}")

st.markdown("---")

# ==========================================
# 7. 24-Hour Solar Generation Chart
# ==========================================
st.subheader("📊 24-Hour Solar Generation Simulation" if lang == "English" else "📊 ২৪ ঘণ্টার সৌর বিদ্যুৎ উৎপাদন গ্রাফ")
df_solar = pd.DataFrame({
    'Time': [f"{h:02d}:00" for h in range(24)],
    'Generation (kW)': [solar_kwp * f for f in [0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.85, 0.95, 1.0, 0.98, 0.90, 0.75, 0.5, 0.2, 0.05, 0, 0, 0, 0, 0, 0]]
})
fig = px.area(df_solar, x='Time', y='Generation (kW)', color_discrete_sequence=['#F59E0B'])
fig.update_layout(template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 8. Advanced Engineering Studio (BNBC & NFPA)
# ==========================================
st.subheader("⚙️ Advanced Solar Engineering Studio" if lang == "English" else "⚙️ অ্যাডভান্সড সোলার ইঞ্জিনিয়ারিং স্টুডিও")
eng_tabs = st.tabs(["🔌 SLD", "⚡ Cable Sizing", "🛡️ Protections", "📋 BOQ"])

with eng_tabs[0]:
    battery_node_str = f'BAT [label="Battery Bank\\n({battery_ah:.0f} Ah 48V)", shape=cylinder, style=filled, fillcolor="#D1D5DB"]; BAT -> INV [label="DC Bus"];' if "With Battery" in system_type else ""
    st.graphviz_chart(f"""
    digraph G {{
        rankdir=LR; node [fontname="sans-serif"];
        PV [label="PV Array\\n({solar_kwp:.2f} kWp)", shape=box, style=filled, fillcolor="#FEF3C7"];
        DCDB [label="DC Breaker & SPD", shape=component, style=filled, fillcolor="#FDE68A"];
        INV [label="Inverter\\n({max(3, round(inverter_kva))} KVA)", shape=box, style=filled, fillcolor="#93C5FD"];
        ACDB [label="AC Breaker & SPD", shape=component, style=filled, fillcolor="#6EE7B7"];
        LOAD [label="Load\\n({running_watts} W)", shape=house, style=filled, fillcolor="#A7F3D0"];
        {battery_node_str}
        PV -> DCDB -> INV -> ACDB -> LOAD;
    }}
    """)

with eng_tabs[1]:
    system_voltage = 48 if "With Battery" in system_type else 230
    dc_current = (solar_kwp * 1000) / system_voltage if system_voltage > 0 else 0
    col_c1, col_c2 = st.columns(2)
    cable_dist = col_c1.number_input("Cable Distance (Meters):", min_value=5, max_value=150, value=15)
    rec_cable, v_drop = ("4.0 mm² Copper", 1.2) if dc_current <= 15 else ("6.0 mm² Copper", 1.8)
    col_c2.metric("Recommended Cable", rec_cable)

with eng_tabs[2]:
    st.write(f"• **AC Main MCB:** `{max(16, int(np.ceil((solar_kwp*1000/230)*1.25/6)*6))} A`")
    st.write(f"• **DC Circuit Breaker:** `{max(16, int(dc_current*1.25))} A (1000V DC)`")

with eng_tabs[3]:
    df_boq = pd.DataFrame({
        "Item Description": ["Solar PV Modules (550W)", f"Inverter ({max(3, round(inverter_kva))} KVA)", "Solar Cable & Wiring", "Mounting Structure", "Distribution Box + SPD", "Earthing & Lightning", "Installation Charge"],
        "Qty": [f"{panels_count} Pcs", "1 Unit", f"{cable_dist*2} Meters", "1 Set", "1 Set", "2 Sets", "1 Job"],
        "Est. Price (BDT)": [panel_cost, inverter_cost, cable_dist*2*180, panels_count*2500, 18000, 14000, installation_cost]
    })
    st.dataframe(df_boq, use_container_width=True)
    st.markdown(f"#### **Total Cost: BDT {df_boq['Est. Price (BDT)'].sum():,.0f}**")

st.markdown("---")

# ==========================================
# 9. Live Weather & Footer
# ==========================================
st.subheader("🌦️ Live Weather-Based Solar Tracker" if lang == "English" else "🌦️ লাইভ আবহাওয়া ট্র্যাকার")
selected_city = st.selectbox("Select City:", ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna"])
if st.button("Check Live Weather Output"):
    res = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={selected_city},BD&appid={API_KEY}&units=metric")
    if res.status_code == 200:
        data = res.json()
        eff = 1.0 - ((data['clouds']['all'] / 100.0) * 0.80)
        st.success(f"⚡ **Live Output for {selected_city}:** {solar_kwp * eff:.2f} kW (Efficiency: {eff*100:.1f}%)")

st.markdown("---")
st.markdown('<div style="text-align: center; color: #94A3B8; padding: 10px;">Designed by <b>Mohammad Sohel</b></div>', unsafe_allow_html=True)
