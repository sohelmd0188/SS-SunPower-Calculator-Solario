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
div[data-testid="stMetricLabel"] { font-size: 0.95rem !important; font-weight: 700 !important; color: #CBD5E1 !important; }
div[data-testid="stMetricValue"] { font-size: 1.45rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
.hero-container {
    background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                url('https://images.unsplash.com/photo-1508514177221-188b1cf16e9d?q=80&w=1200&auto=format&fit=crop');
    background-size: cover; background-position: center;
    border-radius: 16px; padding: 35px 25px; margin-bottom: 25px;
    border: 1px solid rgba(245, 158, 11, 0.4);
}
.hero-title { color: #FFFFFF !important; font-size: 2.2rem !important; font-weight: 800 !important; margin-bottom: 8px !important; }
.hero-subtitle { color: #E2E8F0 !important; font-size: 1.05rem !important; line-height: 1.5 !important; }
.hero-badge { background-color: #F59E0B; color: #0F172A !important; font-weight: 700; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

API_KEY = "f95798b74fd5bd53dd615f40cdf88312"

# ==========================================
# 2. Header & Language Options
# ==========================================
lang = st.radio("🌐 Language / ভাষা:", ["English", "বাংলা"], horizontal=True)

if lang == "English":
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ PROFESSIONAL SOLAR CAD & ROI</span>
        <div class="hero-title">Solario • Advanced Solar Engineering Engine</div>
        <div class="hero-subtitle">Industrial-grade load profiling, tilt optimization, net metering economics, and real-time CAD layout.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ প্রফেশনাল সোলার ক্যাড ও অ্যানালিটিক্স</span>
        <div class="hero-title">স্মার্ট সোলার কমার্শিয়াল ও ইন্ডাস্ট্রিয়াল ডিজাইন ইঞ্জিন</div>
        <div class="hero-subtitle">অ্যাডভান্সড লোড প্রোফাইলিং, টিল্ট অপ্টিমাইজেশন, নেট মিটারিং এবং রিয়েল-টাইম ক্যাড লেআউট।</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. Sidebar Inputs & Professional Engineering Parameters
# ==========================================
if "appliance_list" not in st.session_state:
    st.session_state.appliance_list = {
        "Ceiling Fan (75W)": {"watt": 75, "qty": 5, "type": "regular", "hours": 8.0},
        "LED Light (15W)": {"watt": 15, "qty": 10, "type": "regular", "hours": 8.0},
        "Refrigerator (200W)": {"watt": 200, "qty": 1, "type": "regular", "hours": 8.0},
        "1.5 Ton Inverter AC (1500W)": {"watt": 1500, "qty": 1, "type": "heavy", "hours": 6.0},
        "1 HP Submersible Pump (750W)": {"watt": 750, "qty": 1, "type": "heavy", "hours": 1.5}
    }

EXTRA_APPLIANCES = {
    "2 Ton AC (2200W)": {"watt": 2200, "type": "heavy", "default_hours": 6.0},
    "Washing Machine (500W)": {"watt": 500, "type": "heavy", "default_hours": 1.0},
    "Geyser / Water Heater (2000W)": {"watt": 2000, "type": "heavy", "default_hours": 1.0},
    "Computer / Desktop (250W)": {"watt": 250, "type": "regular", "default_hours": 8.0},
    "Iron Box (1000W)": {"watt": 1000, "type": "heavy", "default_hours": 0.5}
}

st.sidebar.header("🔌 1. Appliance Load Profile" if lang == "English" else "🔌 ১. লোড প্রোফাইল ও যন্ত্রপাতি")

st.sidebar.subheader("💡 Regular Loads" if lang == "English" else "💡 সাধারণ লোড")
for app_name, app_data in list(st.session_state.appliance_list.items()):
    if app_data.get("type") == "regular":
        col_app, col_del = st.sidebar.columns([4, 1])
        with col_app:
            st.session_state.appliance_list[app_name]["qty"] = st.number_input(f"{app_name}", 0, 100, app_data["qty"], key=f"qty_{app_name}")
        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{app_name}"):
                del st.session_state.appliance_list[app_name]
                st.rerun()

st.sidebar.subheader("⚡ Heavy / High Power Loads" if lang == "English" else "⚡ হেভি লোড ও সময়")
for app_name, app_data in list(st.session_state.appliance_list.items()):
    if app_data.get("type") == "heavy":
        col_app, col_del = st.sidebar.columns([4, 1])
        with col_app:
            st.session_state.appliance_list[app_name]["qty"] = st.number_input(f"{app_name} (Qty)", 0, 50, app_data["qty"], key=f"qty_{app_name}")
            st.session_state.appliance_list[app_name]["hours"] = st.number_input(f"⏱️ {app_name} Hrs/Day", 0.1, 24.0, float(app_data.get("hours", 1.0)), 0.5, key=f"hrs_{app_name}")
        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_h_{app_name}"):
                del st.session_state.appliance_list[app_name]
                st.rerun()

selected_extra = st.sidebar.selectbox("Add Extra Appliance" if lang == "English" else "অতিরিক্ত ডিভাইস যোগ করুন", list(EXTRA_APPLIANCES.keys()))
if st.sidebar.button("➕ Add to List" if lang == "English" else "➕ যোগ করুন", use_container_width=True):
    if selected_extra not in st.session_state.appliance_list:
        info = EXTRA_APPLIANCES[selected_extra]
        st.session_state.appliance_list[selected_extra] = {"watt": info["watt"], "qty": 1, "type": info["type"], "hours": info["default_hours"]}
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. Professional Engineering Setup" if lang == "English" else "⚙️ ২. প্রফেশনাল ইঞ্জিনিয়ারিং সেটিংস")

system_type = st.sidebar.radio("System Architecture:" if lang == "English" else "সিস্টেম আর্কিটেকচার:", ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"])
panel_brand = st.sidebar.selectbox("Solar Panel Brand:", ["Longi Solar (Tier-1, 22.5%)", "Jinko Solar (Tier-1, 22%)", "Canadian Solar", "Standard Brand"])
inverter_brand = st.sidebar.selectbox("Inverter Brand:", ["Growatt", "Deye (Hybrid)", "Huawei (Commercial)", "Standard"])

if "With Battery" in system_type:
    battery_type = st.sidebar.selectbox("Battery Chemistry:", ["LiFePO4 Lithium (DoD 90%)", "Tubular Lead-Acid (DoD 50%)"])
    autonomy_hours = st.sidebar.slider("Battery Backup / Autonomy Hours:" if lang == "English" else "ব্যাটারি ব্যাকআপ সময় (ঘণ্টা):", 1, 12, 4)
else:
    net_metering = st.sidebar.checkbox("Enable Net Metering Benefit" if lang == "English" else "নেট মিটারিং সুবিধা সক্রিয় করুন", value=True)

# New Engineering Inputs: Tilt & Shading
tilt_angle = st.sidebar.slider("Panel Tilt Angle (Degrees):" if lang == "English" else "প্যানেল টিল্ট অ্যাঙ্গেল (ডিগ্রি - বাংলাদেশ প্রেক্ষাপটে ১৫°-২৩°):", 0, 45, 20)
shading_loss = st.sidebar.slider("Estimated Shading / Dust Loss (%):" if lang == "English" else "ছায়া ও ধূলিমলিনতা লস (%):", 0, 25, 12)

roof_sqft = st.sidebar.number_input("Available Roof Area (Sq. Ft):" if lang == "English" else "খালি ছাদের আয়তন (বর্গফুট):", min_value=0, value=600)
max_possible_kwp = (roof_sqft / 100) * 1.0

# ==========================================
# 4. Calculation Engine with Professional Losses
# ==========================================
running_watts = sum(d["watt"] * d["qty"] for d in st.session_state.appliance_list.values() if d.get("type") == "regular")
heavy_watts = sum(d["watt"] * d["qty"] for d in st.session_state.appliance_list.values() if d.get("type") == "heavy")
total_running_load = running_watts + heavy_watts

surge_watts = 0
daily_wh = 0.0
for app_name, app_data in st.session_state.appliance_list.items():
    q, w, t, h = app_data["qty"], app_data["watt"], app_data.get("type"), app_data.get("hours", 8.0)
    tot_w = w * q
    if t == "heavy":
        daily_wh += tot_w * h
    else:
        daily_wh += tot_w * 8.0 # Standard 8 hrs for regular
        
    if "Refrigerator" in app_name or "Pump" in app_name:
        surge_watts += tot_w * 3.0
    elif "AC" in app_name:
        surge_watts += tot_w * 1.5
    else:
        surge_watts += tot_w

daily_kwh = daily_wh / 1000.0
inverter_kva = (surge_watts * 1.25) / 1000

# Professional Solar Sizing incorporating Shading & System Losses (~80-85% Performance Ratio)
net_efficiency_factor = (1.0 - (shading_loss / 100.0)) * 0.82
solar_kwp = (daily_wh / 4.5 / net_efficiency_factor) / 1000 if daily_wh > 0 else 0
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0
required_roof_sqft = math.ceil(solar_kwp * 100)

brand_multiplier = 1.18 if "Tier-1" in panel_brand or "Huawei" in inverter_brand or "Deye" in inverter_brand else 1.0
panel_cost = (panels_count * 550) * (30 * brand_multiplier)
inverter_cost = (75000 if inverter_kva <= 5 else 130000) * brand_multiplier

if "With Battery" in system_type:
    dod = 0.90 if "LiFePO4" in battery_type else 0.50
    battery_capacity_wh = (daily_kwh * 1000 * (autonomy_hours / 24)) / dod
    battery_ah = battery_capacity_wh / 48
    battery_cost = (battery_ah / 100) * (135000 if "LiFePO4" in battery_type else 75000)
else:
    battery_ah = 0
    battery_cost = 0

subtotal = panel_cost + inverter_cost + battery_cost
installation_cost = subtotal * 0.12 # 12% professional engineering & wiring cost
total_cost = subtotal + installation_cost

electricity_rate = 11.5 # Updated commercial/residential blended tier rate
monthly_savings = daily_kwh * 30 * electricity_rate
if "With Battery" not in system_type and locals().get('net_metering', True):
    monthly_savings *= 1.25 # Net metering surplus bonus benefit

yearly_savings = monthly_savings * 12
payback_years = total_cost / yearly_savings if yearly_savings > 0 else 0

# ==========================================
# 5. Dashboard Metrics Display
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Connected Load" if lang == "English" else "মোট সংযুক্ত লোড", f"{total_running_load} W")
col2.metric("Peak Surge Load" if lang == "English" else "সর্বোচ্চ স্টার্ট লোড", f"{surge_watts:.0f} W")
col3.metric("Daily Energy Need" if lang == "English" else "দৈনিক শক্তির চাহিদা", f"{daily_kwh:.2f} kWh")
col4.metric("Est. Capital Cost" if lang == "English" else "আনুমানিক মোট খরচ", f"BDT {total_cost:,.0f}")

st.markdown("---")

if solar_kwp > max_possible_kwp:
    st.warning(f"⚠️ **Roof Space Limit Warning:** Required system size ({solar_kwp:.2f} kWp) requires ~{required_roof_sqft} Sq. Ft. Your roof size is {roof_sqft} Sq. Ft.")

c1, c2 = st.columns(2)
with c1:
    st.subheader("📋 Engineering Specifications" if lang == "English" else "📋 প্রফেশনাল ইঞ্জিনিয়ারিং স্পেসিফিকেশন")
    st.info(f"⚡ **Inverter Size:** {max(3, round(inverter_kva, 1))} KVA ({inverter_brand})")
    st.info(f"☀️ **PV Array:** {solar_kwp:.2f} kWp ({panels_count}x 550W - {panel_brand})")
    st.info(f"📐 **Tilt & Shading:** Optimized at {tilt_angle}° Tilt, {shading_loss}% Loss factored")
    if "With Battery" in system_type:
        st.info(f"🔋 **Battery Bank:** {battery_ah:.0f} Ah 48V ({battery_type}, {autonomy_hours}h Autonomy)")

with c2:
    st.subheader("💰 Financial Economics & ROI" if lang == "English" else "💰 আর্থিক বিশ্লেষণ ও মূল্য ফেরত (ROI)")
    st.write(f"• **Panel & Inverter Hardware:** BDT {(panel_cost + inverter_cost):,.0f}")
    if "With Battery" in system_type:
        st.write(f"• **Battery Bank Storage:** BDT {battery_cost:,.0f}")
    st.write(f"• **Engineering & Installation (12%):** BDT {installation_cost:,.0f}")
    st.write("---")
    st.write(f"💵 **Estimated Monthly Savings:** BDT {monthly_savings:,.0f} / month")
    st.write(f"📈 **Payback Period (ROI):** ~**{payback_years:.1f} Years**")

st.markdown("---")

# ==========================================
# 6. Interactive CAD & 3D Rooftop Layout
# ==========================================
st.subheader("📐 Smart Solar CAD & Layout Studio" if lang == "English" else "📐 স্মার্ট সোলার ক্যাড ও লেআউট স্টুডিও")

cad_mode = st.radio("Select View Mode:" if lang == "English" else "ভিউ মোড নির্বাচন করুন:", ["2D Technical Array Blueprint", "3D Interactive Rooftop Model", "Satellite Coordinates Placement"], horizontal=True)

if panels_count > 0 and roof_sqft > 0:
    roof_w = np.sqrt(roof_sqft * 1.5)
    roof_l = roof_sqft / roof_w
    p_w, p_l = 3.5, 6.5
    cols = max(1, int(roof_w // (p_w + 0.5)))
    rows = int(np.ceil(panels_count / cols))

    if "2D Technical" in cad_mode:
        fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='#0F172A')
        ax.set_facecolor('#0F172A')
        ax.add_patch(patches.Rectangle((0, 0), roof_w, roof_l, linewidth=2, edgecolor='#F59E0B', facecolor='#1E293B', linestyle='--'))
        
        placed = 0
        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    x, y = 1.0 + c * (p_w + 0.5), 1.0 + r * (p_l + 0.5)
                    if x + p_w <= roof_w and y + p_l <= roof_l:
                        ax.add_patch(patches.Rectangle((x, y), p_w, p_l, edgecolor='#38BDF8', facecolor='#0284C7', alpha=0.85))
                        placed += 1
        ax.set_xlim(-2, roof_w + 2)
        ax.set_ylim(-2, roof_l + 2)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title(f"2D Panel Layout: {placed} Panels Placed ({tilt_angle}° Tilt Orientation)", color='#F8FAFC', fontsize=10, fontweight='bold')
        st.pyplot(fig, use_container_width=True)

    elif "3D Interactive" in cad_mode:
        base_lat, base_lon = 23.8103, 90.4125
        building_data = [{"coordinates": [[base_lon-0.0001, base_lat-0.0001], [base_lon+0.0001, base_lat-0.0001], [base_lon+0.0001, base_lat+0.0001], [base_lon-0.0001, base_lat+0.0001]], "height": 15, "fill_color": [30, 41, 59, 200]}]
        panel_data = []
        placed = 0
        for r in range(rows):
            for c in range(cols):
                if placed < panels_count:
                    panel_data.append({"coordinates": [[base_lon + c*0.00002, base_lat + r*0.00002], [base_lon + c*0.00002 + 0.00015, base_lat + r*0.00002], [base_lon + c*0.00002 + 0.00015, base_lat + r*0.00002 + 0.00015], [base_lon + c*0.00002, base_lat + r*0.00002 + 0.00015]], "height": 15.8, "fill_color": [2, 132, 199, 255]})
                    placed += 1
        st.pydeck_chart(pdk.Deck(layers=[pdk.Layer("PolygonLayer", building_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True), pdk.Layer("PolygonLayer", panel_data, get_polygon="coordinates", get_elevation="height", get_fill_color="fill_color", extruded=True)], initial_view_state=pdk.ViewState(latitude=base_lat, longitude=base_lon, zoom=19, pitch=55, bearing=30)))

    else:
        st.info("🗺️ **Satellite Mode:** Click anywhere on the map to place your solar array configuration.")
        m = folium.Map(location=[23.8103, 90.4125], zoom_start=20, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Satellite')
        map_data = st_folium(m, height=450, width=800)

st.markdown("---")

# ==========================================
# 7. Long-Term Cash Flow & Net Metering Projection Graph
# ==========================================
st.subheader("📈 10-Year Financial Cash Flow & Savings Projection" if lang == "English" else "📈 ১০ বছরের আর্থিক সাশ্রয় ও ক্যাশ ফ্লো গ্রাফ")

years = list(range(1, 11))
cumulative_savings = []
total_saved = 0
for yr in years:
    # factoring 0.5% yearly degradation and 5% tariff inflation
    yearly_benefit = yearly_savings * ((1.05 ** (yr - 1)) * (0.995 ** (yr - 1)))
    total_saved += yearly_benefit
    cumulative_savings.append(total_saved - total_cost)

df_cashflow = pd.DataFrame({'Year': [f"Year {y}" for y in years], 'Net Profit / ROI (BDT)': cumulative_savings})
fig_cf = px.bar(df_cashflow, x='Year', y='Net Profit / ROI (BDT)', title="Cumulative Net Return Over 10 Years", color_discrete_sequence=['#10B981'])
fig_cf.update_layout(template="plotly_dark")
st.plotly_chart(fig_cf, use_container_width=True)

st.markdown("---")

# ==========================================
# 8. Professional Project Proposal Report Export
# ==========================================
st.subheader("📄 Client Engineering Proposal & PDF Generator" if lang == "English" else "📄 ক্লায়েন্ট প্রপোজাল ও পিডিএফ জেনারেটর")
client_name = st.text_input("Client / Project Name:" if lang == "English" else "গ্রাহক/প্রতিষ্ঠানের নাম:", value="Enterprise Commercial Client")

if st.button("📥 Generate Printable Engineering Proposal Report" if lang == "English" else "📥 প্রিন্ট উপযোগী প্রপোজাল তৈরি করুন", use_container_width=True):
    proposal_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Professional Solar Proposal</title>
        <style>
            body {{ font-family: Arial, sans-serif; color: #1E293B; margin: 30px; }}
            .header {{ text-align: center; border-bottom: 2px solid #F59E0B; padding-bottom: 10px; margin-bottom: 20px; }}
            .title {{ font-size: 22px; font-weight: bold; color: #0F172A; }}
            .section {{ font-size: 15px; font-weight: bold; color: #B45309; background: #FEF3C7; padding: 5px 10px; margin-top: 20px; border-left: 4px solid #F59E0B; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
            th, td {{ border: 1px solid #CBD5E1; padding: 8px; text-align: left; }}
            th {{ background: #F1F5F9; }}
            .btn {{ background: #F59E0B; color: white; padding: 10px 20px; border: none; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <button class="btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
        <div class="header">
            <div class="title">SOLAR ENERGY SYSTEM TECHNICAL & FINANCIAL PROPOSAL</div>
            <div>Prepared by Solario Advanced CAD Engine</div>
        </div>
        <p><strong>Client:</strong> {client_name} &nbsp;|&nbsp; <strong>System Architecture:</strong> {system_type}</p>
        
        <div class="section">1. System Summary & Technical Specs</div>
        <ul>
            <li><strong>Total Load Profile:</strong> {total_running_load} W (Peak Surge: {surge_watts:.0f} W)</li>
            <li><strong>Daily Energy Generation:</strong> {daily_kwh:.2f} kWh</li>
            <li><strong>Solar PV Array:</strong> {solar_kwp:.2f} kWp ({panels_count}x 550W {panel_brand})</li>
            <li><strong>Inverter Capacity:</strong> {max(3, round(inverter_kva, 1))} KVA ({inverter_brand})</li>
            <li><strong>Orientation:</strong> {tilt_angle}° Tilt Angle, Shading Loss factored at {shading_loss}%</li>
        </ul>
        
        <div class="section">2. Financial Analysis & ROI</div>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Total Capital Investment</td><td><strong>BDT {total_cost:,.0f}</strong></td></tr>
            <tr><td>Estimated Monthly Savings</td><td>BDT {monthly_savings:,.0f} / Month</td></tr>
            <tr><td>Payback Period</td><td><strong>~{payback_years:.1f} Years</strong></td></tr>
        </table>
        
        <div class="section">3. Bill of Quantities (BOQ)</div>
        <table>
            <tr><th>Equipment Item</th><th>Qty</th><th>Est. Cost (BDT)</th></tr>
            <tr><td>Solar Panels (550W Tier-1)</td><td>{panels_count} Pcs</td><td>BDT {panel_cost:,.0f}</td></tr>
            <tr><td>Inverter Unit</td><td>1 Unit</td><td>BDT {inverter_cost:,.0f}</td></tr>
            {f"<tr><td>Battery Bank ({battery_ah:.0f}Ah)</td><td>1 Bank</td><td>BDT {battery_cost:,.0f}</td></tr>" if "With Battery" in system_type else ""}
            <tr><td>Structure, Wiring & Installation</td><td>1 Job</td><td>BDT {installation_cost:,.0f}</td></tr>
            <tr style="font-weight:bold; background:#FEF3C7;"><td colspan="2">Total Investment Budget</td><td>BDT {total_cost:,.0f}</td></tr>
        </table>
    </body>
    </html>
    """
    st.components.v1.html(proposal_html, height=700, scrolling=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #94A3B8;'>Designed by <b>Mohammad Sohel</b></div>", unsafe_allow_html=True)
