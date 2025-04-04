import streamlit as st
import urllib.parse
import warnings
from influxdb_client import InfluxDBClient
from influxdb_client.client.warnings import MissingPivotFunction
import pandas as pd

# ----------------------------------------
# 🛑 Suppress Influx Pivot Warning
# ----------------------------------------
warnings.simplefilter("ignore", MissingPivotFunction)

# ----------------------------------------
# 🔧 InfluxDB Configuration
# ----------------------------------------
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "-FfI2tVAZBOrkEZgL28RH0VUK7fNSC0NNjih5IXx4nI6dhqCkndTI50M5hbPy_c0OvZlDX5m3UdlEh15_bdaXQ=="
INFLUXDB_ORG = "aismartlive"
BUCKET = "feedback"

# ----------------------------------------
# 🌐 Grafana Configuration
# ----------------------------------------
GRAFANA_BASE_URL = "http://localhost:3000/d/eehrru8su8vlsb/fe"
GRAFANA_ORG_ID = "1"

@st.cache_data
def fetch_departments():
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()

    flux = f'''
    import "influxdata/influxdb/schema"
    schema.tagValues(bucket: "{BUCKET}", tag: "department")
    '''
    try:
        df = query_api.query_data_frame(flux)
        departments = df["_value"].dropna().unique().tolist()
        departments.sort()
        return ["All"] + departments  # 👈 Add 'All' at the beginning
    except Exception as e:
        st.error(f"⚠️ Failed to fetch departments: {e}")
        return []

# ----------------------------------------
# 🖼️ Streamlit UI Setup
# ----------------------------------------
st.set_page_config(page_title="Clinic Feedback Dashboard", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #fafafa;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    iframe {
        border: 1px solid #ddd;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 Pulse360")
st.subheader("📊 Complete Insight into Patient Experience & Care Trends")

# ----------------------------------------
# 🔽 Department Selection
# ----------------------------------------
departments = fetch_departments()
if not departments:
    st.warning("No departments available.")
    st.stop()

selected_department = st.selectbox("Select Department", departments)

# ----------------------------------------
# 🔗 Build Grafana Embed URL
# ----------------------------------------
params = {
    "orgId": GRAFANA_ORG_ID,
    "from": "now-3h",
    "to": "now",
    "timezone": "browser",
    "refresh": "5s",
}

# If department is not "All", add the variable to the Grafana URL
if selected_department != "All":
    params["var-department"] = selected_department

grafana_url = f"{GRAFANA_BASE_URL}?{urllib.parse.urlencode(params)}"

# ----------------------------------------
# 📺 Display Embedded Grafana Dashboard
# ----------------------------------------
st.markdown(f"""
<iframe
    src="{grafana_url}"
    width="100%"
    height="1000"
    frameborder="0"
    allowfullscreen>
</iframe>
""", unsafe_allow_html=True)
