import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import math

# ==========================================
# ১. পেজ কনফিগারেশন ও কাস্টম UI স্টাইলিং (CSS)
# ==========================================
st.set_page_config(
    page_title="স্মার্ট সোলার ড্যাশবোর্ড ও ক্যালকুলেটর",
    page_icon="☀️",
    layout="wide"
)

# Custom CSS for Modern UI
st.markdown("""
    <style>
    .main {
        background-color: #F8FAFC;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #F59E0B;
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

# ==========================================
# ২. হেডার সেকশন
# ==========================================
st.title("☀️ প্রফেশনাল অল-ইন-ওয়ান সোলার অ্যাপ")
st.caption("আপনার গৃহস্থালি লোডের হিসাব, আনুমানিক বাজেট, জেনারেশন কার্ভ এবং লাইভ আবহাওয়াভিত্তিক সোলার ট্র্যাকার।")

st.markdown("---")

# ==========================================
# ৩. সাইডবার ইনপুট (যন্ত্রপাতি ও ব্যাকআপ)
# ==========================================
st.sidebar.header("🔌 ১. ঘরের যন্ত্রপাতির সংখ্যা")
fan_qty = st.sidebar.number_input("সিওলিং ফ্যান (৭৫W)", min_value=0, value=5)
light_qty = st.sidebar.number_input("LED লাইট (১৫W)", min_value=0, value=10)
fridge_qty = st.sidebar.number_input("ফ্রিজ (২০০W)", min_value=0, value=1)
tv_qty = st.sidebar.number_input("স্মার্ট টিভি (৮০W)", min_value=0, value=1)
oven_qty = st.sidebar.number_input("ওভেন (১২০০W)", min_value=0, value=1)
pump_qty = st.sidebar.number_input("১ HP সাবমারসিবল পাম্প (৭৫০W)", min_value=0, value=1)

st.sidebar.markdown("---")
st.sidebar.header("⏱️ ২. দৈনিক ব্যবহারের সময় (ঘণ্টা)")
fan_hours = st.sidebar.slider("ফ্যান (ঘণ্টা)", 0, 24, 10)
light_hours = st.sidebar.slider("লাইট (ঘণ্টা)", 0, 24, 8)
fridge_hours = st.sidebar.slider("ফ্রিজ (ঘণ্টা)", 0, 24, 24)
tv_hours = st.sidebar.slider("টিভি (ঘণ্টা)", 0, 24, 5)
oven_hours = st.sidebar.slider("ওভেন (মিনিট)", 0, 120, 30) / 60
pump_hours = st.sidebar.slider("পাম্প (ঘণ্টা)", 0, 10, 1)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ ৩. সোলার সিস্টেমের ধরন")
system_type = st.sidebar.radio("ধরন বেছে নিন:", ["হাইব্রিড/অফ-গ্রিড (ব্যাটারি সহ)", "অন-গ্রিড (ব্যাটারি ছাড়া)"])

# OpenWeatherMap API Key (আপনার কী থাকলে এখানে বসাবেন)
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"

# ==========================================
# ৪. গাণিতিক হিসাব-নিকাশ (Backend Logic)
# ==========================================
# মোট রানিং লোড
running_watts = (fan_qty * 75) + (light_qty * 15) + (fridge_qty * 200) + (tv_qty * 80) + (oven_qty * 1200) + (pump_qty * 750)

# পিক সার্জ লোড (পাম্প ও ফ্রিজে ৩ গুণ ধরে)
surge_watts = (fan_qty * 75) + (light_qty * 15) + (tv_qty * 80) + (oven_qty * 1200) + (fridge_qty * 200 * 2.5) + (pump_qty * 750 * 3)

# দৈনিক মোট ওয়াট-আওয়ার (Wh)
daily_wh = (fan_qty * 75 * fan_hours) + (light_qty * 15 * light_hours) + \
           (fridge_qty * 200 * 12) + (tv_qty * 80 * tv_hours) + \
           (oven_qty * 1200 * oven_hours) + (pump_qty * 750 * pump_hours)

daily_kwh = daily_wh / 1000

# ইনভার্টার, প্যানেল ও ব্যাটারি প্রয়োজন
inverter_kva = (surge_watts * 1.25) / 1000
solar_kwp = (daily_wh / 4.0 / 0.85) / 1000
panels_count = math.ceil((solar_kwp * 1000) / 550) if solar_kwp > 0 else 0
battery_ah = (daily_wh * 0.5) / (48 * 0.8) if "অফ-গ্রিড" in system_type else 0

# দামের হিসাব (BDT)
panel_cost = (panels_count * 550) * 26

if inverter_kva <= 3.5:
    inverter_cost = 45000
elif inverter_kva <= 5.5:
    inverter_cost = 65000
else:
    inverter_cost = 95000

battery_cost = (battery_ah / 100) * 120000 if "অফ-গ্রিড" in system_type else 0
subtotal = panel_cost + inverter_cost + battery_cost
installation_cost = subtotal * 0.10
total_cost = subtotal + installation_cost

# ==========================================
# ৫. মূল ড্যাশবোর্ড রেন্ডারিং
# ==========================================

# শীর্ষ রানিং ম্যাট্রিক্স
col1, col2, col3, col4 = st.columns(4)
col1.metric("রানিং লোড", f"{running_watts} W")
col2.metric("পিক সার্জ লোড", f"{surge_watts:.0f} W")
col3.metric("দৈনিক ব্যবহার", f"{daily_kwh:.2f} kWh")
col4.metric("সর্বমোট বাজেট", f"৳ {total_cost:,.0f}")

st.markdown("---")

# দুই কলাম লেআউট: যন্ত্রাংশ ও খরচ
c1, c2 = st.columns(2)

with c1:
    st.subheader("📋 প্রয়োজনীয় যন্ত্রাংশের বিবরণ")
    st.info(f"⚡ **সুপারিশকৃত ইনভার্টার:** {max(3, round(inverter_kva))} KVA / KW (Hybrid 48V)")
    st.info(f"☀️ **সোলার প্যানেল:** {solar_kwp:.2f} kWp (**{panels_count} টি** ৫৫০W Monocrystalline প্যানেল)")
    if "অফ-গ্রiড" in system_type:
        st.info(f"🔋 **ব্যাটারি ব্যাংক:** {battery_ah:.0f} Ah (48V LiFePO4 লিথিয়াম ব্যাটারি)")
    else:
        st.warning("🔋 **ব্যাটারি ব্যাংক:** অন-গ্রিড সিস্টেমে ব্যাটারি প্রয়োজন নেই।")

with c2:
    st.subheader("💰 খরচের বিস্তারিত হিসাব (BDT)")
    st.write(f"• **সোলার প্যানেল (৫টি x ৫৫০W):** ৳ {panel_cost:,.0f}")
    st.write(f"• **ইনভার্টার ({max(3, round(inverter_kva))} KVA):** ৳ {inverter_cost:,.0f}")
    if "অফ-গ্রিড" in system_type:
        st.write(f"• **লিথিয়াম ব্যাটারি (48V):** ৳ {battery_cost:,.0f}")
    st.write(f"• **ওয়্যারিং, মাউন্টিং ও সার্ভিস:** ৳ {installation_cost:,.0f}")
    st.markdown("---")
    st.success(f"### **মোট বাজেট: ৳ {total_cost:,.0f} BDT**")

st.markdown("---")

# ==========================================
# ৬. ২৪-ঘণ্টার জেনারেশন Plotly চার্ট
# ==========================================
st.subheader("📊 ২৪-ঘণ্টার বিদ্যুৎ উৎপাদন সিমুলেশন")

hours = list(range(24))
generation_curve = [0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.85, 0.95, 1.0, 0.98, 0.90, 0.75, 0.5, 0.2, 0.05, 0, 0, 0, 0, 0, 0]
power_output = [solar_kwp * factor for factor in generation_curve]

df_solar = pd.DataFrame({'Time': [f"{h:02d}:00" for h in hours], 'Generation (kW)': power_output})

fig = px.area(
    df_solar, x='Time', y='Generation (kW)',
    title=f"সারা দিনের আনুমানিক সোলার পাওয়ার কার্ভ ({solar_kwp:.2f} kWp সিস্টেম)",
    labels={'Generation (kW)': 'বিদ্যুৎ (kW)', 'Time': 'সময় (ঘণ্টা)'},
    color_discrete_sequence=['#F59E0B']
)
fig.update_layout(xaxis_title="সময়", yaxis_title="বিদ্যুৎ (kW)", hovermode="x unified", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================
# ৭. লাইভ আবহাওয়া ট্র্যাকার সেকশন
# ==========================================
st.subheader("🌦️ লাইভ আবহাওয়াভিত্তিক জেনারেশন ট্র্যাকার")

city = st.text_input("আপনার শহরের নাম লিখুন:", value="Dhaka")

if st.button("লাইভ সোলার আউটপুট চেক করুন"):
    if API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        st.info("💡 **সিমুলেশন মোড:** কোনো আসল OpenWeatherMap API Key যুক্ত করা হয়নি। নিচে নমুনা ডেটা দিয়ে দেখানো হচ্ছে:")
        cloudiness = 25  # নমুনা মেঘ ২৫%
        temp = 32
        weather_desc = "Few Clouds"
    else:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            cloudiness = data['clouds']['all']
            temp = data['main']['temp']
            weather_desc = data['weather'][0]['description'].title()
        else:
            st.error("শহরের নাম পাওয়া যায়নি!")
            cloudiness = None

    if cloudiness is not None:
        efficiency = 1.0 - ((cloudiness / 100.0) * 0.80)
        current_kw = solar_kwp * efficiency

        w1, w2, w3 = st.columns(3)
        w1.metric("তাপমাত্রা", f"{temp} °C")
        w2.metric("মেঘের পরিমাণ", f"{cloudiness}%")
        w3.metric("আবহাওয়া", weather_desc)

        st.success(f"⚡ **লাইভ জেনারেশন আনুমানিক:** {current_kw:.2f} kW (এফিসিয়েন্সি: {efficiency*100:.1f}%)")