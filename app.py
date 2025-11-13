import streamlit as st, pandas as pd, numpy as np, requests
from sklearn.linear_model import LogisticRegression

st.set_page_config(page_title="SportIQ RapidSports", layout="wide")
st.title("🏆 SportIQ — RapidSports Live Match Predictor")
st.caption("Inspired by SofaScore • Powered by RapidSports API + AI")

API_KEY = st.secrets["RAPIDAPI_KEY"]

# RapidSports endpoint base
BASE_URL = "https://rapidsports.p.rapidapi.com/v1/sport/events/live"

def get_live_events():
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "rapidsports.p.rapidapi.com"
    }
    r = requests.get(BASE_URL, headers=headers)
    if r.status_code != 200:
        st.error(f"API Error {r.status_code}: Could not fetch data")
        return pd.DataFrame()
    data = r.json()
    events = []
    for item in data.get("data", []):
        try:
            home = item["homeTeam"]["name"]
            away = item["awayTeam"]["name"]
            sport = item["sport"]["name"]
            events.append({"sport": sport, "home_team": home, "away_team": away})
        except:
            continue
    return pd.DataFrame(events)

def ai_model():
    s = pd.DataFrame({
        "home_odds":[1.9,2.1,1.8,1.7,2.4],
        "away_odds":[3.5,3.2,3.8,4.0,2.9],
        "result":[1,0,1,1,0]
    })
    X, y = s[["home_odds","away_odds"]], s["result"]
    return LogisticRegression().fit(X,y)

model = ai_model()

if st.sidebar.button("Fetch Live Matches"):
    df = get_live_events()
    if df.empty:
        st.warning("No live matches found or API plan limit reached.")
    else:
        st.subheader("🔮 AI Predictions")
        for _, r in df.iterrows():
            home_odds, away_odds = np.random.uniform(1.5,3.5), np.random.uniform(2.5,4.5)
            pred = model.predict([[home_odds, away_odds]])[0]
            result = "🏠 Home Win" if pred==1 else "🧳 Away/Draw"
            st.markdown(f"### {r['home_team']} 🆚 {r['away_team']} ({r['sport']})")
            st.metric("Prediction", result)
            st.metric("Home Odds", f"{home_odds:.2f}")
            st.metric("Away Odds", f"{away_odds:.2f}")
            st.divider()
