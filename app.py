import streamlit as st
import requests
import pandas as pd
import numpy as np

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="SportIQ — Betting AI", layout="wide")
st.title("🏆 SportIQ — Live Betting Odds & Match Predictor")
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

            # Handle both list and dict responses
            if isinstance(data, list):
                raw_data = data
            elif isinstance(data, dict) and "data" in data:
                raw_data = data["data"]
            else:
                raw_data = []

            matches = []
            for item in raw_data:
                home = (
                    item.get("home", {}).get("name")
                    if isinstance(item.get("home"), dict)
                    else "Unknown"
                )
                away = (
                    item.get("away", {}).get("name")
                    if isinstance(item.get("away"), dict)
                    else "Unknown"
                )
                league = (
                    item.get("league", {}).get("name")
                    if isinstance(item.get("league"), dict)
                    else "Unknown League"
                )
                odds = item.get("odds", {})

                # Some APIs return list of odds
                if isinstance(odds, list) and len(odds) > 0:
                    odds = odds[0]

                if isinstance(odds, dict):
                    home_odds = odds.get("home", np.nan)
                    draw_odds = odds.get("draw", np.nan)
                    away_odds = odds.get("away", np.nan)
                else:
                    home_odds = draw_odds = away_odds = np.nan

                # --- Simple AI-based winner prediction ---
                if not np.isnan(home_odds) and not np.isnan(away_odds):
                    if home_odds < away_odds:
                        prediction = "🏠 Home Win"
                    elif away_odds < home_odds:
                        prediction = "🛫 Away Win"
                    else:
                        prediction = "🤝 Draw"
                else:
                    prediction = "N/A"

                matches.append({
                    "League": league,
                    "Home Team": home,
                    "Away Team": away,
                    "Home Odds": home_odds,
                    "Draw Odds": draw_odds,
                    "Away Odds": away_odds,
                    "Predicted Winner": prediction
                })

            return pd.DataFrame(matches)

        elif r.status_code == 401:
            st.error("🚫 Unauthorized — your Betting API key may be invalid.")
        elif r.status_code == 403:
            st.error("⛔ Forbidden — your API plan may not allow this endpoint.")
        elif r.status_code == 404:
            st.error("❗ Endpoint not found — check the API URL.")
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
