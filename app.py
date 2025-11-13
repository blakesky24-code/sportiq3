import streamlit as st
import requests
import pandas as pd
import numpy as np

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="SportIQ 4.0 — Multi-Sport AI", layout="wide")
st.title("🏆 SportIQ 4.0 — Multi-Sport Betting Predictor")
st.caption("Inspired by SofaScore • Powered by Betting-API.com + AI")

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
                home = item.get("home", {}).get("name", "Unknown")
                away = item.get("away", {}).get("name", "Unknown")
                league = item.get("league", {}).get("name", "Unknown League")
                country = item.get("league", {}).get("country", "N/A")
                odds = item.get("odds", {})

                if isinstance(odds, list) and len(odds) > 0:
                    odds = odds[0]

                if isinstance(odds, dict):
                    home_odds = float(odds.get("home", np.nan))
                    draw_odds = float(odds.get("draw", np.nan))
                    away_odds = float(odds.get("away", np.nan))
                else:
                    home_odds = draw_odds = away_odds = np.nan

                # --- Simple AI Prediction ---
                if not np.isnan(home_odds) and not np.isnan(away_odds):
                    if home_odds < away_odds:
                        prediction = "🏠 Home Win"
                        confidence = (away_odds / home_odds) * 10
                    elif away_odds < home_odds:
                        prediction = "🛫 Away Win"
                        confidence = (home_odds / away_odds) * 10
                    else:
                        prediction = "🤝 Draw"
                        confidence = 5.0
                else:
                    prediction = "N/A"
                    confidence = np.nan

                matches.append({
                    "League": league,
                    "Country": country,
                    "Home Team": home,
                    "Away Team": away,
                    "Home Odds": home_odds,
                    "Draw Odds": draw_odds,
                    "Away Odds": away_odds,
                    "Predicted Winner": prediction,
                    "Confidence (%)": round(confidence, 2)
                })

            return pd.DataFrame(matches)

        elif r.status_code == 401:
            st.error("🚫 Unauthorized — Invalid API key.")
        elif r.status_code == 403:
            st.error("⛔ Forbidden — API key not allowed for this plan.")
        elif r.status_code == 404:
            st.error("❗ Endpoint not found — check API sport URL.")
        else:
            st.error(f"❌ API error {r.status_code}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return pd.DataFrame()

# -------------------- UI --------------------
st.sidebar.header("⚙️ SportIQ Control Panel")
sport_choice = st.sidebar.selectbox("Select a sport", list(BASE_URLS.keys()))

if st.sidebar.button("🎯 Fetch Live Matches"):
    with st.spinner("Fetching live odds from Betting API..."):
        df = fetch_odds(sport_choice)
        if df.empty:
            st.warning("No live or scheduled matches found right now.")
        else:
            st.success("✅ Data fetched successfully!")
            
            # Filters
            all_leagues = sorted(df["League"].dropna().unique())
            league_filter = st.sidebar.multiselect("Filter by League", all_leagues)
            if league_filter:
                df = df[df["League"].isin(league_filter)]

            st.subheader(f"📊 Live Matches — {sport_choice}")
            st.dataframe(df, use_container_width=True)

            # --- TOP PREDICTIONS ---
            st.subheader("🔥 Top Predicted Matches")
            top_df = df.dropna(subset=["Confidence (%)"]).sort_values(
                by="Confidence (%)", ascending=False
            ).head(10)
            if not top_df.empty:
                st.dataframe(top_df, use_container_width=True)
            else:
                st.info("No high-confidence predictions found right now.")
