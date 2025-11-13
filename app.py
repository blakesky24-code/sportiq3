import streamlit as st
import requests
import pandas as pd

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="SportIQ 4.0", layout="wide")
st.title("🏆 SportIQ 4.0 — Live Multi-Sport Predictor")
st.caption("Powered by RapidAPI • Auto-fetches multiple sports data")

# -------------------- API SETTINGS --------------------
API_KEY = st.secrets.get("RAPIDAPI_KEY", None)
if not API_KEY:
    st.error("❌ API key missing! Please add RAPIDAPI_KEY in Streamlit Secrets.")
    st.stop()

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "rapidsports.p.rapidapi.com"
}

ENDPOINTS = {
    "Soccer": "https://rapidsports.p.rapidapi.com/v1/stage/current-live-events",
    "Basketball": "https://rapidsports.p.rapidapi.com/v1/stage/current-live-events",
    "Tennis": "https://rapidsports.p.rapidapi.com/v1/stage/current-live-events",
    "Cricket": "https://rapidsports.p.rapidapi.com/v1/stage/current-live-events",
}

# -------------------- FUNCTION TO FETCH --------------------
def get_live_matches(sport):
    url = ENDPOINTS.get(sport)
    if not url:
        st.warning(f"No API endpoint found for {sport}")
        return pd.DataFrame()
    
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            events = data.get("events") or data.get("data") or []
            matches = []
            for e in events:
                home = e.get("homeTeam", {}).get("name", "Unknown")
                away = e.get("awayTeam", {}).get("name", "Unknown")
                matches.append({"Sport": sport, "Home Team": home, "Away Team": away})
            return pd.DataFrame(matches)
        elif r.status_code == 403:
            st.error("🚫 Access denied (403). Check your RapidAPI subscription plan.")
        elif r.status_code == 404:
            st.warning("⚠️ Data not found (404). Endpoint may not support this sport.")
        else:
            st.error(f"Unexpected error: {r.status_code}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return pd.DataFrame()

# -------------------- UI SECTION --------------------
st.sidebar.header("Choose a Sport")
sport_choice = st.sidebar.selectbox("Select a Sport", list(ENDPOINTS.keys()))

if st.sidebar.button("Fetch Live Data"):
    with st.spinner("Fetching live match data..."):
        df = get_live_matches(sport_choice)
        if df.empty:
            st.warning("No live matches found.")
        else:
            st.success("✅ Matches fetched successfully!")
            st.dataframe(df)
else:
    st.info("Click **Fetch Live Data** to load matches.")
