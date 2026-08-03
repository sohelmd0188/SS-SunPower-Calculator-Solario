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
    page_title="Smart Solar Dashboard & Calculator (Solario)",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern UI & Universal Contrast
st.markdown("""
<style>
.main { background-color: #F8FAFC; }

/* Metric Box Styling with Dark Text */
div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border-radius: 12px;
    padding: 10px 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #F59E0B;
}

div[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    word-break: break-word !important;
}

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

/* Universal Hero Banner */
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
        <div class="hero-title">Smart Commercial Solar Calculator & Dashboard</div>
        <div class="hero-subtitle">Calculate household/industrial solar load, ROI, equipment brands, and real-time solar output.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ সোলার ক্যাড ও অ্যানালিটিক্স</span>
        <div class="hero-title">স্মার্ট বাণিজ্যিক সোলার ক্যালকুলেটর ও ড্যাশবোর্ড</div>
        <div class="hero-subtitle">বাসাবাড়ি বা শিল্প প্রতিষ্ঠানের সোলার লোড, আনুমানিক খরচ, ব্র্যান্ড ও রিয়েল-টাইম বিদ্যুৎ উৎপাদন হিসেব করুন।</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. Sidebar Inputs & Dynamic Appliance System
# ==========================================

# Initialize Session State Appliances
if "appliance_list" not in st.session_state:
    st.session_state.appliance_list = {
        "Ceiling Fan (75W)": {"watt": 75, "qty": 5},
        "LED Light (15W)": {"watt": 15, "qty": 10},
        "Refrigerator (200W)": {"watt": 200, "qty": 1},
        "Smart TV (80W)": {"watt": 80, "qty": 1},
        "Oven (1200W)": {"watt": 1200, "qty": 1},
        "1 HP Submersible Pump (750W)": {"watt": 750, "qty": 1}
    }

# Extra appliances list for dropdown
EXTRA_APPLIANCES = {
    "1.5 Ton Inverter AC (1500W)": 1500,
    "1 Ton Non-Inverter AC (1200W)": 1200,
    "2 Ton AC (2200W)": 2200,
    "Washing Machine (500W)": 500,
    "Geyser / Water Heater (2000W)": 2000,
    "Microwave Oven (1000W)": 1000,
    "Computer / Desktop (250W)": 250,
    "Laptop Charger (65W)": 65,
    "Iron Box (1000W)": 1000,
    "Induction Cooker (1800W)": 1800
}

st.sidebar.header("🔌 1. Appliance Quantities & Load" if lang == "English" else "🔌 ১. সরঞ্জামের পরিমাণ ও লোড")

# Option to add extra appliance
st.sidebar.subheader("➕ Add Extra Appliance" if lang == "English" else "➕ অতিরিক্ত ডিভাইস যুক্ত করুন")
selected_extra = st.sidebar.selectbox(
    "Select Appliance:" if lang == "English" else "ডিভাইস বেছে নিন:",
    options=list(EXTRA_APPLIANCES.keys()),
    key="selected_extra_appliance"
)

if st.sidebar.button("➕ Add to List" if lang == "English" else "➕ তালিকা যুক্ত করুন", use_container_width=True):
    if selected_extra not in st.session_state.appliance_list:
        watt_value = EXTRA_APPLIANCES[selected_extra]
        st.session_state.appliance_list[selected_extra] = {"watt": watt_value, "qty": 1}
        st.sidebar.success(f"Added {selected_extra}!")
        st.rerun()
    else:
        st.sidebar.warning("Already in your list!" if lang == "English" else "ইতিমধ্যে তালিকায় আছে!")

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Active Appliances" if lang == "English" else "📝 বর্তমান ব্যবহারের তালিকা")

# Render active appliances dynamically
for app_name, app_data in list(st.session_state.appliance_list.items()):
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

st.sidebar.markdown("---")
st.sidebar.header("⏱️ 2. Daily Usage (Hours)" if lang == "English" else "⏱️ ২. দৈনিক ব্যবহার (ঘণ্টা)")
avg_running_hours = st.sidebar.slider("Avg Daily Running Hours" if lang == "English" else "দৈনিক গড় ব্যবহার (ঘণ্টা)", 1, 24, 8)

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
st.sidebar.header("🏠 Roof Area Calculator" if lang == "English" else "🏠 ছাদের আয়তন দিয়ে হিসেব")
roof_sqft = st.sidebar.number_input("Available Roof Area (Sq. Ft):" if lang == "English" else "খালি ছাদের আয়তন (বর্গফুট):", min_value=0, value=300)
max_possible_kwp = (roof_sqft / 100) * 1.0

# ==========================================
# 4. Backend Calculations & Dynamic ROI
# ==========================================
running_watts = 0
surge_watts = 0

for app_name, app_data in st.session_state.appliance_list.items():
    qty = app_data["qty"]
    watt = app_data["watt"]
    running_watts += watt * qty
    
    if "Refrigerator" in app_name:
        surge_watts += watt * qty * 2.5
    elif "Pump" in app_name:
        surge_watts += watt * qty * 3.0
    elif "AC" in app_name:
        surge_watts += watt * qty * 1.5
    else:
        surge_watts += watt * qty

daily_wh = running_watts * avg_running_hours
daily_kwh = daily_wh / 1000.0

inverter_kva = (surge_watts * 1.25) / 1000
solar_kwp = (daily_wh / 4.0 / 0.85) / 1000 if daily_wh > 0 else 0
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0

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
        st.warning(f"⚠️ **Roof Space Notice:** Your required system ({solar_kwp:.2f} kWp) needs ~{solar_kwp*100:.0f} Sq. Ft. Your roof is {roof_sqft} Sq. Ft (Max capacity: ~{max_possible_kwp:.2f} kWp).")
    else:
        st.warning(f"⚠️ **ছাদের জায়গার সতর্কতা:** আপনার প্রয়োজনীয় সিস্টেমের ({solar_kwp:.2f} kWp) জন্য অন্তত ~{solar_kwp*100:.0f} বর্গফুট ছাদ প্রয়োজন। আপনার দেওয়া ছাদের ক্ষেত্রফল {roof_sqft} বর্গফুট (সর্বোচ্চ ক্ষমতা: ~{max_possible_kwp:.2f} kWp)।")

c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 System Specifications & Brands" if lang == "English" else "📋 যন্ত্রপাতির বিবরণ ও ব্র্যান্ড")
    st.info(f"⚡ **Inverter / ইনভার্টার:** {max(3, round(inverter_kva))} KVA/KW ({inverter_brand})")
    st.info(f"☀️ **Solar Panels / প্যানেল:** {solar_kwp:.2f} kWp ({panels_count}x 550W - {panel_brand})")
    if "With Battery" in system_type:
        st.info(f"🔋 **Battery / ব্যাটারি:** {battery_ah:.0f} Ah 48V ({battery_type})")
    else:
        st.warning("🔋 **Battery:** Not required for On-Grid system." if lang == "English" else "🔋 **ব্যাটারি:** অন-গ্রিড সিস্টেমের জন্য ব্যাটারির প্রয়োজন নেই।")

with c2:
    st.subheader("💰 Cost Breakdown & Financial ROI" if lang == "English" else "💰 আনুমানিক ব্যয় ও সাশ্রয় (ROI)")
    st.write(f"• **Solar Panels ({panel_brand}):** BDT {panel_cost:,.0f}" if lang == "English" else f"• **সোলার প্যানেল ({panel_brand}):** BDT {panel_cost:,.0f}")
    st.write(f"• **Inverter ({inverter_brand}):** BDT {inverter_cost:,.0f}" if lang == "English" else f"• **ইনভার্টার ({inverter_brand}):** BDT {inverter_cost:,.0f}")
    if "With Battery" in system_type:
        st.write(f"• **Battery Bank:** BDT {battery_cost:,.0f}" if lang == "English" else f"• **ব্যাটারি ব্যাকআপ:** BDT {battery_cost:,.0f}")
    st.write(f"• **Installation & Wiring (10%):** BDT {installation_cost:,.0f}" if lang == "English" else f"• **ইনস্টলেশন ও ওয়্যারিং (১০%):** BDT {installation_cost:,.0f}")
    st.write("---")
    st.write(f"💵 **Est. Monthly Savings:** BDT {monthly_savings:,.0f} / month" if lang == "English" else f"💵 **মাসিক আনুমানিক বিল সাশ্রয়:** BDT {monthly_savings:,.0f} / মাস")
    st.write(f"📈 **Estimated Payback Period (ROI):** ~**{payback_years:.1f} Years**" if lang == "English" else f"📈 **মূল্য ফেরত আসার আনুমানিক সময় (ROI):** ~**{payback_years:.1f} বছর**")

st.markdown("---")

# ==========================================
# 6. CAD & Solar Layout Options (Levels 1, 2, 3)
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

    # --- LEVEL 1: Fixed 2D Blueprint ---
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
        title_text = f"2D Blueprint: {placed} Panels Placed ({panels_count} Required)" if lang == "English" else f"২ডি ব্লুপ্রিন্ট: {placed}টি প্যানেল ছাদে বসানো হয়েছে (প্রয়োজন {panels_count}টি)"
        plt.title(title_text, fontsize=10, fontweight='bold', color='#F8FAFC', pad=10)
        st.pyplot(fig, use_container_width=True)

    # --- LEVEL 2: 3D Interactive Model ---
    elif "Level 2" in cad_mode:
        st.write("📍 **Enter your coordinates or use default to generate 3D Building:**" if lang == "English" else "📍 **আপনার ৩ডি বিল্ডিং তৈরির জন্য লোকেশন কোঅর্ডিনেট দিন:**")
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
        st.pydeck_chart(pdk.Deck(layers=[roof_layer, panels_layer], initial_view_state=view_state, tooltip={"text": "Roof & Solar Panel Array"}))

    # --- LEVEL 3: Real Satellite Interactive Solar Placement ---
    elif "Level 3" in cad_mode:
        st.info("🗺️ **How to use:** Enter coordinates or zoom into the Satellite Map and **CLICK on your roof** to place the solar panels!" if lang == "English" else f"🗺️ **ব্যবহারের নিয়ম:** ল্যাটিটিউড-লংটিটিউড দিন অথবা ম্যাপে ছাদের ওপর **ক্লিক করুন**। সাথে সাথে {panels_count}টি সোলার প্যানেল ছাদের ওপর বসে যাবে!")
        
        c1, c2 = st.columns(2)
        base_lat = c1.number_input("Latitude", value=22.376735, format="%.6f", key="sat_lat")
        base_lon = c2.number_input("Longitude", value=91.839035, format="%.6f", key="sat_lon")

        # Base Satellite Map Centered at User Coordinates
        sat_map = folium.Map(
            location=[base_lat, base_lon], 
            zoom_start=20, 
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
            attr='Google Satellite'
        )

        # Interactive Map capturing user clicks
        sat_data = st_folium(sat_map, height=500, width=900, key="sat_map_input")

        click_lat, click_lon = base_lat, base_lon
        is_clicked = False

        if sat_data and sat_data.get("last_clicked"):
            click_lat = sat_data["last_clicked"]["lat"]
            click_lon = sat_data["last_clicked"]["lng"]
            is_clicked = True

        st.markdown("---")
        st.subheader("📍 Rooftop Solar Placement View" if lang == "English" else "📍 ছাদে সোলার প্যানেল প্লেসমেন্ট ভিউ")
        
        # Rendering the Solar Panel Grid on Selected Coordinates
        viz_map = folium.Map(
            location=[click_lat, click_lon], 
            zoom_start=21, 
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
            attr='Google Satellite'
        )

        # Center Roof Pin
        folium.Marker(
            [click_lat, click_lon], 
            tooltip="Selected Roof Location",
            icon=folium.Icon(color="red", icon="home")
        ).add_to(viz_map)

        # Solar Panels Array Drawing
        placed_count = 0
        for r in range(rows):
            for c in range(cols):
                if placed_count < panels_count:
                    # Latitude & Longitude small offsets
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

        # Render Map with unique key to force instant reload on click
        st_folium(viz_map, height=500, width=900, key=f"viz_map_{click_lat}_{click_lon}")
        
        if is_clicked:
            st.success(f"🎉 **{placed_count} Solar Panels placed at Coordinates:** Lat `{click_lat:.6f}`, Lon `{click_lon:.6f}`")
        else:
            st.info("💡 Click on your rooftop above to position the solar panel layout!" if lang == "English" else "💡 আপনার ছাদের সঠিক স্থানে প্যানেল বসাতে ওপরের ম্যাপে ক্লিক করুন!")

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
fig.update_layout(template="plotly_white", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 8. Live Weather Solar Tracker (City & Map)
# ==========================================
st.subheader("🌦️ Live Weather-Based Solar Tracker" if lang == "English" else "🌦️ লাইভ আবহাওয়া ট্র্যাকার")

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
            w3.metric("Condition" if lang == "English" else "আবহাওয়া অবস্থা", weather_desc)
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
                w3.metric("Condition" if lang == "English" else "আবহাওয়া অবস্থা", weather_desc)
                st.success(f"⚡ **Estimated Live Output:** {current_kw:.2f} kW (Efficiency: {efficiency*100:.1f}%)" if lang == "English" else f"⚡ **আনুমানিক উৎপাদন:** {current_kw:.2f} kW (কার্যক্ষমতা: {efficiency*100:.1f}%)")
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
