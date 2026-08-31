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

# Custom CSS for Clear Visibility & Universal Day/Night Contrast
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #1E293B !important;
    border-radius: 12px;
    padding: 15px 18px !important;
    box-shadow: 0 4px 10px -1px rgba(0, 0, 0, 0.3);
    border-left: 6px solid #F59E0B !important;
    min-height: 95px;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    color: #CBD5E1 !important;
    white-space: nowrap !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    word-break: normal !important;
    white-space: nowrap !important;
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

.hero-container {
    background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                url('https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?q=80&w=1200&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    border-radius: 16px;
    padding: 35px 25px;
    margin-bottom: 25px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(245, 158, 11, 0.4);
}
.hero-title {
    color: #FFFFFF !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    margin-bottom: 8px !important;
    text-shadow: 0 2px 6px rgba(0, 0, 0, 0.8);
}
.hero-subtitle {
    color: #E2E8F0 !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    margin-bottom: 0px !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
}
.hero-badge {
    display: inline-block;
    background-color: #F59E0B;
    color: #0F172A !important;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    margin-bottom: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
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
        <span class="hero-badge">☀️ SOLAR CAD & ANALYTICS</span>
        <div class="hero-title">Solario • Next-Gen Smart Solar CAD & ROI Engine </div>
        <div class="hero-subtitle">Transform rooftops into clean energy powerhouses — Calculate solar load, 3D CAD, and live weather output.</div>
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
# 3. Sidebar Inputs & Categorized Appliances
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

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Regular Loads (Standard)" if lang == "English" else "💡 সাধারণ লোড (নিয়মিত ব্যবহার)")
for app_name, app_data in list(st.session_state.appliance_list.items()):
    if app_data.get("type", "regular") == "regular":
        col_app, col_del = st.sidebar.columns([4, 1])
        with col_app:
            new_qty = st.number_input(f"{app_name}", min_value=0, max_value=100, value=app_data["qty"], step=1, key=f"qty_{app_name}")
            st.session_state.appliance_list[app_name]["qty"] = new_qty
        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{app_name}"):
                del st.session_state.appliance_list[app_name]
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Heavy / High Power Loads" if lang == "English" else "⚡ হেভি ও হাই-ওয়াট লোড (আলাদা সময়)")
for app_name, app_data in list(st.session_state.appliance_list.items()):
    if app_data.get("type") == "heavy":
        col_app, col_del = st.sidebar.columns([4, 1])
        with col_app:
            new_qty = st.number_input(f"{app_name} (Qty)", min_value=0, max_value=50, value=app_data["qty"], step=1, key=f"qty_{app_name}")
            st.session_state.appliance_list[app_name]["qty"] = new_qty
            custom_hours = st.number_input(f"⏱️ {app_name} (Hours/Day)", min_value=0.1, max_value=24.0, value=float(app_data.get("hours", 1.0)), step=0.5, key=f"hrs_{app_name}")
            st.session_state.appliance_list[app_name]["hours"] = custom_hours
        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{app_name}"):
                del st.session_state.appliance_list[app_name]
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⏱️ 2. Regular Load Usage" if lang == "English" else "⏱️ ২. সাধারণ লোড ব্যবহারের সময়")
avg_running_hours = st.sidebar.slider("Avg Daily Hours for Regular Loads" if lang == "English" else "সাধারণ লোড সমূহের দৈনিক গড় সময় (ঘণ্টা)", 1, 24, 8)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. Equipment & Brand Selection" if lang == "English" else "⚙️ ৩. যন্ত্রপাতি ও ব্র্যান্ড নির্বাচন")

system_type = st.sidebar.radio("Select System Type:" if lang == "English" else "সিস্টেম টাইপ নির্বাচন করুন:", 
                               ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"])

panel_brand = st.sidebar.selectbox("Solar Panel Brand:" if lang == "English" else "সোলার প্যানেল ব্র্যান্ড:", 
                                  ["Longi Solar (Tier-1)", "Jinko Solar (Tier-1)", "Canadian Solar", "Standard Brand"])
inverter_brand = st.sidebar.selectbox("Inverter Brand:" if lang == "English" else "ইনভার্টার ব্র্যান্ড:", 
                                     ["Growatt", "Deye", "Huawei", "Must / Standard"])

if "With Battery" in system_type:
    battery_type = st.sidebar.selectbox("Battery Type:" if lang == "English" else "ব্যাটারি টাইপ:", 
                                        ["LiFePO4 Lithium Battery", "Tubular Lead-Acid Battery"])

brand_multiplier = 1.15 if "Tier-1" in panel_brand or "Huawei" in inverter_brand or "Deye" in inverter_brand else 1.0

# Roof Area Calculator Component
st.sidebar.markdown("---")
st.sidebar.header("🏠 Roof Area Calculator" if lang == "English" else "🏠 ছাদের আয়তন দিয়ে হিসেব")
roof_sqft = st.sidebar.number_input("Available Roof Area (Sq. Ft):" if lang == "English" else "খালি ছাদের আয়তন (বর্গফুট):", min_value=0, value=300)
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
        used_hrs = app_data.get("hours", 1.0)
        daily_wh += total_app_watt * used_hrs
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

electricity_rate = 9.5
monthly_savings = daily_kwh * 30 * electricity_rate
yearly_savings = monthly_savings * 12
payback_years = total_cost / yearly_savings if yearly_savings > 0 else 0

# ==========================================
# 5. Dashboard Metrics
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load" if lang == "English" else "চলমান লোড", f"{running_watts} W")
col2.metric("Peak Surge Load" if lang == "English" else "সর্বোচ্চ স্টার্ট লোড", f"{surge_watts:.0f} W")
col3.metric("Daily Usage" if lang == "English" else "দৈনিক ব্যবহার", f"{daily_kwh:.2f} kWh")
col4.metric("Total Budget" if lang == "English" else "মোট বাজেট", f"BDT {total_cost:,.0f}")

st.markdown("---")

if solar_kwp > max_possible_kwp:
    if lang == "English":
        st.warning(f"⚠️ **Roof Space Notice:** Your required system ({solar_kwp:.2f} kWp) needs ~{required_roof_sqft} Sq. Ft. Your roof is {roof_sqft} Sq. Ft.")
    else:
        st.warning(f"⚠️ **ছাদের জায়গার সতর্কতা:** আপনার প্রয়োজনীয় সিস্টেমের ({solar_kwp:.2f} kWp) জন্য অন্তত ~{required_roof_sqft} বর্গফুট ছাদ প্রয়োজন।")

c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 System Specifications & Brands" if lang == "English" else "📋 যন্ত্রপাতির বিবরণ ও ব্র্যান্ড")
    st.info(f"⚡ **Inverter:** {max(3, round(inverter_kva))} KVA ({inverter_brand})")
    st.info(f"☀️ **Solar Panels:** {solar_kwp:.2f} kWp ({panels_count}x 550W - {panel_brand})")
    st.info(f"🏠 **Roof Space Needed:** ~{required_roof_sqft} Sq. Ft")
    if "With Battery" in system_type:
        st.info(f"🔋 **Battery:** {battery_ah:.0f} Ah 48V ({battery_type})")
    else:
        st.warning("🔋 **Battery:** Not required for On-Grid system.")

with c2:
    st.subheader("💰 Cost Breakdown & Financial ROI" if lang == "English" else "💰 আনুমানিক ব্যয় ও সাশ্রয় (ROI)")
    st.write(f"• **Solar Panels:** BDT {panel_cost:,.0f}")
    st.write(f"• **Inverter:** BDT {inverter_cost:,.0f}")
    if "With Battery" in system_type:
        st.write(f"• **Battery Bank:** BDT {battery_cost:,.0f}")
    st.write(f"• **Installation & Wiring:** BDT {installation_cost:,.0f}")
    st.write("---")
    st.write(f"💵 **Est. Monthly Savings:** BDT {monthly_savings:,.0f}")
    st.write(f"📈 **Payback Period (ROI):** ~**{payback_years:.1f} Years**")

st.markdown("---")

# ==========================================
# 6. Dynamic AutoCAD Style SLD Generator (Pure SVG)
# ==========================================
def generate_autocad_sld_svg(sys_type, kwp, inv_kva, batt_ah, load_w, client_name="SOHEL ENERGY SOLUTIONS"):
    is_hybrid = "With Battery" in sys_type
    sys_title = "HYBRID / OFF-GRID SOLAR PV SINGLE LINE DIAGRAM" if is_hybrid else "ON-GRID SOLAR PV SINGLE LINE DIAGRAM"
    
    battery_svg_block = ""
    if is_hybrid:
        battery_svg_block = f"""
        <!-- Battery Bank Block -->
        <g transform="translate(420, 160)">
            <rect x="0" y="0" width="130" height="70" fill="#0A192F" stroke="#00E5FF" stroke-width="2" rx="4"/>
            <text x="65" y="25" fill="#00E5FF" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">BATTERY BANK</text>
            <text x="65" y="45" fill="#FFFFFF" font-family="monospace" font-size="10" text-anchor="middle">{batt_ah:.0f}Ah / 48V LiFePO4</text>
            <text x="65" y="60" fill="#8892B0" font-family="monospace" font-size="8" text-anchor="middle">DC STORAGE</text>
        </g>
        <!-- Wire from Inverter to Battery -->
        <path d="M 485 115 L 485 160" stroke="#FFD700" stroke-width="2.5" stroke-dasharray="4" fill="none"/>
        <text x="495" y="140" fill="#FFD700" font-family="monospace" font-size="8">DC BUS</text>
        """

    svg = f"""
    <svg width="100%" height="320" viewBox="0 0 950 320" xmlns="http://www.w3.org/2000/svg" style="background-color: #020C1B; border: 2px solid #1E293B; border-radius: 8px;">
        <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#0F2B48" stroke-width="0.5"/>
            </pattern>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#00E5FF"/>
            </marker>
        </defs>
        
        <!-- AutoCAD Grid Background -->
        <rect width="100%" height="100%" fill="url(#grid)" />
        
        <!-- Drawing Outer Frame -->
        <rect x="10" y="10" width="930" height="300" fill="none" stroke="#00E5FF" stroke-width="1.5"/>
        
        <!-- Title Block -->
        <g transform="translate(620, 230)">
            <rect x="0" y="0" width="315" height="74" fill="#0A192F" stroke="#00E5FF" stroke-width="1.5"/>
            <line x1="0" y1="25" x2="315" y2="25" stroke="#00E5FF" stroke-width="1"/>
            <line x1="0" y1="50" x2="315" y2="50" stroke="#00E5FF" stroke-width="1"/>
            <line x1="160" y1="25" x2="160" y2="74" stroke="#00E5FF" stroke-width="1"/>
            
            <text x="157" y="17" fill="#64FFDA" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">CAD SLD: {sys_title}</text>
            <text x="10" y="40" fill="#E6F1FF" font-family="monospace" font-size="9">CLIENT: {client_name[:18]}</text>
            <text x="170" y="40" fill="#E6F1FF" font-family="monospace" font-size="9">DESIGN: SOLARIO CAD ENGINE</text>
            <text x="10" y="65" fill="#8892B0" font-family="monospace" font-size="8">STD: BNBC 2020 / NFPA 70</text>
            <text x="170" y="65" fill="#8892B0" font-family="monospace" font-size="8">SCALE: N.T.S.</text>
        </g>

        <!-- 1. PV ARRAY -->
        <g transform="translate(30, 45)">
            <rect x="0" y="0" width="120" height="70" fill="#0A192F" stroke="#00E5FF" stroke-width="2" rx="4"/>
            <polygon points="10,15 35,15 45,55 20,55" fill="#112240" stroke="#64FFDA" stroke-width="1"/>
            <polygon points="40,15 65,15 75,55 50,55" fill="#112240" stroke="#64FFDA" stroke-width="1"/>
            <polygon points="70,15 95,15 105,55 80,55" fill="#112240" stroke="#64FFDA" stroke-width="1"/>
            <text x="60" y="66" fill="#64FFDA" font-family="monospace" font-size="10" font-weight="bold" text-anchor="middle">PV ARRAY ({kwp:.2f}kWp)</text>
        </g>

        <!-- Wire 1 -->
        <line x1="150" y1="80" x2="200" y2="80" stroke="#00E5FF" stroke-width="2.5" marker-end="url(#arrow)"/>
        <text x="175" y="72" fill="#8892B0" font-family="monospace" font-size="8" text-anchor="middle">DC 1000V</text>

        <!-- 2. DC PROTECTION BOX -->
        <g transform="translate(200, 45)">
            <rect x="0" y="0" width="110" height="70" fill="#0A192F" stroke="#FFD700" stroke-width="2" rx="4"/>
            <text x="55" y="25" fill="#FFD700" font-family="monospace" font-size="10" font-weight="bold" text-anchor="middle">DC Protection</text>
            <text x="55" y="42" fill="#E6F1FF" font-family="monospace" font-size="8" text-anchor="middle">• DC FUSE 1000V</text>
            <text x="55" y="53" fill="#E6F1FF" font-family="monospace" font-size="8" text-anchor="middle">• DC SPD Type II</text>
            <text x="55" y="64" fill="#E6F1FF" font-family="monospace" font-size="8" text-anchor="middle">• DC MCB 32A</text>
        </g>

        <!-- Wire 2 -->
        <line x1="310" y1="80" x2="360" y2="80" stroke="#00E5FF" stroke-width="2.5" marker-end="url(#arrow)"/>

        <!-- 3. INVERTER BLOCK -->
        <g transform="translate(360, 45)">
            <rect x="0" y="0" width="130" height="70" fill="#0A192F" stroke="#64FFDA" stroke-width="2" rx="4"/>
            <text x="65" y="22" fill="#64FFDA" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">SOLAR INVERTER</text>
            <text x="65" y="42" fill="#FFFFFF" font-family="monospace" font-size="10" text-anchor="middle">{inv_kva} KVA Pure Sine</text>
            <text x="65" y="58" fill="#8892B0" font-family="monospace" font-size="8" text-anchor="middle">= DC -> AC MPPT =</text>
        </g>

        {battery_svg_block}

        <!-- Wire 3 -->
        <line x1="490" y1="80" x2="540" y2="80" stroke="#64FFDA" stroke-width="2.5" marker-end="url(#arrow)"/>
        <text x="515" y="72" fill="#8892B0" font-family="monospace" font-size="8" text-anchor="middle">AC 230V</text>

        <!-- 4. AC DISTRIBUTION PANEL -->
        <g transform="translate(540, 45)">
            <rect x="0" y="0" width="110" height="70" fill="#0A192F" stroke="#FFD700" stroke-width="2" rx="4"/>
            <text x="55" y="25" fill="#FFD700" font-family="monospace" font-size="10" font-weight="bold" text-anchor="middle">AC Panel (MDB)</text>
            <text x="55" y="42" fill="#E6F1FF" font-family="monospace" font-size="8" text-anchor="middle">• AC MCB / MCCB</text>
            <text x="55" y="53" fill="#E6F1FF" font-family="monospace" font-size="8" text-anchor="middle">• AC SPD Type II</text>
            <text x="55" y="64" fill="#E6F1FF" font-family="monospace" font-size="8" text-anchor="middle">• Dual Earthing</text>
        </g>

        <!-- Wire 4 -->
        <line x1="650" y1="80" x2="700" y2="80" stroke="#64FFDA" stroke-width="2.5" marker-end="url(#arrow)"/>

        <!-- 5. CONNECTED BUILDING LOAD -->
        <g transform="translate(700, 45)">
            <rect x="0" y="0" width="120" height="70" fill="#0A192F" stroke="#00E5FF" stroke-width="2" rx="4"/>
            <text x="60" y="28" fill="#00E5FF" font-family="monospace" font-size="11" font-weight="bold" text-anchor="middle">BUILDING LOAD</text>
            <text x="60" y="48" fill="#FFFFFF" font-family="monospace" font-size="10" text-anchor="middle">{load_w} Watts</text>
            <text x="60" y="62" fill="#8892B0" font-family="monospace" font-size="8" text-anchor="middle">AC Single/3-Phase</text>
        </g>

        <!-- Grid Connection (For On-Grid or Hybrid Grid Feed) -->
        <line x1="595" y1="115" x2="595" y2="160" stroke="#64FFDA" stroke-width="2" stroke-dasharray="3"/>
        <g transform="translate(540, 160)">
            <rect x="0" y="0" width="110" height="40" fill="#0A192F" stroke="#64FFDA" stroke-width="1.5" rx="3"/>
            <text x="55" y="20" fill="#64FFDA" font-family="monospace" font-size="9" text-anchor="middle">NATIONAL GRID</text>
            <text x="55" y="32" fill="#8892B0" font-family="monospace" font-size="8" text-anchor="middle">Net Metering</text>
        </g>

        <!-- Earth Lines Symbol -->
        <g transform="translate(250, 125)">
            <line x1="5" y1="0" x2="5" y2="15" stroke="#00FF66" stroke-width="1.5"/>
            <line x1="0" y1="15" x2="10" y2="15" stroke="#00FF66" stroke-width="1.5"/>
            <line x1="2" y1="18" x2="8" y2="18" stroke="#00FF66" stroke-width="1.5"/>
            <line x1="4" y1="21" x2="6" y2="21" stroke="#00FF66" stroke-width="1.5"/>
        </g>
    </svg>
    """
    return svg

# ==========================================
# 7. Advanced Engineering Studio (BNBC & NFPA Standards)
# ==========================================
st.subheader("⚙️ Advanced Solar Engineering Studio" if lang == "English" else "⚙️ অ্যাডভান্সড সোলার ইঞ্জিনিয়ারিং স্টুডিও")
st.caption("Standardized according to BNBC-2020 & NFPA-70 (NEC) compliance standards")

eng_tabs = st.tabs([
    "🔌 Dynamic AutoCAD SLD Diagram",
    "⚡ Cable Sizing & Voltage Drop",
    "🛡️ Circuit Breaker & Safety",
    "📋 Bill of Quantities (BOQ)"
])

# --- TAB 1: Auto CAD Style SLD ---
with eng_tabs[0]:
    st.write("#### Auto-Generated AutoCAD Single Line Diagram (SLD)")
    st.caption("Diagram dynamically changes based on your On-Grid/Off-Grid configuration & loads.")
    
    autocad_svg_code = generate_autocad_sld_svg(
        sys_type=system_type, 
        kwp=solar_kwp, 
        inv_kva=max(3, round(inverter_kva)), 
        batt_ah=battery_ah, 
        load_w=running_watts
    )
    
    st.components.v1.html(autocad_svg_code, height=335)
    st.info("ℹ️ **AutoCAD Engineering Standard:** Fully compliant with BNBC & NFPA-70. Switch system type from sidebar to view live On-Grid / Hybrid wiring updates.")

# --- TAB 2: Cable Sizing & Voltage Drop ---
with eng_tabs[1]:
    st.write("#### Cable Selection & Voltage Drop Analysis")
    col_c1, col_c2 = st.columns(2)
    system_voltage = 48 if "With Battery" in system_type else 230
    dc_current = (solar_kwp * 1000) / system_voltage if system_voltage > 0 else 0
    
    with col_c1:
        cable_dist = st.number_input("Cable Distance (Meters):", min_value=5, max_value=150, value=15)
        st.metric(label="Calculated Current", value=f"{dc_current:.2f} A")
        
    with col_c2:
        if dc_current <= 15:
            rec_cable = "4.0 mm² Copper"
            v_drop_val = (2 * cable_dist * dc_current * 0.0178) / (4.0 * system_voltage)
        elif dc_current <= 30:
            rec_cable = "6.0 mm² Copper"
            v_drop_val = (2 * cable_dist * dc_current * 0.0178) / (6.0 * system_voltage)
        else:
            rec_cable = "10.0 mm² Copper"
            v_drop_val = (2 * cable_dist * dc_current * 0.0178) / (10.0 * system_voltage)
            
        st.metric(label="Recommended Cable", value=rec_cable)
        st.metric(label="Voltage Drop (%)", value=f"{v_drop_val:.2f}%")

# --- TAB 3: Breaker & Safety ---
with eng_tabs[2]:
    st.write("#### Circuit Breaker & Safety Specs")
    ac_amp = (solar_kwp * 1000) / 230
    mcb_rating_val = int(np.ceil(ac_amp * 1.25 / 6) * 6)
    
    cp1, cp2 = st.columns(2)
    with cp1:
        st.markdown("##### ⚡ Protection Ratings")
        st.write(f"• **AC Main MCB:** `{max(16, mcb_rating_val)} A (Single/Double Pole)`")
        st.write(f"• **DC Breaker:** `{max(16, int(dc_current * 1.25))} A (1000V DC)`")
        st.write(f"• **SPD Protection:** `Type-II DC & AC SPD Boxes`")
    with cp2:
        st.markdown("##### 🌩️ Earthing & Lightning System")
        st.write("• **Earthing Pits:** 2 Independent Pits")
        st.write("• **Earthing Wire:** 16 mm² Copper Wire")

# --- TAB 4: BOQ ---
with eng_tabs[3]:
    st.write("#### Project BOQ Summary")
    boq_items = {
        "Item Description": [
            f"Solar PV Modules (550W Tier-1)",
            f"Solar Inverter ({max(3, round(inverter_kva))} KVA)",
            "Solar Cable & Armored Wiring",
            "Aluminum Rooftop Structure",
            "DC/AC Distribution Box + Breakers",
            "Earthing & Lightning Arrestor",
            "Installation Charge"
        ],
        "Qty": [f"{panels_count} Pcs", "1 Unit", f"{cable_dist * 2} Meters", "1 Set", "1 Set", "2 Sets", "1 Job"],
        "Est. Price (BDT)": [panel_cost, inverter_cost, cable_dist * 2 * 180, panels_count * 2500, 18000, 14000, installation_cost]
    }
    df_boq_table = pd.DataFrame(boq_items)
    st.dataframe(df_boq_table, use_container_width=True)
    st.markdown(f"#### **Total Engineering Cost: BDT {df_boq_table['Est. Price (BDT)'].sum():,.0f}**")

st.markdown("---")

# ==========================================
# 8. Proposal Report & Direct PDF Printer Engine
# ==========================================
st.subheader("📄 Dynamic PDF Engineering Proposal Generator")
st.caption("Generates an AutoCAD Style SLD & standard Engineering PDF report.")

client_name = st.text_input("Client / Project Name:", value="Solario Demo Project")

if st.button("📥 Generate Official PDF Proposal Report", use_container_width=True):
    
    svg_report_sld = generate_autocad_sld_svg(
        sys_type=system_type, 
        kwp=solar_kwp, 
        inv_kva=max(3, round(inverter_kva)), 
        batt_ah=battery_ah, 
        load_w=running_watts,
        client_name=client_name
    )

    report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Solar System Engineering Proposal - {client_name}</title>
        <style>
            @media print {{
                .no-print {{ display: none !important; }}
                body {{ margin: 0; padding: 15px; background: white; }}
                .page-break {{ page-break-before: always; }}
            }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1E293B; margin: 20px; }}
            .header {{ text-align: center; border-bottom: 3px solid #F59E0B; padding-bottom: 10px; margin-bottom: 20px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #0F172A; margin: 0; }}
            .subtitle {{ font-size: 13px; color: #64748B; margin-top: 5px; }}
            .section-title {{ font-size: 15px; font-weight: bold; color: #0F172A; background: #F1F5F9; padding: 6px 10px; border-left: 4px solid #F59E0B; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }}
            th, td {{ border: 1px solid #CBD5E1; padding: 8px 10px; text-align: left; }}
            th {{ background-color: #F8FAFC; font-weight: bold; }}
            .summary-box {{ display: flex; justify-content: space-between; margin-top: 15px; font-size: 13px; }}
            .summary-card {{ background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; width: 48%; box-sizing: border-box; }}
            .total-row {{ font-weight: bold; background-color: #FEF3C7; }}
            .btn-print {{ background-color: #F59E0B; color: white; padding: 12px 25px; font-size: 16px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; margin-bottom: 20px; width: 100%; }}
            .btn-print:hover {{ background-color: #D97706; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 11px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 10px; }}
        </style>
    </head>
    <body>
        
        <div class="no-print">
            <button class="btn-print" onclick="window.print()">🖨️ Download / Print PDF Report (Save as PDF)</button>
        </div>

        <div class="header">
            <div class="title">SOLAR ENERGY SYSTEM ENGINEERING PROPOSAL</div>
            <div class="subtitle">Solario • Smart Solar CAD Engine</div>
        </div>
        
        <p><strong>Client Name:</strong> {client_name} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>System Type:</strong> {system_type}</p>
        
        <div class="section-title">1. System Executive Summary</div>
        <div class="summary-box">
            <div class="summary-card">
                <strong>Running Load:</strong> {running_watts} W<br>
                <strong>Peak Surge Load:</strong> {surge_watts:.0f} W<br>
                <strong>Daily Energy Usage:</strong> {daily_kwh:.2f} kWh
            </div>
            <div class="summary-card">
                <strong>Solar Capacity:</strong> {solar_kwp:.2f} kWp ({panels_count}x 550W Panel)<br>
                <strong>Inverter Rating:</strong> {max(3, round(inverter_kva))} KVA ({inverter_brand})<br>
                <strong>Roof Space Needed:</strong> ~{required_roof_sqft} Sq. Ft
            </div>
        </div>

        <div class="section-title">2. Dynamic AutoCAD Single Line Diagram (SLD)</div>
        <div style="margin-top: 10px; text-align: center;">
            {svg_report_sld}
        </div>

        <div class="section-title">3. Financial ROI & Budget Details</div>
        <table>
            <tr><th>Metric</th><th>Details / Amount</th></tr>
            <tr><td>Total System Investment</td><td><strong>BDT {total_cost:,.0f}</strong></td></tr>
            <tr><td>Estimated Monthly Savings</td><td>BDT {monthly_savings:,.0f} / Month</td></tr>
            <tr><td>Payback Period (ROI)</td><td><strong>~{payback_years:.1f} Years</strong></td></tr>
        </table>

        <div class="section-title">4. Bill of Quantities (BOQ)</div>
        <table>
            <tr><th>Item Description</th><th>Quantity</th><th>Estimated Price (BDT)</th></tr>
            <tr><td>Solar PV Modules (550W Tier-1)</td><td>{panels_count} Pcs</td><td>BDT {panel_cost:,.0f}</td></tr>
            <tr><td>Solar Inverter ({max(3, round(inverter_kva))} KVA)</td><td>1 Unit</td><td>BDT {inverter_cost:,.0f}</td></tr>
            <tr><td>Solar Cable & Wiring</td><td>{cable_dist * 2} Meters</td><td>BDT {cable_dist * 2 * 180:,.0f}</td></tr>
            <tr><td>Rooftop Structure</td><td>1 Set</td><td>BDT {panels_count * 2500:,.0f}</td></tr>
            <tr><td>DC/AC Distribution & Breakers</td><td>1 Set</td><td>BDT 18,000</td></tr>
            <tr><td>Earthing & Protections</td><td>2 Sets</td><td>BDT 14,000</td></tr>
            <tr><td>Installation Charges</td><td>1 Job</td><td>BDT {installation_cost:,.0f}</td></tr>
            <tr class="total-row"><td colspan="2">Total Budget</td><td>BDT {df_boq_table['Est. Price (BDT)'].sum():,.0f}</td></tr>
        </table>

        <div class="footer">
            Generated by Solario CAD Engine • Designed by Mohammad Sohel
        </div>
    </body>
    </html>
    """

    st.markdown("### 📜 Live Proposal & PDF Print View")
    st.components.v1.html(report_html, height=750, scrolling=True)

# ==========================================
# 9. Footer
# ==========================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94A3B8; padding: 10px;">
        Designed by <b>Mohammad Sohel</b>
    </div>
    """,
    unsafe_allow_html=True
)
