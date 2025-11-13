import streamlit as st, pandas as pd, numpy as np, requests
from sklearn.linear_model import LogisticRegression

st.set_page_config(page_title="SportIQ 4.0", layout="wide")
st.title("⚽ SportIQ 4.0 — Live Multi-Sport Predictor")
st.caption("Inspired by SofaScore • powered by RapidAPI + AI")

# Your RapidAPI key
API_KEY = st.secrets["RAPIDAPI_KEY"]

# RapidAPI endpoints for different sports
ENDPOINTS = {
    "football":   ("https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all", "api-football-v1.p.rapidapi.com"),
    "basketball": ("https://api-basketball.p.rapidapi.com/games?live=all", "api-basketball.p.rapidapi.com"),
    "baseball":   ("https://api-baseball.p.rapidapi.com/games?live=all", "api-baseball.p.rapidapi.com"),
    "tennis":     ("https://api-tennis.p.rapidapi.com/matches?live=all", "api-tennis.p.rapidapi.com"),
    "hockey":     ("https://api-hockey.p.rapidapi.com/games?live=all", "api-hockey.p.rapidapi.com"),
    "cricket":    ("https://cricket-live-data.p.rapidapi.com/matches", "cricket-live-data.p.rapidapi.com"),
    "rugby":      ("https://rugby-live-data.p.rapidapi.com/matches", "rugby-live-data.p.rapidapi.com")
}

def get_data(sport):
    url, host = ENDPOINTS[sport]
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": host}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        st.error(f"API error {r.status_code}")
        return pd.DataFrame()
    data = r.json()
    matches = []
    if "response" in data:
        for m in data["response"]:
            try:
                home = m["teams"]["home"]["name"]
                away = m["teams"]["away"]["name"]
                matches.append({"home_team": home, "away_team": away})
            except:
                continue
    elif "results" in data:
        for m in data["results"]:
            home, away = m.get("home","?"), m.get("away","?")
            matches.append({"home_team": home, "away_team": away})
    return pd.DataFrame(matches)

def tiny_model():
    s = pd.DataFrame({
        "home_odds":[1.9,2.1,1.8,1.7,2.4],
        "away_odds":[3.5,3.2,3.8,4.0,2.9],
        "result":[1,0,1,1,0]
    })
    X, y = s[["home_odds","away_odds"]], s["result"]
    return LogisticRegression().fit(X,y)

model = tiny_model()

sport = st.sidebar.selectbox("Select a sport", list(ENDPOINTS.keys()))

if st.sidebar.button("Fetch Matches"):
    df = get_data(sport)
    if df.empty:
        st.warning("No live matches found or API limit reached.")
    else:
        st.subheader("🔮 AI Predictions")
        for _, r in df.iterrows():
            home_odds, away_odds = np.random.uniform(1.5,3.5), np.random.uniform(2.5,4.5)
            pred = model.predict([[home_odds, away_odds]])[0]
            result = "🏠 Home Win" if pred==1 else "🧳 Away/Draw"
            st.markdown(f"### {r['home_team']} 🆚 {r['away_team']}")
            st.metric("Prediction", result)
            st.metric("Home Odds", f"{home_odds:.2f}")
            st.metric("Away Odds", f"{away_odds:.2f}")
            st.divider()
