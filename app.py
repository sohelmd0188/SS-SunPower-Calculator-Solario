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
        <div class="hero-subtitle">Advanced calculations with 2D/3D CAD Layout, Weather API, Engineering Studio, Cash Flow, and BOQ Projections.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="hero-container">
        <span class="hero-badge">☀️ সোলার ক্যাড ও অ্যানালিটিক্স</span>
        <div class="hero-title">স্মার্ট বাণিজ্যিক সোলার ক্যালকুলেটর ও ড্যাশবোর্ড</div>
        <div class="hero-subtitle">২ডি/থ্রিডি ক্যাড লেআউট, আবহাওয়া সিমুলেশন, ইঞ্জিনিয়ারিং স্টুডিও, ক্যাশ ফ্লো এবং প্রফেশনাল প্রপোজাল সমেত সম্পূর্ণ সিস্টেম।</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 3. Sidebar Inputs & Engineering Parameters
# ==========================================
if "appliance_list" not in st.session_state:
    st.session_state.appliance_list = {
        "Ceiling Fan (75W)": {"watt": 75, "qty": 5, "type": "regular", "hours": 8.0},
        "LED Light (15W)": {"watt": 15, "qty": 10, "type": "regular", "hours": 8.0},
        "Refrigerator (200W)": {"watt": 200, "qty": 1, "type": "regular", "hours": 8.0},
        "1.5 Ton Inverter AC (1500W)": {"watt": 1500, "qty": 1, "type": "heavy", "hours": 6.0}
    }

st.sidebar.header("🔌 1. Appliance Quantities & Load" if lang == "English" else "🔌 ১. সরঞ্জামের পরিমাণ ও লোড")

# Add New Appliance Option
with st.sidebar.expander("➕ Add New Appliance" if lang == "English" else "➕ নতুন অ্যাপ্লায়েন্স যোগ করুন"):
    new_name = st.text_input("Appliance Name" if lang == "English" else "নাম", "Water Pump (750W)")
    new_watt = st.number_input("Wattage (W)" if lang == "English" else "ওয়াট", min_value=5, max_value=5000, value=750)
    new_qty_input = st.number_input("Quantity" if lang == "English" else "পরিমাণ", min_value=1, max_value=20, value=1)
    new_type = st.selectbox("Usage Type" if lang == "English" else "ব্যবহারের ধরন", ["regular", "heavy"])
    new_hours = st.slider("Daily Usage Hours" if lang == "English" else "দৈনিক ব্যবহারের ঘণ্টা", 1.0, 24.0, 4.0)
    if st.button("Add to List" if lang == "English" else "তালিকায় যোগ করুন"):
        st.session_state.appliance_list[new_name] = {"watt": new_watt, "qty": new_qty_input, "type": new_type, "hours": new_hours}
        st.rerun()

# Render existing appliances with Quantity, Type, and Hour Control
for app_name, app_data in list(st.session_state.appliance_list.items()):
    st.sidebar.markdown(f"**{app_name}**")
    col_q, col_h, col_del = st.sidebar.columns([2, 2, 1])
    with col_q:
        new_qty = st.number_input("Qty", min_value=0, max_value=50, value=app_data["qty"], step=1, key=f"qty_{app_name}")
        st.session_state.appliance_list[app_name]["qty"] = new_qty
    with col_h:
        new_hrs = st.number_input("Hrs", min_value=0.5, max_value=24.0, value=float(app_data.get("hours", 8.0)), step=0.5, key=f"hrs_{app_name}")
        st.session_state.appliance_list[app_name]["hours"] = new_hrs
    with col_del:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{app_name}"):
            del st.session_state.appliance_list[app_name]
            st.rerun()
    st.sidebar.markdown("---")

st.sidebar.header("📐 2. Tilt & Azimuth & Losses" if lang == "English" else "২. টিল্ট, আজিমুথ ও লস ফ্যাক্টর")
tilt_angle = st.sidebar.slider("Panel Tilt Angle (Degrees):" if lang == "English" else "প্যানেল টিল্ট অ্যাঙ্গেল (ডিগ্রী):", 0, 45, 23)
azimuth_angle = st.sidebar.slider("Azimuth Angle (South = 0°):" if lang == "English" else "আজিমুথ অ্যাঙ্গেল (দক্ষিণ = ০°):", -90, 90, 0)
shading_loss_pct = st.sidebar.slider("Shading & Dust Loss (%):" if lang == "English" else "ছায়া ও ধূলিমলিনতা লস (%):", 0, 30, 15)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 3. System & Battery Engineering" if lang == "English" else "৩. সিস্টেম ও ব্যাটারি ইঞ্জিনিয়ারিং")
system_type = st.sidebar.radio("Select System Type:" if lang == "English" else "সিস্টেম টাইপ:", ["Hybrid / Off-Grid (With Battery)", "On-Grid (Without Battery)"])
panel_brand = st.sidebar.selectbox("Solar Panel Brand:" if lang == "English" else "প্যানেল ব্র্যান্ড:", ["Longi Solar (Tier-1)", "Jinko Solar (Tier-1)", "Standard"])
inverter_brand = st.sidebar.selectbox("Inverter Brand:" if lang == "English" else "ইনভার্টার ব্র্যান্ড:", ["Growatt", "Deye", "Huawei"])

if "With Battery" in system_type:
    battery_type = st.sidebar.selectbox("Battery Chemistry:" if lang == "English" else "ব্যাটারি কেমিক্যাল টাইপ:", ["LiFePO4 Lithium Battery (90% DoD)", "Tubular Lead-Acid Battery (70% DoD)"])
    autonomy_hours = st.sidebar.slider("Battery Backup Hours (Autonomy):" if lang == "English" else "ব্যাটারি ব্যাকআপ আওয়ার্স:", 1, 12, 4)
else:
    autonomy_hours = 0

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
    used_hrs = app_data.get("hours", 6.0)
    daily_wh += total_app_watt * used_hrs
    surge_watts += total_app_watt * (2.0 if "AC" in app_name or "Refrigerator" in app_name or "Pump" in app_name else 1.0)

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
# 6. Advanced Modules: 24-Hour Simulation & CAD/Layout
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 24-Hr Generation / উৎপাদন সিমুলেশন", 
    "🗺️ CAD Layout & Roof / ক্যাড ও ছাদের বিন্যাস", 
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
    st.subheader("Rooftop Space & Panel CAD Layout Assessment" if lang == "English" else "ছাদের ক্ষেত্রফল ও প্যানেল ক্যাড লেআউট বিশ্লেষণ")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📍 **Required Roof Area:** {required_roof_sqft} Sq. Ft")
        st.info(f"📍 **Available Roof Area:** {roof_sqft} Sq. Ft")
        if roof_sqft < required_roof_sqft:
            st.error("⚠️ Warning: Available roof area is less than required!" if lang == "English" else "⚠️ সতর্কবার্তা: উপলব্ধ ছাদের জায়গা প্রয়োজনের তুলনায় কম!")
        else:
            st.success("✅ Roof area is sufficient for this installation capacity." if lang == "English" else "✅ এই সিস্টেমের জন্য ছাদের জায়গা যথেষ্ট রয়েছে।")
    with col_b:
        if panels_count > 0:
            cols_grid = max(1, math.ceil(math.sqrt(panels_count)))
            x_coords = [i % cols_grid for i in range(panels_count)]
            y_coords = [i // cols_grid for i in range(panels_count)]
            df_cad = pd.DataFrame({"X": x_coords, "Y": y_coords})
            fig_cad = px.scatter(df_cad, x="X", y="Y", title="Simulated Panel Placement Layout (550W Modules)" if lang == "English" else "সিমুলেটেড প্যানেল লেআউট গ্রিড", symbol_sequence=['square'])
            fig_cad.update_traces(marker=dict(size=15, color='#F59E0B'))
            fig_cad.update_layout(template="plotly_dark", xaxis_title="Array Width", yaxis_title="Array Length")
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
            <p><strong>Design Specs:</strong> Tilt: {tilt_angle}° | Azimuth: {azimuth_angle}° | Shading Loss: {shading_loss_pct}% | Backup: {autonomy_hours} Hours</p>
            
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
