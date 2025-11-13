import streamlit as st
import requests
import pandas as pd

# -------------------- PAGE SETTINGS --------------------
st.set_page_config(page_title="SportIQ 5.0", layout="wide")
st.title("🏆 SportIQ 5.0 — Multi-Sport Live & Upcoming Matches")
st.caption("Powered by RapidAPI Sports Data (Auto fetches from multiple sports)")

# -------------------- API SETTINGS --------------------
API_KEY = st.secrets.get("RAPIDAPI_KEY", None)
if not API_KEY:
    st.error("❌ API key missing. Please add RAPIDAPI_KEY in Streamlit secrets.")
    st.stop()

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

SPORTS = {
    "Football": "https://api-football-v1.p.rapidapi.com/v3/fixtures?live=all",
    "Basketball": "https://api-basketball.p.rapidapi.com/games?live=all",
    "Baseball": "https://api-baseball.p.rapidapi.com/games?live=all",
    "Hockey": "https://api-hockey.p.rapidapi.com/games?live=all",
    "Formula 1": "https://api-formula-1.p.rapidapi.com/races?live=all"
}

UPCOMING = {
    "Football": "https://api-football-v1.p.rapidapi.com/v3/fixtures?next=10",
    "Basketball": "https://api-basketball.p.rapidapi.com/games?next=10",
    "Baseball": "https://api-baseball.p.rapidapi.com/games?next=10",
    "Hockey": "https://api-hockey.p.rapidapi.com/games?next=10",
    "Formula 1": "https://api-formula-1.p.rapidapi.com/races?next=10"
}

# -------------------- FETCH FUNCTION --------------------
def fetch_matches(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            matches = []
            for m in data.get("response", []):
                home = m.get("teams", {}).get("home", {}).get("name", "Unknown")
                away = m.get("teams", {}).get("away", {}).get("name", "Unknown")
                league = m.get("league", {}).get("name", "N/A")
                date = m.get("fixture", {}).get("date", "N/A")
                matches.append({"League": league, "Home": home, "Away": away, "Date": date})
            return pd.DataFrame(matches)
        elif response.status_code == 404:
            st.warning("⚠️ Endpoint not found (404). This sport may not have data right now.")
        elif response.status_code == 403:
            st.error("🚫 Access denied (403). Check your RapidAPI plan permissions.")
        else:
            st.error(f"❌ Unexpected API error: {response.status_code}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return pd.DataFrame()

# -------------------- UI --------------------
st.sidebar.header("Choose your sport")
sport_choice = st.sidebar.selectbox("Select Sport", list(SPORTS.keys()))

if st.sidebar.button("Fetch Live Matches"):
    with st.spinner("Fetching live matches..."):
        df = fetch_matches(SPORTS[sport_choice])
        if df.empty:
            st.warning("No live matches found. Try fetching upcoming games below.")
        else:
            st.success("✅ Live matches loaded successfully!")
            st.dataframe(df)

if st.sidebar.button("Fetch Upcoming Matches"):
    with st.spinner("Fetching upcoming matches..."):
        df2 = fetch_matches(UPCOMING[sport_choice])
        if df2.empty:
            st.warning("No upcoming matches available.")
        else:
            st.success("✅ Upcoming matches loaded successfully!")
            st.dataframe(df2)
