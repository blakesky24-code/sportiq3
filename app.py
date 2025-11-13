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
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
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
            if events:
                return pd.DataFrame(events)
        elif r.status_code == 403:
            st.error("⚠️ Access denied — make sure you’re subscribed to the RapidSports API.")
            return pd.DataFrame()
    
    st.warning("No live or scheduled matches found.")
    return pd.DataFrame()
