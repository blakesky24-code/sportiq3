import streamlit as st
import requests
import pandas as pd

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="SportIQ — Betting AI", layout="wide")
st.title("🏆 SportIQ — Live Betting Odds & Match Tracker")
st.caption("Powered by Betting-API.com • Real-time odds + AI predictions")

# -------------------- API SETTINGS --------------------
API_KEY = st.secrets.get("BETTING_API_KEY", None)
if not API_KEY:
    st.error("❌ Missing BETTING_API_KEY in Streamlit secrets.")
    st.stop()

BASE_URLS = {
    "Football": "https://api.betting-api.com/1xbet/football/line/all",
    "Basketball": "https://api.betting-api.com/1xbet/basketball/line/all",
    "Tennis": "https://api.betting-api.com/1xbet/tennis/line/all"
}

HEADERS = {"authorization": API_KEY}

# -------------------- FETCH FUNCTION --------------------
def fetch_odds(sport):
    url = BASE_URLS.get(sport)
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            matches = []
            for item in data.get("data", []):
                home = item.get("home", {}).get("name", "Unknown")
                away = item.get("away", {}).get("name", "Unknown")
                league = item.get("league", {}).get("name", "Unknown League")
                odds = item.get("odds", {})
                home_odds = odds.get("home", "N/A")
                draw_odds = odds.get("draw", "N/A")
                away_odds = odds.get("away", "N/A")
                matches.append({
                    "League": league,
                    "Home Team": home,
                    "Away Team": away,
                    "Home Odds": home_odds,
                    "Draw Odds": draw_odds,
                    "Away Odds": away_odds
                })
            return pd.DataFrame(matches)
        elif r.status_code == 401:
            st.error("🚫 Unauthorized — your Betting API key may be invalid.")
        elif r.status_code == 403:
            st.error("⛔ Forbidden — API key or plan access issue.")
        elif r.status_code == 404:
            st.error("❗ Endpoint not found — check API URL or sport name.")
        else:
            st.error(f"❌ API error {r.status_code}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return pd.DataFrame()

# -------------------- UI --------------------
st.sidebar.header("Select Sport")
sport_choice = st.sidebar.selectbox("Choose a sport", list(BASE_URLS.keys()))

if st.sidebar.button("Fetch Live Matches"):
    with st.spinner("Fetching data from Betting API..."):
        df = fetch_odds(sport_choice)
        if df.empty:
            st.warning("No data found for this sport right now.")
        else:
            st.success("✅ Matches and odds fetched successfully!")
            st.dataframe(df)
