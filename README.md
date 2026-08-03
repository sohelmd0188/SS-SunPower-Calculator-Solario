# ☀️ Smart Solar Dashboard & Calculator (Solario)

An interactive, web-based solar load calculator, financial ROI estimator, and real-time solar panel placement tool built with **Python**, **Streamlit**, **Folium**, and **Pydeck**. 

This application helps users estimate their solar energy requirements, system costs, payback period, and visualize 2D/3D solar panel placements directly on their rooftops using satellite mapping.

---

## ✨ Key Features

* **🔌 Interactive Load Calculation:** Enter home/commercial appliances (fans, lights, refrigerators, pumps, etc.) to automatically compute running watts, surge load, and daily energy consumption (`kWh`).
* **⚙️ System & Brand Customization:** Choose between **On-Grid** or **Hybrid/Off-Grid** systems, select Tier-1 solar panel brands, inverters, and battery types (LiFePO4 / Lead-Acid).
* **💰 Cost & ROI Analysis:** Get instant financial breakdowns, installation costs, monthly utility bill savings, and estimated payback period (ROI).
* **📐 Interactive Rooftop CAD & Visualization:**
  * **Level 1 (2D Blueprint):** Visual representation of panel layouts based on available roof area.
  * **Level 2 (3D Model):** Interactive 3D building visualization using Pydeck with geographic coordinates.
  * **Level 3 (Satellite Placement):** High-resolution Google Satellite map where users can enter coordinates or **click directly on their roof** to simulate realistic solar panel layout.
* **🌦️ Live Weather Solar Tracker:** Integrated with OpenWeatherMap API to simulate real-time solar power generation based on cloud coverage and temperature for Bangladesh cities or custom map locations.
* **🌐 Multi-Language Support:** Easily toggle between **English** and **বাংলা**.

---

## 🛠️ Tech Stack

* **Frontend & Framework:** [Streamlit](https://streamlit.io/)
* **Data Visualization:** Plotly Express, Matplotlib
* **Maps & Geographic Visualizations:** Folium, Pydeck, Streamlit-Folium
* **Data Processing:** Pandas, NumPy
* **Live Weather Data:** OpenWeatherMap REST API

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.8 or higher installed on your machine.

### Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sohelmd0188/SS-SunPower-Calculator-Solario.git](https://github.com/sohelmd0188/SS-SunPower-Calculator-Solario.git)
   cd SS-SunPower-Calculator-Solario

2. **Install required packages:**
   ```bash
   pip install streamlit pandas plotly matplotlib numpy pydeck folium streamlit-folium requests

3. **Run the Streamlit App:**
   ```bash
   streamlit run app.py

 👤 Author
Mohammad Sohel
GitHub: @sohelmd0188
