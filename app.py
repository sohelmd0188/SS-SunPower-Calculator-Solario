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
/* Enhanced Metric Box Styling with High Contrast Day/Night Support */
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

# Categorized Default Appliances (Regular vs Heavy)
if "appliance_list" not in st.session_state:
    st.session_state.appliance_list = {
        # Regular Loads
        "Ceiling Fan (75W)": {"watt": 75, "qty": 5, "type": "regular", "hours": 8.0},
        "LED Light (15W)": {"watt": 15, "qty": 10, "type": "regular", "hours": 8.0},
        "Refrigerator (200W)": {"watt": 200, "qty": 1, "type": "regular", "hours": 8.0},
        "Smart TV (80W)": {"watt": 80, "qty": 1, "type": "regular", "hours": 8.0},
        
        # Heavy Loads
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

# --- REGULAR LOADS ---
st.sidebar.subheader("💡 Regular Loads (Standard)" if lang == "English" else "💡 সাধারণ লোড (নিয়মিত ব্যবহার)")
for app_name, app_data in list(st.session_state.appliance_list.items()):
    if app_data.get("type", "regular") == "regular":
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
            
        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{app_name}", help=f"Remove {app_name}"):
                del st.session_state.appliance_list[app_name]
                st.rerun()

# --- HEAVY LOADS ---
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Heavy / High Power Loads" if lang == "English" else "⚡ হেভি ও হাই-ওয়াট লোড (আলাদা সময়)")
for app_name, app_data in list(st.session_state.appliance_list.items()):
    if app_data.get("type") == "heavy":
        col_app, col_del = st.sidebar.columns([4, 1])
        with col_app:
            new_qty = st.number_input(
                f"{app_name} (Qty)",
                min_value=0,
                max_value=50,
                value=app_data["qty"],
                step=1,
                key=f"qty_{app_name}"
            )
            st.session_state.appliance_list[app_name]["qty"] = new_qty
            
            custom_hours = st.number_input(
                f"⏱️ {app_name} (Hours/Day)",
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
st.sidebar.header("⏱️ 2. Regular Load Usage" if lang == "English" else "⏱️ ২. সাধারণ লোড ব্যবহারের সময়")
avg_running_hours = st.sidebar.slider(
    "Avg Daily Hours for Regular Loads" if lang == "English" else "সাধারণ লোড সমূহের দৈনিক গড় সময় (ঘণ্টা)", 
    1, 24, 8
)

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
# 5. Main Dashboard Rendering Metrics
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load" if lang == "English" else "চলমান লোড", f"{running_watts} W")
col2.metric("Peak Surge Load" if lang == "English" else "সর্বোচ্চ স্টার্ট লোড", f"{surge_watts:.0f} W")
col3.metric("Daily Usage" if lang == "English" else "দৈনিক ব্যবহার", f"{daily_kwh:.2f} kWh")
col4.metric("Total Budget" if lang == "English" else "মোট বাজেট", f"BDT {total_cost:,.0f}")

st.markdown("---")

if solar_kwp > max_possible_kwp:
    if lang == "English":
        st.warning(f"⚠️ **Roof Space Notice:** Your required system ({solar_kwp:.2f} kWp) needs ~{required_roof_sqft} Sq. Ft. Your roof is {roof_sqft} Sq. Ft (Max capacity: ~{max_possible_kwp:.2f} kWp).")
    else:
        st.warning(f"⚠️ **ছাদের জায়গার সতর্কতা:** আপনার প্রয়োজনীয় সিস্টেমের ({solar_kwp:.2f} kWp) জন্য অন্তত ~{required_roof_sqft} বর্গফুট ছাদ প্রয়োজন। আপনার দেওয়া ছাদের ক্ষেত্রফল {roof_sqft} বর্গফুট (সর্বোচ্চ ক্ষমতা: ~{max_possible_kwp:.2f} kWp)।")

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

    # --- LEVEL 1: 2D Blueprint ---
    if "Level 1" in cad_mode:
        fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        
        roof_rect = patches.Rectangle((0, 0), roof_w, roof_l, linewidth=2, edgecolor='#F59E0B', facecolor='#1E293B', linestyle='--')
        ax.add_patch(roof_rect)
        
        ax.text(roof_w/2, -1.8, f"Roof Width: {roof_w:.1f} ft", ha='center', fontsize=9, color='#F8FAFC')
        ax.text(-1.8, roof_l/2, f"Roof Length: {roof_l:.1f} ft", va='center', rotation='vertical', fontsize=9, color='#F8FAFC')

        placed = 0
        start_x, start_y = 1.0, 1.0

        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    x = start_x + c * (p_w + 0.5)
                    y = start_y + r * (p_l + 0.5)
                    if (x + p_w <= roof_w) and (y + p_l <= roof_l):
                        panel_patch = patches.Rectangle((x, y), p_w, p_l, linewidth=1, edgecolor='#38BDF8', facecolor='#0284C7', alpha=0.85)
                        ax.add_patch(panel_patch)
                        ax.plot([x, x+p_w], [y+p_l/2, y+p_l/2], color='#E0F2FE', linewidth=0.5)
                        ax.plot([x+p_w/2, x+p_w/2], [y, y+p_l], color='#E0F2FE', linewidth=0.5)
                        placed += 1

        ax.set_xlim(-4, roof_w + 4)
        ax.set_ylim(-4, roof_l + 4)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title(f"2D Blueprint: {placed} Panels Placed ({panels_count} Required)", fontsize=10, fontweight='bold', color='#F8FAFC', pad=10)
        st.pyplot(fig, use_container_width=True)

    # --- LEVEL 2: 3D Interactive Model ---
    elif "Level 2" in cad_mode:
        st.write("📍 **Enter your coordinates to generate 3D Building:**" if lang == "English" else "📍 **৩ডি বিল্ডিং তৈরির জন্য লোকেশন কোঅর্ডিনেট দিন:**")
        c1, c2 = st.columns(2)
        base_lat = c1.number_input("Latitude", value=23.8103, format="%.4f")
        base_lon = c2.number_input("Longitude", value=90.4125, format="%.4f")

        building_data = [{
            "coordinates": [
                [base_lon - 0.0001, base_lat - 0.0001],
                [base_lon + 0.0001, base_lat - 0.0001],
                [base_lon + 0.0001, base_lat + 0.0001],
                [base_lon - 0.0001, base_lat + 0.0001]
            ],
            "height": 15,
            "fill_color": [30, 41, 59, 200]
        }]
        
        panel_data = []
        placed = 0
        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    offset_x = (c - cols/2) * 0.00002
                    offset_y = (r - rows/2) * 0.00002
                    panel_data.append({
                        "coordinates": [
                            [base_lon + offset_x, base_lat + offset_y],
                            [base_lon + offset_x + 0.000015, base_lat + offset_y],
                            [base_lon + offset_x + 0.000015, base_lat + offset_y + 0.000015],
                            [base_lon + offset_x, base_lat + offset_y + 0.000015]
                        ],
                        "height": 15.8,
                        "fill_color": [2, 132, 199, 255]
                    })
                    placed += 1

        roof_layer = pdk.Layer("PolygonLayer", building_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True)
        panels_layer = pdk.Layer("PolygonLayer", panel_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True)

        view_state = pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=19, pitch=55, bearing=30)
        st.pydeck_chart(pdk.Deck(layers=[roof_layer, panels_layer], initial_view_state=view_state))

    # --- LEVEL 3: Real Satellite Interactive Solar Placement ---
    elif "Level 3" in cad_mode:
        st.info("🗺️ **How to use:** Enter coordinates or zoom into the Satellite Map and **CLICK on your roof**!" if lang == "English" else f"🗺️ **ব্যবহারের নিয়ম:** ম্যাপে ছাদের ওপর **ক্লিক করুন**। সাথে সাথে {panels_count}টি প্যানেল ছাদের ওপর বসে যাবে!")
        
        c1, c2 = st.columns(2)
        base_lat = c1.number_input("Latitude", value=22.376735, format="%.6f", key="sat_lat")
        base_lon = c2.number_input("Longitude", value=91.839035, format="%.6f", key="sat_lon")

        sat_map = folium.Map(
            location=[base_lat, base_lon], 
            zoom_start=20, 
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
            attr='Google Satellite'
        )

        sat_data = st_folium(sat_map, height=500, width=900, key="sat_map_input")

        click_lat, click_lon = base_lat, base_lon
        is_clicked = False

        if sat_data and sat_data.get("last_clicked"):
            click_lat = sat_data["last_clicked"]["lat"]
            click_lon = sat_data["last_clicked"]["lng"]
            is_clicked = True

        st.markdown("---")
        st.subheader("📍 Rooftop Solar Placement View" if lang == "English" else "📍 ছাদে সোলার প্যানেল প্লেসমেন্ট ভিউ")
        
        viz_map = folium.Map(
            location=[click_lat, click_lon], 
            zoom_start=21, 
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
            attr='Google Satellite'
        )

        folium.Marker(
            [click_lat, click_lon], 
            tooltip="Selected Roof Location",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(viz_map)

        placed_count = 0
        for r in range(rows):
            for c in range(cols):
                if placed_count < panels_count:
                    p_lat = click_lat + ((r - rows/2) * 0.000022)
                    p_lon = click_lon + ((c - cols/2) * 0.000022)
                    
                    bounds = [[p_lat, p_lon], [p_lat + 0.000018, p_lon + 0.000018]]
                    
                    folium.Rectangle(
                        bounds=bounds,
                        color="#38BDF8",
                        fill=True,
                        fill_color="#0284C7",
                        fill_opacity=0.85,
                        tooltip=f"Solar Panel #{placed_count + 1} (550W)"
                    ).add_to(viz_map)
                    placed_count += 1

        st_folium(viz_map, height=500, width=900, key=f"viz_map_{click_lat}_{click_lon}")
        
        if is_clicked:
            st.success(f"🎉 **{placed_count} Solar Panels placed at Coordinates:** Lat `{click_lat:.6f}`, Lon `{click_lon:.6f}`")

st.markdown("---")

# ==========================================
# 7. 24-Hour Solar Generation Chart
# ==========================================
st.subheader("📊 24-Hour Solar Generation Simulation" if lang == "English" else "📊 ২৪ ঘণ্টার সৌর বিদ্যুৎ উৎপাদন গ্রাফ")
hours = list(range(24))
generation_curve = [0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.85, 0.95, 1.0, 0.98, 0.90, 0.75, 0.5, 0.2, 0.05, 0, 0, 0, 0, 0, 0]
power_output = [solar_kwp * factor for factor in generation_curve]

df_solar = pd.DataFrame({'Time': [f"{h:02d}:00" for h in hours], 'Generation (kW)': power_output})
fig = px.area(df_solar, x='Time', y='Generation (kW)', 
              title=f"Estimated Daily Solar Generation Curve ({solar_kwp:.2f} kWp System)" if lang == "English" else f"দৈনিক আনুমানিক বিদ্যুৎ উৎপাদন গ্রাফ ({solar_kwp:.2f} kWp System)",
              color_discrete_sequence=['#F59E0B'])
fig.update_layout(template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 8. Advanced Engineering Studio (BNBC & NFPA Standards)
# ==========================================
st.subheader("⚙️ Advanced Solar Engineering Studio" if lang == "English" else "⚙️ অ্যাডভান্সড সোলার ইঞ্জিনিয়ারিং স্টুডিও")
st.caption("Standardized according to BNBC-2020 & NFPA-70 (NEC) compliance standards" if lang == "English" else "BNBC-২০২০ এবং NFPA-৭০ (NEC) এর মানদণ্ড অনুযায়ী প্রস্তুতকৃত")

eng_tabs = st.tabs([
    "🔌 Single Line Diagram (SLD)" if lang == "English" else "🔌 সিঙ্গেল লাইন ডায়াগ্রাম (SLD)",
    "⚡ Cable Sizing & Voltage Drop" if lang == "English" else "⚡ ক্যাবল সাইজিং ও ভোল্টেজ ড্রপ",
    "🛡️ Circuit Breaker & Safety" if lang == "English" else "🛡️ সার্কিট ব্রেকার ও সেফটি",
    "📋 Bill of Quantities (BOQ)" if lang == "English" else "📋 সামগ্রীর তালিকা ও বাজেট (BOQ)"
])

# --- TAB 1: SLD ---
with eng_tabs[0]:
    st.write("#### Dynamic Electrical SLD Layout" if lang == "English" else "#### ডায়নামিক ইলেকট্রিক্যাল SLD লেআউট")
    
    battery_node_str = f'BAT [label="Battery Bank\\n({battery_ah:.0f} Ah 48V)", shape=cylinder, style=filled, fillcolor="#D1D5DB"]; BAT -> INV [label="DC Bus"];' if "With Battery" in system_type else ""
    
    dot_code = f"""
    digraph G {{
        rankdir=LR;
        node [fontname="sans-serif"];
        
        PV [label="PV Array\\n({solar_kwp:.2f} kWp)", shape=box, style=filled, fillcolor="#FEF3C7"];
        DCDB [label="DC Breaker & SPD\\n(Protection)", shape=component, style=filled, fillcolor="#FDE68A"];
        INV [label="Solar Inverter\\n({max(3, round(inverter_kva))} KVA)", shape=box, style=filled, fillcolor="#93C5FD"];
        ACDB [label="AC Breaker & SPD\\n(Main Distribution)", shape=component, style=filled, fillcolor="#6EE7B7"];
        LOAD [label="Connected Load\\n({running_watts} W)", shape=house, style=filled, fillcolor="#A7F3D0"];
        
        {battery_node_str}
        
        PV -> DCDB [label="DC Cable"];
        DCDB -> INV [label="DC Input"];
        INV -> ACDB [label="AC Output"];
        ACDB -> LOAD [label="AC Line"];
    }}
    """
    
    st.graphviz_chart(dot_code)
    st.info("ℹ️ **BNBC Standard Notice:** All DC lines must include DC SPD (Surge Protection Device) and Isolator Switch before Inverter." if lang == "English" else "ℹ️ **BNBC মানদণ্ড সতর্কতা:** ইনভার্টারের পূর্বে প্রতিটি ডিসি লাইনে ডিসি এসপিডি (সুরক্ষা ডিভাইস) এবং আইসোলেটর সুইচ থাকা বাধ্যতামূলক।")

# --- TAB 2: Cable Sizing & Voltage Drop ---
with eng_tabs[1]:
    st.write("#### Electrical Cable Selection & Voltage Drop Analysis" if lang == "English" else "#### ক্যাবল নির্বাচন ও ভোল্টেজ ড্রপ বিশ্লেষণ")
    col_c1, col_c2 = st.columns(2)
    
    system_voltage = 48 if "With Battery" in system_type else 230
    dc_current = (solar_kwp * 1000) / system_voltage if system_voltage > 0 else 0
    
    with col_c1:
        cable_dist = st.number_input("Cable Distance (Panel to Inverter - Meters):" if lang == "English" else "ক্যাবলের দৈর্ঘ্য (প্যানেল থেকে ইনভার্টার - মিটার):", min_value=5, max_value=150, value=15)
        st.metric(label="Calculated System Current" if lang == "English" else "হিসেবকৃত কারেন্ট", value=f"{dc_current:.2f} A")
        
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
            
        st.metric(label="Recommended Cable Size" if lang == "English" else "সুপারিশকৃত ক্যাবল সাইজ", value=rec_cable)
        st.metric(label="Estimated Voltage Drop (%)" if lang == "English" else "আনুমানিক ভোল্টেজ ড্রপ (%)", value=f"{v_drop_val:.2f}%", 
                  delta="Acceptable (<3%)" if v_drop_val < 3 else "High Loss (>3%)",
                  delta_color="normal" if v_drop_val < 3 else "inverse")

# --- TAB 3: Breaker & Safety ---
with eng_tabs[2]:
    st.write("#### Circuit Breaker & Lightning Protection (LPS)" if lang == "English" else "#### সার্কিট ব্রেকার ও বজ্রপাত সুরক্ষার বিবরণ (BNBC/NFPA-70)")
    ac_amp = (solar_kwp * 1000) / 230
    mcb_rating_val = int(np.ceil(ac_amp * 1.25 / 6) * 6)
    
    cp1, cp2 = st.columns(2)
    with cp1:
        st.markdown("##### ⚡ Circuit Breakers & SPD Ratings" if lang == "English" else "##### ⚡ সার্কিট ব্রেকার ও সুরক্ষার বিবরণ")
        st.write(f"• **AC Main MCB:** `{max(16, mcb_rating_val)} A (C-Curve Single/Double Pole)`")
        st.write(f"• **DC Circuit Breaker:** `{max(16, int(dc_current * 1.25))} A (1000V DC Rated)`")
        st.write(f"• **Surge Protection (SPD):** `Type-II DC & AC SPD Boxes`")
        
    with cp2:
        st.markdown("##### 🌩️ Earthing & Lightning Protection System" if lang == "English" else "##### 🌩️ আর্থিং ও বজ্রপাত সুরক্ষা ব্যবস্থা")
        st.write("• **Earthing Pits:** 2 Independent Pits (Equipment & Lightning)")
        st.write("• **Earthing Wire:** 16 mm² Green Insulated Copper Cable")
        st.write("• **LPS Rod:** Early Streamer Emission (ESE) Terminal Air Rod")

# --- TAB 4: BOQ ---
with eng_tabs[3]:
    st.write("#### Bill of Quantities (BOQ) Summary" if lang == "English" else "#### প্রজেক্ট মালামাল ও খরচের বিবরণী (BOQ)")
    
    boq_items = {
        "Item Description / বিবরণ": [
            f"Solar PV Modules (550W Tier-1)",
            f"Solar Inverter ({max(3, round(inverter_kva))} KVA)",
            "Solar Cable & Armored Wiring",
            "Aluminum Rooftop Mounting Structure",
            "DC/AC Distribution Box + SPD + Breakers",
            "Earthing Rods & Cable Trays",
            "Engineering & Installation Charge"
        ],
        "Qty / পরিমাণ": [
            f"{panels_count} Pcs",
            "1 Unit",
            f"{cable_dist * 2} Meters",
            "1 Set",
            "1 Set",
            "2 Sets",
            "1 Job"
        ],
        "Est. Price (BDT)": [
            panel_cost,
            inverter_cost,
            cable_dist * 2 * 180,
            panels_count * 2500,
            18000,
            14000,
            installation_cost
        ]
    }
    
    df_boq_table = pd.DataFrame(boq_items)
    st.dataframe(df_boq_table, use_container_width=True)
    st.markdown(f"#### **Total Engineering Cost: BDT {df_boq_table['Est. Price (BDT)'].sum():,.0f}**")

st.markdown("---")

# ==========================================
# 9. Live Weather Solar Tracker (City & Map)
# ==========================================
st.subheader("🌦️ Live Weather-Based Solar Tracker" if lang == "English" else "🌦️ লাইভ আবহাওয়া ট্র্যাকার")

track_options = ["Bangladesh City List", "Select Location on Map"] if lang == "English" else ["বাংলাদেশের শহর তালিকা", "ম্যাপ থেকে লোকেশন নিন"]
track_type = st.radio("Select Location Mode:" if lang == "English" else "লোকেশন মোড নির্বাচন করুন:", track_options, horizontal=True)

if track_type in ["Bangladesh City List", "বাংলাদেশের শহর তালিকা"]:
    bd_cities = ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barishal", "Rangpur", "Mymensingh", "Cox's Bazar", "Cumilla", "Gazipur"]
    selected_city = st.selectbox("Select a City in Bangladesh:" if lang == "English" else "বাংলাদেশের শহর বেছে নিন:", bd_cities)
    
    if st.button("Check Live Solar Output" if lang == "English" else "লাইভ সোলার আউটপুট দেখুন"):
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
            w1.metric("Temperature" if lang == "English" else "তাপমাত্রা", f"{temp} °C")
            w2.metric("Cloudiness" if lang == "English" else "মেঘের পরিমাণ", f"{cloudiness}%")
            w3.metric("Condition" if lang == "English" else "আবহাওয়া অবস্থা", weather_desc)
            st.success(f"⚡ **Estimated Live Output for {selected_city}:** {current_kw:.2f} kW (Efficiency: {efficiency*100:.1f}%)" if lang == "English" else f"⚡ **{selected_city}-এর জন্য আনুমানিক উৎপাদন:** {current_kw:.2f} kW (কার্যক্ষমতা: {efficiency*100:.1f}%)")
        else:
            st.error("Error fetching weather data!")

else:
    st.info("🗺️ **Click anywhere on the map to pick a location:**" if lang == "English" else "🗺️ **ম্যাপের যেকোনো স্থানে ক্লিক করে লোকেশন নির্বাচন করুন:**")

    m = folium.Map(location=[23.8103, 90.4125], zoom_start=7)
    folium.LatLngPopup().add_to(m)

    map_data = st_folium(m, height=350, width=700)

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        
        st.write(f"📌 **Selected Location:** Lat {lat:.4f}, Lon {lon:.4f}")
        
        if st.button("Check Live Solar Output for Selected Location" if lang == "English" else "নির্বাচিত এলাকার জন্য লাইভ আউটপুট দেখুন"):
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
                w1.metric("Temperature" if lang == "English" else "তাপমাত্রা", f"{temp} °C")
                w2.metric("Cloudiness" if lang == "English" else "মেঘের পরিমাণ", f"{cloudiness}%")
                w3.metric("Condition" if lang == "English" else "আবহাওয়া অবস্থা", weather_desc)
                st.success(f"⚡ **Estimated Live Output:** {current_kw:.2f} kW (Efficiency: {efficiency*100:.1f}%)" if lang == "English" else f"⚡ **আনুমানিক উৎপাদন:** {current_kw:.2f} kW (কার্যক্ষমতা: {efficiency*100:.1f}%)")
            else:
                st.error("Error fetching weather data for coordinates!")

st.markdown("---")

# ==========================================
# 10. Professional Project Report Generation & Export (WITH SLD DIAGRAM)
# ==========================================
st.subheader("📄 Automated Project Proposal & Report Generator" if lang == "English" else "📄 স্বয়ংক্রিয় প্রজেক্ট প্রপোজাল ও রিপোর্ট জেনারেটর")
st.caption("Generate an official PDF/Print-ready engineering proposal" if lang == "English" else "অফিসিয়াল পিডিএফ/প্রিন্ট উপযোগী ইঞ্জিনিয়ারিং প্রপোজাল তৈরি করুন")

client_name = st.text_input("Client / Project Name:" if lang == "English" else "গ্রাহক/প্রজেক্টের নাম:", value="Solario Demo Project")

if st.button("📥 Generate & View Official Proposal Report" if lang == "English" else "📥 প্রপোজাল রিপোর্ট তৈরি করে দেখুন", use_container_width=True):
    
    # Conditional SVG Battery block for SLD
    battery_svg_block = ""
    if "With Battery" in system_type:
        battery_svg_block = f"""
        <line x1="430" y1="90" x2="430" y2="45" stroke="#F59E0B" stroke-width="2.5"/>
        <line x1="430" y1="45" x2="470" y2="45" stroke="#F59E0B" stroke-width="2.5" marker-end="url(#arrow)"/>
        <g transform="translate(470, 20)">
            <rect x="0" y="0" width="130" height="50" rx="6" fill="#F1F5F9" stroke="#64748B" stroke-width="2"/>
            <text x="65" y="22" font-family="sans-serif" font-size="11" font-weight="bold" fill="#0F172A" text-anchor="middle">Battery Bank</text>
            <text x="65" y="38" font-family="sans-serif" font-size="10" fill="#475569" text-anchor="middle">({battery_ah:.0f} Ah 48V)</text>
        </g>
        """

    # Pure HTML/SVG SLD diagram to embed smoothly into print report
    sld_svg = f"""
    <div style="text-align: center; margin: 20px 0; background: #FFFFFF; padding: 15px; border: 1px solid #CBD5E1; border-radius: 8px;">
        <svg width="100%" height="110" viewBox="0 0 820 110" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#0284C7"/>
                </marker>
            </defs>
            
            <!-- PV Array -->
            <rect x="10" y="20" width="130" height="50" rx="6" fill="#FEF3C7" stroke="#F59E0B" stroke-width="2"/>
            <text x="75" y="42" font-family="sans-serif" font-size="11" font-weight="bold" fill="#78350F" text-anchor="middle">PV Array</text>
            <text x="75" y="58" font-family="sans-serif" font-size="10" fill="#B45309" text-anchor="middle">({solar_kwp:.2f} kWp)</text>
            
            <!-- Arrow 1 -->
            <line x1="140" y1="45" x2="175" y2="45" stroke="#0284C7" stroke-width="2.5" marker-end="url(#arrow)"/>
            <text x="157" y="38" font-family="sans-serif" font-size="8" fill="#64748B" text-anchor="middle">DC</text>
            
            <!-- DC DB -->
            <rect x="180" y="20" width="120" height="50" rx="6" fill="#FDE68A" stroke="#D97706" stroke-width="2"/>
            <text x="240" y="42" font-family="sans-serif" font-size="11" font-weight="bold" fill="#78350F" text-anchor="middle">DCDB + SPD</text>
            <text x="240" y="58" font-family="sans-serif" font-size="10" fill="#92400E" text-anchor="middle">Protection</text>
            
            <!-- Arrow 2 -->
            <line x1="300" y1="45" x2="335" y2="45" stroke="#0284C7" stroke-width="2.5" marker-end="url(#arrow)"/>
            
            <!-- Inverter -->
            <rect x="340" y="20" width="130" height="50" rx="6" fill="#93C5FD" stroke="#2563EB" stroke-width="2"/>
            <text x="405" y="42" font-family="sans-serif" font-size="11" font-weight="bold" fill="#1E3A8A" text-anchor="middle">Solar Inverter</text>
            <text x="405" y="58" font-family="sans-serif" font-size="10" fill="#1E40AF" text-anchor="middle">({max(3, round(inverter_kva))} KVA)</text>
            
            {battery_svg_block}

            <!-- Arrow 3 -->
            <line x1="470" y1="45" x2="505" y2="45" stroke="#0284C7" stroke-width="2.5" marker-end="url(#arrow)"/>
            <text x="487" y="38" font-family="sans-serif" font-size="8" fill="#64748B" text-anchor="middle">AC</text>

            <!-- AC DB -->
            <rect x="510" y="20" width="120" height="50" rx="6" fill="#6EE7B7" stroke="#059669" stroke-width="2"/>
            <text x="570" y="42" font-family="sans-serif" font-size="11" font-weight="bold" fill="#064E3B" text-anchor="middle">ACDB + SPD</text>
            <text x="570" y="58" font-family="sans-serif" font-size="10" fill="#047857" text-anchor="middle">Main Panel</text>
            
            <!-- Arrow 4 -->
            <line x1="630" y1="45" x2="665" y2="45" stroke="#0284C7" stroke-width="2.5" marker-end="url(#arrow)"/>
            
            <!-- Connected Load -->
            <rect x="670" y="20" width="130" height="50" rx="6" fill="#A7F3D0" stroke="#10B981" stroke-width="2"/>
            <text x="735" y="42" font-family="sans-serif" font-size="11" font-weight="bold" fill="#064E3B" text-anchor="middle">Building Load</text>
            <text x="735" y="58" font-family="sans-serif" font-size="10" fill="#047857" text-anchor="middle">({running_watts} W)</text>
        </svg>
    </div>
    """

    report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Solar System Engineering Proposal</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1E293B; margin: 20px; }}
            .header {{ text-align: center; border-bottom: 3px solid #F59E0B; padding-bottom: 10px; margin-bottom: 20px; }}
            .title {{ font-size: 24px; font-weight: bold; color: #0F172A; margin: 0; }}
            .subtitle {{ font-size: 14px; color: #64748B; margin-top: 5px; }}
            .section-title {{ font-size: 16px; font-weight: bold; color: #F59E0B; background: #FEF3C7; padding: 6px 10px; border-left: 4px solid #F59E0B; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
            th, td {{ border: 1px solid #CBD5E1; padding: 8px 12px; text-align: left; }}
            th {{ background-color: #F1F5F9; font-weight: bold; }}
            .summary-box {{ display: flex; justify-content: space-between; margin-top: 15px; font-size: 14px; }}
            .summary-card {{ background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px; border-radius: 6px; width: 48%; box-sizing: border-box; }}
            .total-row {{ font-weight: bold; background-color: #FEF3C7; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 11px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">SOLAR ENERGY SYSTEM PROPOSAL</div>
            <div class="subtitle">Solario • Next-Gen Smart Solar CAD & ROI Engine</div>
        </div>
        
        <p><strong>Project / Client:</strong> {client_name}</p>
        <p><strong>System Type:</strong> {system_type}</p>
        
        <div class="section-title">1. System Executive Summary</div>
        <div class="summary-box">
            <div class="summary-card">
                <strong>Connected Load:</strong> {running_watts} W<br>
                <strong>Peak Surge Load:</strong> {surge_watts:.0f} W<br>
                <strong>Daily Energy Consumption:</strong> {daily_kwh:.2f} kWh
            </div>
            <div class="summary-card">
                <strong>Recommended Solar PV:</strong> {solar_kwp:.2f} kWp ({panels_count}x 550W - {panel_brand})<br>
                <strong>Inverter Capacity:</strong> {max(3, round(inverter_kva))} KVA ({inverter_brand})<br>
                <strong>Roof Space Required:</strong> ~{required_roof_sqft} Sq. Ft
            </div>
        </div>

        <div class="section-title">2. Single Line Diagram (SLD)</div>
        {sld_svg}

        <div class="section-title">3. Financial ROI & Savings Estimation</div>
        <table>
            <tr><th>Metric</th><th>Details / Amount</th></tr>
            <tr><td>Total System Budget</td><td><strong>BDT {total_cost:,.0f}</strong></td></tr>
            <tr><td>Estimated Monthly Savings</td><td>BDT {monthly_savings:,.0f} / Month</td></tr>
            <tr><td>Estimated Annual Savings</td><td>BDT {yearly_savings:,.0f} / Year</td></tr>
            <tr><td>Payback Period (ROI)</td><td><strong>~{payback_years:.1f} Years</strong></td></tr>
        </table>

        <div class="section-title">4. Bill of Quantities (BOQ)</div>
        <table>
            <tr>
                <th>Item Description</th>
                <th>Quantity</th>
                <th>Estimated Cost (BDT)</th>
            </tr>
            <tr><td>Solar PV Modules (550W Tier-1)</td><td>{panels_count} Pcs</td><td>BDT {panel_cost:,.0f}</td></tr>
            <tr><td>Solar Inverter ({max(3, round(inverter_kva))} KVA)</td><td>1 Unit</td><td>BDT {inverter_cost:,.0f}</td></tr>
            <tr><td>Solar Cable & Armored Wiring</td><td>{cable_dist * 2} Meters</td><td>BDT {cable_dist * 2 * 180:,.0f}</td></tr>
            <tr><td>Rooftop Mounting Structure</td><td>1 Set</td><td>BDT {panels_count * 2500:,.0f}</td></tr>
            <tr><td>DC/AC Protection Boxes + SPD + Breakers</td><td>1 Set</td><td>BDT 18,000</td></tr>
            <tr><td>Earthing Rods & Cable Trays</td><td>2 Sets</td><td>BDT 14,000</td></tr>
            <tr><td>Engineering & Installation Charge</td><td>1 Job</td><td>BDT {installation_cost:,.0f}</td></tr>
            <tr class="total-row">
                <td colspan="2">Total Project Cost</td>
                <td>BDT {df_boq_table['Est. Price (BDT)'].sum():,.0f}</td>
            </tr>
        </table>

        <div class="section-title">5. Engineering Standards & Compliance</div>
        <p style="font-size: 12px; color: #475569;">
            • Compliant with BNBC-2020 & NFPA-70 (NEC) guidelines.<br>
            • Dual earthing protection system for equipment and lightning arrestor.<br>
            • Voltage drop kept within 3% limit for optimal generation efficiency.
        </p>

        <div class="footer">
            Generated via Solario CAD Engine • Designed by Mohammad Sohel
        </div>
    </body>
    </html>
    """

    st.markdown("### 📜 Official Proposal Preview")
    st.components.v1.html(report_html, height=650, scrolling=True)

    st.download_button(
        label="📥 Download HTML Report (Print to PDF)" if lang == "English" else "📥 রিপোর্ট ডাউনলোড করুন (পিডিএফ প্রিন্ট করুন)",
        data=report_html,
        file_name=f"Solar_Proposal_{client_name.replace(' ', '_')}.html",
        mime="text/html"
    )

# ==========================================
# 11. Footer Section
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
