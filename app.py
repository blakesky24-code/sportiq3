import streamlit as st, pandas as pd, numpy as np, requests
from sklearn.linear_model import LogisticRegression

st.set_page_config(page_title="SportIQ 3.0", layout="wide")
st.title("⚽ SportIQ 3.0 — Multi-Sport Live Predictor")
st.caption("Dark SofaScore theme • powered by API-SPORTS + AI")

# 🔑 Your API key from API-SPORTS
API_KEY = st.secrets["SPORTS_API_KEY"]

# 🏟️ Official API-Sports endpoints
ENDPOINTS = {
    "football":   "https://v3.football.api-sports.io/fixtures?live=all",
    "basketball": "https://v1.basketball.api-sports.io/games?live=all",
    "baseball":   "https://v1.baseball.api-sports.io/games?live=all",
    "tennis":     "https://v1.tennis.api-sports.io/matches?live=all",
    "hockey":     "https://v1.hockey.api-sports.io/games?live=all",
    "rugby":      "https://v1.rugby.api-sports.io/matches?live=all",
    "cricket":    "https://v1.cricket.api-sports.io/matches"
}

# 🧠 Basic logistic model (demo predictor)
def tiny_model():
    s = pd.DataFrame({
        "home_odds":[1.9,2.1,1.8,1.7,2.4],
        "away_odds":[3.5,3.2,3.8,4.0,2.9],
        "result":[1,0,1,1,0]
    })
    X, y = s[["home_odds","away_odds"]], s["result"]
    return LogisticRegression().fit(X,y)

model = tiny_model()

# ⚙️ Data fetching
def get_data(sport):
    url = ENDPOINTS[sport]
    headers = {"x-apisports-key": API_KEY}
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

# 🧭 Sidebar UI
sport = st.sidebar.selectbox(
    "Select a sport",
    list(ENDPOINTS.keys())
)

# 🎮 Fetch button
if st.sidebar.button("Fetch Live Matches"):
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
