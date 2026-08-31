import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import math

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
        <div class="hero-subtitle">Advanced calculations with 2D/3D Interactive Map CAD Layout, Weather API, Engineering Studio, Cash Flow, and BOQ Projections.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ সোলার ক্যাড ও অ্যানালিটিক্স</span>
        <div class="hero-title">স্মার্ট বাণিজ্যিক সোলার ক্যালকুলেটর ও ড্যাশবোর্ড</div>
        <div class="hero-subtitle">লাইভ ম্যাপ ইন্টিগ্রেশন, ২ডি/থ্রিডি ক্যাড লেআউট, আবহাওয়া সিমুলেশন, ইঞ্জিনিয়ারিং স্টুডিও, ক্যাশ ফ্লো এবং প্রফেশনাল প্রপোজাল সমেত সম্পূর্ণ সিস্টেম।</div>
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
# 6. Advanced Modules: 24-Hour Simulation & Interactive 2D/3D Map CAD Layout
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 24-Hr Generation / উৎপাদন সিমুলেশন", 
    "🗺️ Interactive Live Map & 2D/3D CAD Layout / লাইভ ম্যাপ ও ক্যাড লেআউট", 
    "⚡ Engineering Studio / ইঞ্জিনিয়ারিং স্টুডিও", 
    "📈 Cash Flow & Proposal / ক্যাশ ফ্লো ও প্রপোজাল"
])

with tab1:
    st.subheader("24-Hour Solar PV Power Generation Curve" if lang == "English" else "২৪ ঘণ্টার সোলার পাওয়ার প্রোডাকশন কার্ভ")
    hours_day = list(range(24))
    generation_curve = [max(0, solar_kwp * 1000 * math.exp(-((h - 13) ** 2) / 10)) for h in hours_day]
    
    df_gen = pd.DataFrame({"Hour": hours_day, "Power (W)": generation_curve})
    fig_gen = px.area(df_gen, x="Hour", y="Power (W)", title="Estimated Daily Power Profile (Watts)" if lang == "English" else "দিনব্যাপী সৌর বিদ্যুৎ উৎপাদনের প্রোফাইল", color_discrete_sequence=['#F59E0B'])
    fig_gen.update_layout(template="plotly_dark")
    st.plotly_chart(fig_gen, use_container_width=True)

with tab2:
    st.subheader("Interactive Live Map Location & 2D/3D Rooftop CAD Layout" if lang == "English" else "লাইভ ম্যাপ লোকেশন ও ২ডি/থ্রিডি ছাদের ক্যাড লেআউট")
    
    # Live Map & Location Setting
    col_map_opt1, col_map_opt2 = st.columns(2)
    with col_map_opt1:
        map_city = st.selectbox("Select Project City / Location:" if lang == "English" else "প্রজেক্টের শহর বা লোকেশন:", 
                                ["Chattogram (Default)", "Dhaka", "Sylhet", "Rajshahi", "Khulna", "Barishal", "Rangpur"])
    with col_map_opt2:
        view_mode = st.radio("Select View Mode:" if lang == "English" else "ভিউ মোড নির্বাচন করুন:", ["2D Top-Down View", "3D Isometric View", "Live Satellite Map Grid"], horizontal=True)

    # City Coordinates mapping for Live Map
    city_coords = {
        "Chattogram (Default)": {"lat": 22.3569, "lon": 91.7832},
        "Dhaka": {"lat": 23.8103, "lon": 90.4125},
        "Sylhet": {"lat": 24.8949, "lon": 91.8687},
        "Rajshahi": {"lat": 24.3745, "lon": 88.6042},
        "Khulna": {"lat": 22.8456, "lon": 89.5403},
        "Barishal": {"lat": 22.7010, "lon": 90.3535},
        "Rangpur": {"lat": 25.7439, "lon": 89.2752}
    }
    lat = city_coords[map_city]["lat"]
    lon = city_coords[map_city]["lon"]

    if view_mode == "Live Satellite Map Grid":
        st.info(f"📍 Showing live map region for **{map_city}** (Lat: {lat}, Lon: {lon}) with simulated rooftop boundaries.")
        df_map = pd.DataFrame({'lat': [lat], 'lon': [lon], 'name': [f"{map_city} Project Rooftop"]})
        st.map(df_map, zoom=14)
    else:
        col_a, col_b = st.columns([1, 1.2])
        with col_a:
            st.info(f"📍 **Required Roof Area:** {required_roof_sqft} Sq. Ft")
            st.info(f"📍 **Available Roof Area:** {roof_sqft} Sq. Ft")
            st.info(f"📐 **Tilt Alignment Angle:** {tilt_angle}° facing South")
            if roof_sqft < required_roof_sqft:
                st.error("⚠️ Warning: Available roof area is less than required!" if lang == "English" else "⚠️ সতর্কবার্তা: উপলব্ধ ছাদের জায়গা প্রয়োজনের তুলনায় কম!")
            else:
                st.success("✅ Roof area is sufficient for this installation capacity." if lang == "English" else "✅ এই সিস্টেমের জন্য ছাদের জায়গা যথেষ্ট রয়েছে।")
        
        with col_b:
            if panels_count > 0:
                cols_grid = max(1, math.ceil(math.sqrt(panels_count)))
                x_coords = [i % cols_grid for i in range(panels_count)]
                y_coords = [i // cols_grid for i in range(panels_count)]
                
                if view_mode == "3D Isometric View":
                    z_coords = [math.sin(math.radians(tilt_angle)) * (i // cols_grid) for i in range(panels_count)]
                    df_cad = pd.DataFrame({"X": x_coords, "Y": y_coords, "Z": z_coords})
                    fig_cad = px.scatter_3d(df_cad, x="X", y="Y", z="Z", title=f"3D Isometric Rooftop Panel Grid ({panels_count} Modules)" if lang == "English" else f"থ্রিডি ছাদের সোলার প্যানেল বিন্যাস ({panels_count} পিস)")
                    fig_cad.update_traces(marker=dict(size=8, color='#F59E0B'))
                else:
                    df_cad = pd.DataFrame({"X": x_coords, "Y": y_coords})
                    fig_cad = px.scatter(df_cad, x="X", y="Y", title=f"2D Top-Down Rooftop Grid ({panels_count} Modules)" if lang == "English" else f"টুডি ছাদের সোলার প্যানেল গ্রিড ({panels_count} পিস)", symbol_sequence=['square'])
                    fig_cad.update_traces(marker=dict(size=16, color='#F59E0B'))
                
                fig_cad.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig_cad, use_container_width=True)

with tab3:
    st.subheader("Advanced Engineering & Protection Studio (BNBC & NFPA)" if lang == "English" else "অ্যাডভান্সড ইঞ্জিনিয়ারিং ও প্রটেকশন স্টুডিও (BNBC ও NFPA মানদণ্ড)")
    col_eng1, col_eng2 = st.columns(2)
    with col_eng1:
        st.markdown("### 🔌 Cable Sizing & Voltage Drop")
        st.write(f"- **DC Cable Recommendation:** 4mm² / 6mm² XLPE Copper Wire (Max 1% Drop)")
        st.write(f"- **AC Cable Recommendation:** 10mm² Copper Cable for Main Inverter Feed")
        st.write(f"- **Estimated Inverter Capacity:** {inverter_kva:.2f} kVA ({inverter_brand})")
    with col_eng2:
        st.markdown("### ⚡ Protection & Earthing (NFPA 780)")
        st.write(f"- **DC Protection:** PV DC Isolator & Surge Protection Device (SPD Type-2)")
        st.write(f"- **AC Protection:** MCB & Residual Current Circuit Breaker (RCCB)")
        st.write(f"- **Earthing System:** Dedicated Copper Earth Rod (Resistance < 5 Ohms)")

with tab4:
    st.subheader("📈 10-Year Net Metering Cash Flow & Proposal" if lang == "English" else "📈 ১০ বছরের নেট মিটারিং ক্যাশ ফ্লো ও প্রপোজাল")
    
    years = list(range(1, 11))
    cumulative_cash_flow = []
    running_cf = -total_cost
    tariff_escalation = 1.05  

    for y in years:
        yearly_benefit = yearly_savings * (tariff_escalation ** (y - 1))
        running_cf += yearly_benefit
        cumulative_cash_flow.append(running_cf)

    df_cashflow = pd.DataFrame({
        'Year': [f"Year {y}" for y in years],
        'Net Cash Flow (BDT)': cumulative_cash_flow
    })

    fig_cf = px.bar(df_cashflow, x='Year', y='Net Cash Flow (BDT)',
                  title="10-Year Cumulative Savings & Net Metering Return" if lang == "English" else "১০ বছরের সঞ্চয় ও নেট মিটারিং রিটার্ন গ্রাফ",
                  color='Net Cash Flow (BDT)', color_continuous_scale=['#EF4444', '#10B981'])
    fig_cf.update_layout(template="plotly_dark")
    st.plotly_chart(fig_cf, use_container_width=True)

    st.markdown("---")
    client_name = st.text_input("Client / Project Name:" if lang == "English" else "গ্রাহক বা প্রজেক্টের নাম:", value="Commercial Solar Client")

    if st.button("📥 Generate Printable Proposal Window" if lang == "English" else "📥 প্রিন্টযোগ্য প্রপোজাল তৈরি করুন", use_container_width=True):
        proposal_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Solar Proposal & BOQ</title>
            <style>
                body {{ font-family: Arial, sans-serif; color: #1E293B; margin: 20px; }}
                h2 {{ color: #D97706; border-bottom: 2px solid #F59E0B; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
                th, td {{ border: 1px solid #CBD5E1; padding: 8px 12px; text-align: left; }}
                th {{ background-color: #F1F5F9; }}
                .btn {{ background: #F59E0B; color: white; padding: 10px 20px; border: none; font-weight: bold; border-radius: 5px; cursor: pointer; margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <button class="btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
            <h2>Solario Commercial Solar Proposal</h2>
            <p><strong>Client:</strong> {client_name} | <strong>System Type:</strong> {system_type}</p>
            <p><strong>Design Specs:</strong> Tilt: {tilt_angle}° | Shading Loss: {shading_loss_pct}% | Backup: {autonomy_hours} Hours</p>
            
            <h3>Bill of Quantities (BOQ)</h3>
            <table>
                <tr><th>Item Description</th><th>Qty</th><th>Estimated Price (BDT)</th></tr>
                <tr><td>Solar PV Modules ({panel_brand})</td><td>{panels_count} Pcs (550W)</td><td>BDT {panel_cost:,.0f}</td></tr>
                <tr><td>Inverter ({inverter_brand})</td><td>1 Unit ({inverter_kva:.1f} kVA)</td><td>BDT {inverter_cost:,.0f}</td></tr>
                {"<tr><td>Battery Bank (" + battery_type + ")</td><td>1 Set (" + f"{battery_ah:.1f}" + " Ah)</td><td>BDT " + f"{battery_cost:,.0f}</td></tr>" if "With Battery" in system_type else ""}
                <tr><td>Rooftop Structure, Wiring & Protection</td><td>1 Set</td><td>BDT {installation_cost:,.0f}</td></tr>
                <tr style="font-weight:bold; background:#FEF3C7;"><td colspan="2">Total Investment</td><td>BDT {total_cost:,.0f}</td></tr>
            </table>
            
            <h3>Financial Summary & ROI</h3>
            <p>Estimated Monthly Savings: <strong>BDT {monthly_savings:,.0f}</strong></p>
            <p>Estimated Yearly Savings: <strong>BDT {yearly_savings:,.0f}</strong></p>
            <p>Payback Period (ROI): <strong>~{payback_years:.1f} Years</strong></p>
        </body>
        </html>
        """
        st.components.v1.html(proposal_html, height=600, scrolling=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #94A3B8;'>Designed by <b>Mohammad Sohel</b></div>", unsafe_allow_html=True)
