import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import math

# ==========================================
# 1. Page Configuration & Custom UI Styling
# ==========================================
st.set_page_config(
    page_title="Smart Solar Dashboard & Calculator",
    page_icon="☀️",
    layout="wide"
)

# Custom CSS for Modern UI & Text Overflow Fix
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

/* Fix text size & prevent text clipping/overflow in metric boxes */
div[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    word-break: break-word !important;
}

/* Force dark text for metric box */
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
</style>
""", unsafe_allow_html=True)

# OpenWeatherMap API Key
API_KEY = "f95798b74fd5bd53dd615f40cdf88312"

# ==========================================
# 2. Header Section & Multi-language Option
# ==========================================
# Language Switcher
lang = st.radio("🌐 Language / ভাষা:", ["English", "বাংলা"], horizontal=True)

if lang == "English":
    st.title("☀️ Smart Commercial Solar Calculator & Dashboard")
    st.caption("Calculate household/industrial solar load, ROI, equipment brands, and real-time solar output.")
else:
    st.title("☀️ স্মার্ট বাণিজ্যিক সোলার ক্যালকুলেটর ও ড্যাশবোর্ড")
    st.caption("বাসাবাড়ি বা শিল্প প্রতিষ্ঠানের সোলার লোড, আনুমানিক খরচ, ব্র্যাণ্ড ও রিয়েল-টাইম বিদ্যুৎ উৎপাদন হিসেব করুন।")

st.markdown("---")

# ==========================================
# 3. Sidebar Inputs
# ==========================================
st.sidebar.header("🔌 1. Appliance Quantities" if lang == "English" else "🔌 ১. সরঞ্জামের পরিমাণ")
fan_qty = st.sidebar.number_input("Ceiling Fan (75W)" if lang == "English" else "সিকেলিং ফ্যান (৭৫ ওয়াট)", min_value=0, value=5)
light_qty = st.sidebar.number_input("LED Light (15W)" if lang == "English" else "এলইডি লাইট (১৫ ওয়াট)", min_value=0, value=10)
fridge_qty = st.sidebar.number_input("Refrigerator (200W)" if lang == "English" else "রেফ্রিজারেটর/ফ্রিজ (২০০ ওয়াট)", min_value=0, value=1)
tv_qty = st.sidebar.number_input("Smart TV (80W)" if lang == "English" else "স্মার্ট টিভি (৮০ ওয়াট)", min_value=0, value=1)
oven_qty = st.sidebar.number_input("Oven (1200W)" if lang == "English" else "ওভেন (১২০০ ওয়াট)", min_value=0, value=1)
pump_qty = st.sidebar.number_input("1 HP Submersible Pump (750W)" if lang == "English" else "১ এইচপি সাবমার্সিবল পাম্প (৭৫০ ওয়াট)", min_value=0, value=1)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ 2. Daily Usage (Hours)" if lang == "English" else "⏱️ ২. দৈনিক ব্যবহার (ঘণ্টা)")
fan_hours = st.sidebar.slider("Fan (Hours)" if lang == "English" else "ফ্যান (ঘণ্টা)", 0, 24, 10)
light_hours = st.sidebar.slider("Light (Hours)" if lang == "English" else "লাইট (ঘণ্টা)", 0, 24, 8)
fridge_hours = st.sidebar.slider("Refrigerator (Hours)" if lang == "English" else "ফ্রিজ (ঘণ্টা)", 0, 24, 24)
tv_hours = st.sidebar.slider("TV (Hours)" if lang == "English" else "টিভি (ঘণ্টা)", 0, 24, 5)
oven_hours = st.sidebar.slider("Oven (Minutes)" if lang == "English" else "ওভেন (মিনিট)", 0, 120, 30) / 60
pump_hours = st.sidebar.slider("Pump (Hours)" if lang == "English" else "পাম্প (ঘণ্টা)", 0, 10, 1)

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

# Brand-based pricing multipliers
brand_multiplier = 1.15 if "Tier-1" in panel_brand or "Huawei" in inverter_brand or "Deye" in inverter_brand else 1.0

# ==========================================
# 4. Roof Area Calculator Component
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🏠 Roof Area Calculator" if lang == "English" else "🏠 ছাদের আয়তন দিয়ে হিসেব")
roof_sqft = st.sidebar.number_input("Available Roof Area (Sq. Ft):" if lang == "English" else "খালি ছাদের আয়তন (বর্গফুট):", min_value=0, value=300)
max_possible_kwp = (roof_sqft / 100) * 1.0  # Approx 100 sqft per 1kWp

# ==========================================
# 5. Backend Calculations & ROI Logic
# ==========================================
running_watts = (fan_qty * 75) + (light_qty * 15) + (fridge_qty * 200) + (tv_qty * 80) + (oven_qty * 1200) + (pump_qty * 750)
surge_watts = (fan_qty * 75) + (light_qty * 15) + (tv_qty * 80) + (oven_qty * 1200) + (fridge_qty * 200 * 2.5) + (pump_qty * 750 * 3)

daily_wh = (fan_qty * 75 * fan_hours) + (light_qty * 15 * light_hours) + \
           (fridge_qty * 200 * 12) + (tv_qty * 80 * tv_hours) + \
           (oven_qty * 1200 * oven_hours) + (pump_qty * 750 * pump_hours)
daily_kwh = daily_wh / 1000

inverter_kva = (surge_watts * 1.25) / 1000
solar_kwp = (daily_wh / 4.0 / 0.85) / 1000
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0

# Cost Calculation with Brand Pricing
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

# Financial ROI Calculations
electricity_rate = 9.5  # Average BDT per kWh unit in Bangladesh
monthly_savings = daily_kwh * 30 * electricity_rate
yearly_savings = monthly_savings * 12
payback_years = total_cost / yearly_savings if yearly_savings > 0 else 0

# ==========================================
# 6. Main Dashboard Rendering
# ==========================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Running Load" if lang == "English" else "চলমান লোড", f"{running_watts} W")
col2.metric("Peak Surge Load" if lang == "English" else "সর্বোচ্চ স্টার্ট লোড", f"{surge_watts:.0f} W")
col3.metric("Daily Usage" if lang == "English" else "দৈনিক ব্যবহার", f"{daily_kwh:.2f} kWh")
col4.metric("Total Budget" if lang == "English" else "মোট বাজেট", f"BDT {total_cost:,.0f}")

st.markdown("---")

# Roof Fitting Alert
if solar_kwp > max_possible_kwp:
    if lang == "English":
        st.warning(f"⚠️ **Roof Space Notice:** Your required system ({solar_kwp:.2f} kWp) needs ~{solar_kwp*100:.0f} Sq. Ft. Your roof is {roof_sqft} Sq. Ft (Max capacity: ~{max_possible_kwp:.2f} kWp).")
    else:
        st.warning(f"⚠️ **ছাদের জায়গার সতর্কতা:** আপনার প্রয়োজনীয় সিস্টেমের ({solar_kwp:.2f} kWp) জন্য অন্তত ~{solar_kwp*100:.0f} বর্গফুট ছাদ প্রয়োজন। আপনার দেওয়া ছাদের ক্ষেত্রফল {roof_sqft} বর্গফুট (সর্বোচ্চ ক্ষমতা: ~{max_possible_kwp:.2f} kWp)।")

# Hardware Specs & Cost Summary
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
if lang == "English":
    st.success(f"### 🎯 Total Estimated System Cost: BDT {total_cost:,.0f}")
else:
    st.success(f"### 🎯 মোট আনুমানিক প্রজেক্ট খরচ: BDT {total_cost:,.0f}")
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
    import folium
    from streamlit_folium import st_folium

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
