import json
import os
import requests
from bs4 import BeautifulSoup

def fetch_github_contributions(username="[YOUR_GITHUB_USERNAME]"):
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        raise Exception(f"Failed to fetch user contributions: {res.status_code}")

    soup = BeautifulSoup(res.content, "html.parser")
    days = soup.find_all("td", class_="ContributionCalendar-day")
    
    calendar_data = []
    total_contributions = 0
    
    for day in days:
        date = day.get("data-date")
        count = day.get("data-count")
        level = day.get("data-level", "0")
        
        if date:
            c_count = int(count) if count else 0
            calendar_data.append({
                "date": date,
                "count": c_count,
                "level": int(level)
            })
            total_contributions += c_count
            
    # Calculate Streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    best_day = {"date": "", "count": 0}
    
    for item in calendar_data:
        cnt = item["count"]
        if cnt > best_day["count"]:
            best_day = {"date": item["date"], "count": cnt}
            
        if cnt > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
    # Current streak from end
    for item in reversed(calendar_data):
        if item["count"] > 0:
            current_streak += 1
        else:
            break

    output = {
        "total": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": calendar_data
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Saved raw contribution metrics to data/contributions.json")

if __name__ == "__main__":
    fetch_github_contributions()
