import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="SportIQ 3.0", layout="wide")

st.title("⚽ SportIQ 3.0 — Multi-Sport Predictor")
st.caption("Powered by RapidAPI Sports Data")

API_KEY = st.secrets.get("RAPIDAPI_KEY", None)

if not API_KEY:
    st.error("❌ API key not found. Please add RAPIDAPI_KEY in Streamlit Secrets.")
    st.stop()

def get_live_events():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "rapidsports.p.rapidapi.com"
    }

    urls = [
        "https://rapidsports.p.rapidapi.com/v1/sport/events/live",
        "https://rapidsports.p.rapidapi.com/v1/sport/scheduled",
        "https://rapidsports.p.rapidapi.com/v1/sport/events"
    ]

    for url in urls:
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                matches = []
                for m in data.get("data", []):
                    home = m.get("homeTeam", {}).get("name", "Unknown")
                    away = m.get("awayTeam", {}).get("name", "Unknown")
                    sport = m.get("sport", {}).get("name", "N/A")
                    matches.append({
                        "Sport": sport,
                        "Home Team": home,
                        "Away Team": away
                    })
                if matches:
                    return pd.DataFrame(matches)
            elif r.status_code == 403:
                st.error("🚫 403 Forbidden — Check your API plan or host name.")
                return pd.DataFrame()
            elif r.status_code == 404:
                st.warning("⚠️ 404 Not Found — Endpoint might not exist.")
                continue
        except Exception as e:
            st.error(f"Request failed: {e}")
    return pd.DataFrame()

st.sidebar.header("Controls")
if st.sidebar.button("Fetch Live Matches"):
    with st.spinner("Fetching live data..."):
        df = get_live_events()
        if df.empty:
            st.warning("No live or scheduled matches found.")
        else:
            st.success("✅ Data fetched successfully!")
            st.dataframe(df)
else:
    st.info("Click **Fetch Live Matches** to get current data.")
