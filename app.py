import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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
}
div[data-testid="stMetricValue"] {
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
}
.hero-container {
    background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                url('https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?q=80&w=1200&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    border-radius: 16px;
    padding: 35px 25px;
    margin-bottom: 25px;
    border: 1px solid rgba(245, 158, 11, 0.4);
}
.hero-title { color: #FFFFFF !important; font-size: 2.2rem !important; font-weight: 800 !important; margin-bottom: 8px !important; }
.hero-subtitle { color: #E2E8F0 !important; font-size: 1.05rem !important; }
.hero-badge {
    display: inline-block; background-color: #F59E0B; color: #0F172A !important;
    font-weight: 700; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Header Section & Language Option
# ==========================================
lang = st.radio("🌐 Language / ভাষা:", ["English", "বাংলা"], horizontal=True)

if lang == "English":
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ SOLAR CAD & ANALYTICS</span>
        <div class="hero-title">Solario • Next-Gen Smart Solar CAD & ROI Engine </div>
        <div class="hero-subtitle">Advanced calculations with Multi-Level CAD Blueprint, Pydeck 3D Model, Satellite Roof Mapping, and BOQ Projections.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ সোলার ক্যাড ও অ্যানালিটিক্স</span>
        <div class="hero-title">স্মার্ট বাণিজ্যিক সোলার ক্যালকুলেটর ও ড্যাশবোর্ড</div>
        <div class="hero-subtitle">মাল্টি-লেভেল ক্যাড ব্লুপ্রিন্ট, থ্রিডি পাইডেক ماডেল, স্যাটেলাইট ম্যাপ প্লেসমেন্ট এবং প্রফেশনাল প্রপোজাল সমেত সম্পূর্ণ সিস্টেম।</div>
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
        "Electric Oven / Baking Oven (2000W)": {"watt": 2000, "qty": 1, "type": "heavy", "hours": 1.0},
        "1 HP Submersible Pump (750W)": {"watt": 750, "qty": 1, "type": "heavy", "hours": 1.5}
    }

EXTRA_APPLIANCES = {
    "1.5 Ton Inverter AC (1500W)": {"watt": 1500, "type": "heavy", "default_hours": 6.0},
    "1 Ton Non-Inverter AC (1200W)": {"watt": 1200, "type": "heavy", "default_hours": 6.0},
    "2 Ton AC (2200W)": {"watt": 2200, "type": "heavy", "default_hours": 6.0},
    "0.5 HP Water Motor / Pump (375W)": {"watt": 375, "type": "heavy", "default_hours": 1.0},
    "1 HP Water Motor / Pump (750W)": {"watt": 750, "type": "heavy", "default_hours": 1.0},
    "1.5 HP Submersible Pump (1100W)": {"watt": 1100, "type": "heavy", "default_hours": 1.5},
    "2 HP Deep Tubewell Motor (1500W)": {"watt": 1500, "type": "heavy", "default_hours": 1.5},
    "Microwave Oven (1200W)": {"watt": 1200, "type": "heavy", "default_hours": 0.5},
    "Electric Oven / Baking Oven (2000W)": {"watt": 2000, "type": "heavy", "default_hours": 1.0},
    "Washing Machine (500W)": {"watt": 500, "type": "heavy", "default_hours": 1.0},
    "Geyser / Water Heater (2000W)": {"watt": 2000, "type": "heavy", "default_hours": 1.0},
    "Computer / Desktop (250W)": {"watt": 250, "type": "regular", "default_hours": 8.0},
    "Laptop Charger (65W)": {"watt": 65, "type": "regular", "default_hours": 8.0},
    "Iron Box (1000W)": {"watt": 1000, "type": "heavy", "default_hours": 0.5},
    "Induction Cooker (1800W)": {"watt": 1800, "type": "heavy", "default_hours": 2.0}
}

st.sidebar.header("🔌 1. Appliance Quantities & Load" if lang == "English" else "🔌 ১. সরঞ্জামের পরিমাণ ও লোড")

# Regular Loads Section
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

st.sidebar.markdown("---")

# Heavy Loads Section
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
            if st.button("🗑️", key=f"del_heavy_{app_name}", help=f"Remove {app_name}"):
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
system_type = st.sidebar.radio("Select System Type:" if lang == "English" else "সিস্টেম টাইপ:", ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"])
panel_brand = st.sidebar.selectbox("Solar Panel Brand:" if lang == "English" else "প্যানেল ব্র্যান্ড:", ["Longi Solar (Tier-1)", "Jinko Solar (Tier-1)", "Standard"])
inverter_brand = st.sidebar.selectbox("Inverter Brand:" if lang == "English" else "ইনভার্টার ব্র্যান্ড:", ["Growatt", "Deye", "Huawei"])

if "With Battery" in system_type:
    battery_type = st.sidebar.selectbox("Battery Chemistry:" if lang == "English" else "ব্যাটারি কেমিক্যাল টাইপ:", ["LiFePO4 Lithium Battery (90% DoD)", "Tubular Lead-Acid Battery (70% DoD)"])
    autonomy_hours = st.sidebar.slider("Battery Backup Hours (Autonomy):" if lang == "English" else "ব্যাটারি ব্যাকআপ আওয়ার্স:", 1, 12, 4)
else:
    autonomy_hours = 0

tilt_angle = st.sidebar.slider("Panel Tilt Angle (Degrees):" if lang == "English" else "প্যানেল টিল্ট অ্যাঙ্গেল (ডিগ্রী):", 0, 45, 23)
shading_loss_pct = st.sidebar.slider("Shading & Dust Loss (%):" if lang == "English" else "ছায়া ও ধূলিমলিনতা লস (%):", 0, 30, 15)
roof_sqft = st.sidebar.number_input("Available Roof Area (Sq. Ft):" if lang == "English" else "খালি ছাদের আয়তন (বর্গফুট):", min_value=0, value=800)
brand_multiplier = 1.15 if "Tier-1" in panel_brand or "Huawei" in inverter_brand else 1.0

# ==========================================
# 4. Core Calculations with Detailed Factors
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
    
    if app_type == "regular":
        used_hrs = avg_running_hours
    else:
        used_hrs = app_data.get("hours", 1.0)
        
    daily_wh += total_app_watt * used_hrs
    surge_watts += total_app_watt * (3.0 if "Motor" in app_name or "Pump" in app_name else (2.0 if "AC" in app_name or "Refrigerator" in app_name else 1.0))

daily_kwh = daily_wh / 1000.0
inverter_kva = (surge_watts * 1.25) / 1000

tilt_efficiency_factor = 1.0 - abs(tilt_angle - 23) * 0.005
net_loss_multiplier = (1.0 - (shading_loss_pct / 100.0)) * tilt_efficiency_factor

solar_kwp = (daily_wh / 4.0 / max(0.5, net_loss_multiplier)) / 1000 if daily_wh > 0 else 0
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0
required_roof_sqft = math.ceil(solar_kwp * 100)

panel_cost = (panels_count * 550) * (28 * brand_multiplier if "Tier-1" in panel_brand else 25)
inverter_cost = 75000 * brand_multiplier if inverter_kva > 3 else 50000 * brand_multiplier

if "With Battery" in system_type:
    dod_rate = 0.9 if "LiFePO4" in battery_type else 0.7
    battery_ah = (daily_wh * (autonomy_hours / 24.0)) / (48 * dod_rate)
    battery_cost = (battery_ah / 100) * (130000 if "LiFePO4" in battery_type else 75000)
else:
    battery_ah = 0
    battery_cost = 0

subtotal = panel_cost + inverter_cost + battery_cost
installation_cost = subtotal * 0.10
total_cost = subtotal + installation_cost

electricity_rate = 10.0 
monthly_savings = daily_kwh * 30 * electricity_rate
yearly_savings = monthly_savings * 12
payback_years = total_cost / yearly_savings if yearly_savings > 0 else 0

# ==========================================
# 5. UI Metrics Dashboard
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load" if lang == "English" else "চলমান লোড", f"{running_watts} W")
col2.metric("System Size" if lang == "English" else "সোলার সিস্টেম", f"{solar_kwp:.2f} kWp")
col3.metric("Monthly Savings" if lang == "English" else "মাসিক সাশ্রয়", f"BDT {monthly_savings:,.0f}")
col4.metric("Total Investment" if lang == "English" else "মোট বাজেট", f"BDT {total_cost:,.0f}")

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
        base_lat = c1.number_input("Latitude", value=22.3569, format="%.4f")
        base_lon = c2.number_input("Longitude", value=91.7832, format="%.4f")

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
        base_lat = c1.number_input("Latitude", value=22.3569, format="%.6f", key="sat_lat")
        base_lon = c2.number_input("Longitude", value=91.7832, format="%.6f", key="sat_lon")

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
st.markdown("<div style='text-align: center; color: #94A3B8;'>Designed by <b>Mohammad Sohel</b></div>", unsafe_allow_html=True)
