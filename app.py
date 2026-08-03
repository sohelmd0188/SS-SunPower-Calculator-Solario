import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import pydeck as pdk
import folium
from streamlit_folium import st_folium
import requests

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Smart Solar Calculator & CAD",
    page_icon="☀️",
    layout="wide"
)

# --- LANGUAGE SELECTION ---
lang = st.sidebar.radio("🌐 Select Language / ভাষা নির্বাচন করুন", ["English", "বাংলা"])

# --- TITLE & SUBTITLE ---
if lang == "English":
    st.title("☀️ Smart Solar Dashboard & Rooftop CAD")
    st.markdown("Calculate load, estimate financial ROI, simulate 2D/3D solar placement, and view live solar generation.")
else:
    st.title("☀️ স্মার্ট সোলার ড্যাশবোর্ড এবং রুফটপ ক্যাড")
    st.markdown("লোড হিসাব করুন, খরচ ও সেভিংস জানুন, ছাদের ওপর ২ডি/৩ডি সোলার বসান এবং লাইভ ওয়েদার ট্র্যাক করুন।")

st.markdown("---")

# --- 2. APPLIANCE LOAD CALCULATOR ---
st.header("⚡ 1. Appliance Load Calculation" if lang == "English" else "⚡ ১. হোম ও কমার্শিয়াল অ্যাপ্লায়েন্স লোড হিসাব")

col1, col2 = st.columns([2, 1])

with col1:
    default_appliances = [
        {"name": "LED Bulb", "watts": 15, "qty": 8, "hours": 8},
        {"name": "Ceiling Fan", "watts": 75, "qty": 5, "hours": 12},
        {"name": "Refrigerator", "watts": 200, "qty": 1, "hours": 24},
        {"name": "Television", "watts": 100, "qty": 1, "hours": 5},
        {"name": "AC (1.5 Ton Inverter)", "watts": 1500, "qty": 1, "hours": 6},
        {"name": "Water Pump (1 HP)", "watts": 750, "qty": 1, "hours": 1},
    ]
    df_load = pd.DataFrame(default_appliances)
    edited_df = st.data_editor(df_load, num_rows="dynamic", key="load_editor")

# Calculations
edited_df["Total Watts"] = edited_df["watts"] * edited_df["qty"]
edited_df["Daily kWh"] = (edited_df["Total Watts"] * edited_df["hours"]) / 1000

total_running_watts = edited_df["Total Watts"].sum()
total_daily_kwh = edited_df["Daily kWh"].sum()

# Surge Factor Estimation
surge_capacity = total_running_watts * 1.25

with col2:
    st.metric(label="Total Running Load" if lang == "English" else "মোট রানিং লোড", value=f"{total_running_watts:,.0f} W")
    st.metric(label="Peak/Surge Capacity Needed" if lang == "English" else "ইনভার্টার পিক ক্যাপাসিটি", value=f"{surge_capacity:,.0f} W")
    st.metric(label="Daily Energy Consumption" if lang == "English" else "দৈনিক মোট বিদ্যুৎ ব্যবহার", value=f"{total_daily_kwh:.2f} kWh")

st.markdown("---")

# --- 3. SYSTEM SPECIFICATIONS & CONFIGURATION ---
st.header("⚙️ 2. System Specifications & Brand Selection" if lang == "English" else "⚙️ ২. সোলার সিস্টেম ও ব্র্যান্ড কনফিগারেশন")

sc1, sc2, sc3 = st.columns(3)

with sc1:
    system_type = st.selectbox("Select System Type", ["On-Grid (Grid-Tied)", "Hybrid (Grid + Battery Backup)", "Off-Grid (Standalone Battery)"])
    sunlight_hours = st.slider("Average Peak Sun Hours (Bangladesh Avg: 4.5)", 3.0, 6.0, 4.5, 0.1)

with sc2:
    panel_wattage = st.selectbox("Solar Panel Wattage", [450, 550, 650], index=1)
    panel_brand = st.selectbox("Panel Brand (Tier-1)", ["Longi Solar", "Jinko Solar", "Canadian Solar", "JA Solar", "Standard Brand"])

with sc3:
    inverter_brand = st.selectbox("Inverter Brand", ["Growatt", "Deye", "Huawei", "GoodWe", "Must Solar"])
    battery_type = st.selectbox("Battery Storage Type", ["LiFePO4 Lithium (Recommended)", "Tubular Lead-Acid", "No Battery (On-Grid)"])

# Required System Size Logic
required_kw = (total_daily_kwh / sunlight_hours) * 1.2  # 20% system efficiency loss factor
panels_count = int(np.ceil((required_kw * 1000) / panel_wattage))
actual_system_kw = (panels_count * panel_wattage) / 1000

st.info(f"💡 Recommended System Size: **{actual_system_kw:.2f} kWp** ({panels_count} Panels of {panel_wattage}W each)" if lang == "English" else f"💡 আপনার জন্য রেকমেন্ডেড সিস্টেম সাইজ: **{actual_system_kw:.2f} কিলোওয়াট** (মোট **{panels_count}টি** {panel_wattage}W প্যানেল)")

st.markdown("---")

# --- 4. COST & FINANCIAL ROI ESTIMATION ---
st.header("💰 3. Cost Breakdown & ROI Analysis" if lang == "English" else "💰 ৩. খরচ এবং পে-ব্যাক পিরিয়ড (ROI) হিসেব")

# Market Baseline Pricing Logic (BDT)
panel_price_per_watt = 28 if panel_brand != "Standard Brand" else 25
panel_cost = actual_system_kw * 1000 * panel_price_per_watt

# Inverter Costing
if actual_system_kw <= 3.5:
    inverter_cost = 55000
elif actual_system_kw <= 5.5:
    inverter_cost = 85000
else:
    inverter_cost = 120000

# Battery Costing
if "No Battery" in battery_type:
    battery_cost = 0
elif "Lithium" in battery_type:
    battery_cost = 130000 * max(1, int(actual_system_kw / 3))
else:
    battery_cost = 75000 * max(1, int(actual_system_kw / 3))

# Structure & Installation (10%)
structure_installation = (panel_cost + inverter_cost + battery_cost) * 0.10
total_setup_cost = panel_cost + inverter_cost + battery_cost + structure_installation

# Financial Savings Calculation
electricity_rate = 9.50 # BDT per kWh (Avg Commercial/Residential)
monthly_savings = total_daily_kwh * 30 * electricity_rate
yearly_savings = monthly_savings * 12
payback_years = total_setup_cost / yearly_savings if yearly_savings > 0 else 0

fc1, fc2, fc3, fc4 = st.columns(4)
fc1.metric("Est. Total Investment", f"৳ {total_setup_cost:,.0f}")
fc2.metric("Monthly Utility Savings", f"৳ {monthly_savings:,.0f}")
fc3.metric("Yearly Utility Savings", f"৳ {yearly_savings:,.0f}")
fc4.metric("Estimated ROI Payback Period", f"{payback_years:.1f} Years / বছর")

# Cost Pie Chart
cost_data = pd.DataFrame({
    'Component': ['Solar Panels', 'Inverter System', 'Battery Bank', 'Installation & Structure'],
    'Cost': [panel_cost, inverter_cost, battery_cost, structure_installation]
})
fig_cost = px.pie(cost_data, values='Cost', names='Component', title="Setup Investment Breakdown (BDT)", hole=0.4)
st.plotly_chart(fig_cost, use_container_width=True)

st.markdown("---")

# --- 5. ROOFTOP SPACE & CAD VISUALIZATION ---
st.header("📐 4. Rooftop Solar CAD & 2D/3D Placement" if lang == "English" else "📐 ৪. ছাদের মাপ ও প্যানেল প্লেসমেন্ট ভিজ্যুয়ালাইজেশন")

cad_mode = st.radio("Select Visualization View", ["Level 1: 2D Rooftop Blueprint Layout", "Level 2: 3D Interactive Building CAD", "Level 3: Real Satellite Interactive Solar Placement"], horizontal=True)

roof_width = st.slider("Rooftop Width (Feet)", 15, 100, 30)
roof_length = st.slider("Rooftop Length (Feet)", 20, 150, 50)

cols = max(1, int(roof_width / 3.5))
rows = int(np.ceil(panels_count / cols))

# --- LEVEL 1: 2D Blueprint ---
if "Level 1" in cad_mode:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_facecolor("#0F172A")
    fig.patch.set_facecolor("#0F172A")
    
    # Roof boundary
    ax.plot([0, roof_width, roof_width, 0, 0], [0, 0, roof_length, roof_length, 0], color='#38BDF8', lw=3)
    
    # Panel Placement Rectangles
    placed = 0
    p_w, p_h = 3.2, 6.5 # Approx panel dimensions in feet
    for r in range(rows):
        for c in range(cols):
            if placed < panels_count:
                x = 2 + (c * (p_w + 1))
                y = 2 + (r * (p_h + 1))
                if x + p_w <= roof_width and y + p_h <= roof_length:
                    rect = plt.Rectangle((x, y), p_w, p_h, facecolor='#0284C7', edgecolor='#BAE6FD', alpha=0.85)
                    ax.add_patch(rect)
                    ax.text(x + p_w/2, y + p_h/2, f"P{placed+1}", color='white', ha='center', va='center', fontsize=7)
                    placed += 1

    ax.set_xlim(-5, roof_width + 5)
    ax.set_ylim(-5, roof_length + 5)
    ax.set_title(f"2D Blueprint Layout ({placed}/{panels_count} Panels Placed)", color='white')
    ax.tick_params(colors='white')
    st.pyplot(fig)

# --- LEVEL 2: 3D Interactive Building CAD ---
elif "Level 2" in cad_mode:
    st.write("🌌 **Interactive 3D Rooftop Solar Model** (Rotate & Zoom using Mouse)")
    
    lat = 23.8103
    lon = 90.4125
    
    # Building Polygon Data
    building_data = pd.DataFrame([{
        "coordinates": [
            [lon - 0.0001, lat - 0.0001],
            [lon + 0.0001, lat - 0.0001],
            [lon + 0.0001, lat + 0.0001],
            [lon - 0.0001, lat + 0.0001]
        ],
        "height": 25
    }])
    
    # Solar Panels Grid on top of the building
    panels_3d = []
    for r in range(rows):
        for c in range(cols):
            p_lat = lat - 0.00008 + (r * 0.00003)
            p_lon = lon - 0.00008 + (c * 0.00003)
            panels_3d.append({"position": [p_lon, p_lat, 26]})
            
    panels_3d_df = pd.DataFrame(panels_3d)

    layer_building = pdk.Layer(
        "PolygonLayer",
        building_data,
        get_polygon="coordinates",
        get_elevation="height",
        get_fill_color=[50, 65, 85, 200],
        extruded=True,
    )

    layer_panels = pdk.Layer(
        " ScatterplotLayer",
        panels_3d_df,
        get_position="position",
        get_color=[2, 132, 199, 255],
        get_radius=1.5,
    )

    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=18, pitch=55, bearing=30)
    st.pydeck_chart(pdk.Deck(layers=[layer_building, layer_panels], initial_view_state=view_state))

# --- LEVEL 3: Real Satellite Interactive Solar Placement ---
elif "Level 3" in cad_mode:
    st.info("🗺️ **How to use:** Enter coordinates or zoom into the Satellite Map and **CLICK on your roof** to place the solar panels!" if lang == "English" else f"🗺️ **ব্যবহারের নিয়ম:** ল্যাটিটিউড-লংটিটিউড দিন অথবা ম্যাপে ছাদের ওপর **ক্লিক করুন**। সাথে সাথে {panels_count}টি সোলার প্যানেল ছাদের ওপর বসে যাবে!")
    
    c1, c2 = st.columns(2)
    base_lat = c1.number_input("Latitude", value=23.8103, format="%.6f", key="sat_lat")
    base_lon = c2.number_input("Longitude", value=90.4125, format="%.6f", key="sat_lon")

    # Create Map object centered at user input
    sat_map = folium.Map(
        location=[base_lat, base_lon], 
        zoom_start=19, 
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
        attr='Google Satellite'
    )

    # Interactive Satellite Map Selection
    sat_data = st_folium(sat_map, height=500, width=900, key="sat_map_input")

    click_lat, click_lon = base_lat, base_lon
    is_clicked = False

    if sat_data and sat_data.get("last_clicked"):
        click_lat = sat_data["last_clicked"]["lat"]
        click_lon = sat_data["last_clicked"]["lng"]
        is_clicked = True

    st.markdown("---")
    
    # Render the Visualization Map with Solar Panels Placed
    st.subheader("📍 Rooftop Solar Placement View" if lang == "English" else "📍 ছাদে সোলার প্যানেল প্লেসমেন্ট ভিউ")
    
    viz_map = folium.Map(
        location=[click_lat, click_lon], 
        zoom_start=20, 
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
        attr='Google Satellite'
    )

    # Add red pin marker on chosen location
    folium.Marker(
        [click_lat, click_lon], 
        tooltip="Selected Roof Center",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(viz_map)

    # Draw Blue Solar Panels Grid on top of satellite roof
    placed_count = 0
    for r in range(rows):
        for c in range(cols):
            if placed_count < panels_count:
                # Offset calculation for centered layout
                p_lat = click_lat + ((r - rows/2) * 0.000025)
                p_lon = click_lon + ((c - cols/2) * 0.000025)
                
                bounds = [[p_lat, p_lon], [p_lat + 0.000020, p_lon + 0.000020]]
                
                folium.Rectangle(
                    bounds=bounds,
                    color="#38BDF8",
                    fill=True,
                    fill_color="#0284C7",
                    fill_opacity=0.85,
                    popup=f"Solar Panel #{placed_count + 1} (550W)",
                    tooltip=f"Panel #{placed_count + 1}"
                ).add_to(viz_map)
                placed_count += 1

    # Display Final Visualized Map with unique key
    st_folium(viz_map, height=500, width=900, key=f"viz_map_{click_lat}_{click_lon}")
    
    if is_clicked:
        st.success(f"🎉 **{placed_count} Solar Panels placed at Coordinates:** Lat `{click_lat:.6f}`, Lon `{click_lon:.6f}`")
    else:
        st.info("💡 Click on your rooftop above to position the solar panel layout!" if lang == "English" else "💡 আপনার ছাদের সঠিক স্থানে প্যানেল বসাতে ওপরের ম্যাপে ক্লিক করুন!")

st.markdown("---")

# --- 6. 24-HOUR GENERATION SIMULATION ---
st.subheader("📊 24-Hour Solar Generation Simulation" if lang == "English" else "📊 ২৪ ঘণ্টার সৌর বিদ্যুৎ উৎপাদন গ্রাফ")
hours = list(range(24))
generation_curve = [0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.85, 0.95, 1.0, 0.98, 0.90, 0.75, 0.5, 0.2, 0.05, 0, 0, 0, 0, 0, 0, 0]
hourly_power_kw = [g * actual_system_kw for g in generation_curve]

df_gen = pd.DataFrame({"Hour of Day": hours, "Solar Output (kW)": hourly_power_kw})
fig_gen = px.area(df_gen, x="Hour of Day", y="Solar Output (kW)", title="Daily Power Generation Profile (kW)", color_discrete_sequence=['#F59E0B'])
st.plotly_chart(fig_gen, use_container_width=True)

st.markdown("---")

# --- 7. REAL-TIME WEATHER & SOLAR TRACKER (OPENWEATHER API) ---
st.header("🌤️ 5. Live Weather Solar Power Estimator" if lang == "English" else "🌤️ ৫. লাইভ আবহাওয়া ও রিয়েল-টাইম সোলার জেনারেটর")

city = st.text_input("Enter City for Real-Time Weather Check", "Dhaka")
api_key = "bd5e378503939ddaee76f12ad7a97608" # Demo OpenWeather Key

if st.button("Fetch Real-Time Solar Estimate"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url).json()
        
        if res.get("cod") == 200:
            temp = res["main"]["temp"]
            clouds = res["clouds"]["all"]
            weather_desc = res["weather"][0]["description"].capitalize()
            
            # Weather Efficiency Calculation Logic
            cloud_efficiency = (100 - (clouds * 0.7)) / 100
            temp_efficiency = 1.0 - max(0, (temp - 25) * 0.004) # 0.4% loss per degree above 25°C
            total_efficiency = cloud_efficiency * temp_efficiency
            
            live_power_output = actual_system_kw * total_efficiency
            
            w1, w2, w3, w4 = st.columns(4)
            w1.metric("Temperature", f"{temp} °C")
            w2.metric("Cloud Coverage", f"{clouds} %")
            w3.metric("System Efficiency", f"{total_efficiency*100:.1f} %")
            w4.metric("Live Estimated Generation", f"{live_power_output:.2f} kW")
            
            st.success(f"Weather Condition in **{city}**: {weather_desc}")
        else:
            st.error("City not found. Please check spelling.")
    except Exception as e:
        st.error(f"Could not retrieve weather data: {e}")

# Footer
st.markdown("---")
st.caption("Developed by **Mohammad Sohel** | Smart Solar Dashboard & Rooftop CAD System")
