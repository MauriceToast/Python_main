from datetime import datetime, date
import csv
import os
import requests
from io import StringIO


team_prestige = {
    "Detroit Red Wings": 12 / 20,
    "Montreal Canadiens": 14 / 20,
    "Boston Bruins": 14 / 20,
    "Tampa Bay Lightning": 12 / 20,
    "Florida Panthers": 18 / 20,
    "Ottawa Senators": 11 / 20,
    "Toronto Maple Leafs" : 12 / 20,
    "Buffalo Sabres": 9 / 20,

    "Carolina Hurricanes": 16 / 20,
    "Washington Capitals": 16 / 20,
    "New York Islanders": 10 / 20,
    "Philadelphia Flyers": 12 / 20,
    "New Jersey Devils": 13 / 20,
    "New York Rangers": 11 / 20,
    "Pittsburgh Penguins": 11 / 20,
    "Columbus Blue Jackets": 12 / 20,

     "Colorado Avalanche": 17 / 20,
     "Dallas Stars": 16 / 20,
     "Minnesota Wild": 14 / 20,
     "Utah Mammoth": 11 / 20,
     "St.Louis Blues": 10 / 20,
     "Winnipeg Jets": 12 / 20,
     "Chicago Blackhawks": 10 / 20
     "Nashville Predators": 09 / 20,

     "Vegas Golden Knights": 14 / 20
     "Anaheim Ducks": 12 / 20
     "Edmonton Oilers": 16 / 20
     "Los Angeles Kings": 11 / 20,
     "San Jose Sharks": 11 / 20,
     "Calgary Flames": 10 / 20,
     "Seattle Kraken": 10 / 20,
     "Vancouver Canucks": 10 / 20,
}


def replace_team_names(team_name):
    replacements = {
        "Genève": "Geneve",
        # Add more replacements here if needed
    }
    return replacements.get(team_name, team_name)


base_url = "https://raw.githubusercontent.com/MauriceToast/Python_main/main/"

french_months = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}


def parse_french_date(date_str):
    day, month, year = date_str.split()
    month_num = french_months[month.lower()]
    return datetime(int(year), month_num, int(day))


def fetch_rankings_data():
    rankings_data = {"Atlantic": [], "Metropolitan": [], "Central": [], "Pacific": []}
    # Atlantic
    url_a = base_url + "NHL_AtlanticDivision_rankings.csv"
    response_a = requests.get(url_a)
    if response_a.status_code == 200:
        content_a = StringIO(response_a.text)
        reader_a = csv.DictReader(content_a)
        for row in reader_a:
            rankings_data["Atlantic"].append(row)
    #Metropolitan
    url_b = base_url + "NHL_MetropolitanDivision_rankings.csv"
    response_b = requests.get(url_b)
    if response_b.status_code == 200:
        content_b = StringIO(response_b.text)
        reader_b = csv.DictReader(content_b)
        for row in reader_b:
            rankings_data["Metropolitan"].append(row)
    #Central
    url_c = base_url + "NHL_CentralDivision_rankings.csv"
    response_c = requests.get(url_c)
    if response_c.status_code == 200:
        content_c = StringIO(response_c.text)
        reader_c = csv.DictReader(content_c)
        for row in reader_c:
            rankings_data["Central"].append(row)
    #Pacific
    url_d = base_url + "NHL_PacificDivision_rankings.csv"
    response_d = requests.get(url_d)
    if response_d.status_code == 200:
        content_d = StringIO(response_d.text)
        reader_d = csv.DictReader(content_d)
        for row in reader_d:
            rankings_data["Pacific"].append(row)
    return rankings_data

def fetch_matches_data():
    matches_data = []
    url = base_url + "nhl_matches.csv"
    response = requests.get(url)
    if response.status_code == 200:
        content = StringIO(response.text)
        reader = csv.DictReader(content)
        for row in reader:
            matches_data.append(row)
    return matches_data


def calculate_bookmaker_quotes(team1, team2, rankings_data, matches_data, date_str):
    date_obj = parse_french_date(date_str)
    formatted_date = date_obj.strftime('%Y-%m-%d')

    # Define weights for each factor (must sum to 1)
    weights = {
        'points_ratio': 0.4,
        'prestige': 0.3,
        'home_advantage': 0.2,
        'goal_difference': 0.1
    }
    assert sum(weights.values()) == 1, "Weights must sum to 1"

    group = None
    for g in ['GrpA', 'GrpB']:
        teams = [r['team'] for r in rankings_data[g]]
        if team1 in teams and team2 in teams:
            group = g
            break
    if group is None:
        print(f"Teams {team1} and {team2} not found in the same group.")

    group_rankings = rankings_data[group]
    team1_data = next((r for r in group_rankings if r['team'] == team1), None)
    team2_data = next((r for r in group_rankings if r['team'] == team2), None)

    if not team1_data or not team2_data:
        print(f"Missing data for one or both teams: {team1} vs {team2}. Using default odds.")
        default_odds = {
            'team1': 2.0,
            'team2': 2.0,
            'draw': 3.0,
            'team1_extra': 4.0,
            'team2_extra': 4.0
        }
        save_quotes(date_str, f"{team1} - {team2}", default_odds)
        return default_odds

    # Initialize probabilities
    team1_prob = 0.5
    team2_prob = 0.5

    # 1. Points ratio
    team1_points_ratio = int(team1_data['points']) / max(int(team1_data['games_played']), 1)
    team2_points_ratio = int(team2_data['points']) / max(int(team2_data['games_played']), 1)
    total_points_ratio = team1_points_ratio + team2_points_ratio

    if total_points_ratio == 0:
        # Avoid division by zero: skip this factor, or use default odds, or set equal probability
        print(f"Both teams {team1} and {team2} have zero points ratio. Using default odds.")
        default_odds = {
            'team1': 2.0,
            'team2': 2.0,
            'draw': 3.0,
            'team1_extra': 4.0,
            'team2_extra': 4.0
        }
        save_quotes(date_str, f"{team1} - {team2}", default_odds)
        return default_odds

    team1_prob += weights['points_ratio'] * (team1_points_ratio / total_points_ratio - 0.5)
    team2_prob += weights['points_ratio'] * (team2_points_ratio / total_points_ratio - 0.5)
    # 2. Team prestige
    team1_prestige = team_prestige.get(team1.upper(), 10 / 20)
    team2_prestige = team_prestige.get(team2.upper(), 10 / 20)
    team1_prob += weights['prestige'] * (team1_prestige - 0.5)
    team2_prob += weights['prestige'] * (team2_prestige - 0.5)

    # 3. Home advantage
    team1_prob += weights['home_advantage'] * 0.1  # 10% advantage for home team
    team2_prob -= weights['home_advantage'] * 0.1

    # 4. Goal difference
    team1_goal_diff = (int(team1_data['goals_for']) - int(team1_data['goals_against'])) / int(
        team1_data['games_played'])
    team2_goal_diff = (int(team2_data['goals_for']) - int(team2_data['goals_against'])) / int(
        team2_data['games_played'])
    total_goal_diff = abs(team1_goal_diff) + abs(team2_goal_diff)
    if total_goal_diff != 0:
        team1_prob += weights['goal_difference'] * (team1_goal_diff / total_goal_diff)
        team2_prob += weights['goal_difference'] * (team2_goal_diff / total_goal_diff)

    # Normalize probabilities for regular time outcomes
    total_prob = team1_prob + team2_prob
    team1_prob /= total_prob
    team2_prob /= total_prob

    # Calculate draw probability
    draw_prob = max(0.15, min(0.3, 1 - (team1_prob + team2_prob)))

    # Adjust regular win probabilities
    team1_prob *= (1 - draw_prob)
    team2_prob *= (1 - draw_prob)

    # Calculate extra time probabilities
    # We'll assume extra time odds are slightly lower than regular time
    extra_time_factor = 0.8  # This factor makes extra time odds ~20% lower than regular time
    team1_extra_prob = team1_prob * extra_time_factor
    team2_extra_prob = team2_prob * extra_time_factor

    # Apply bookmaker's margin (5%)
    margin = 0.05
    margin_factor = 1 - margin

    # Convert probabilities to odds
    team1_odds = 1 / (team1_prob / margin_factor)
    team2_odds = 1 / (team2_prob / margin_factor)
    team1_extra_odds = 1 / (team1_extra_prob / margin_factor)
    team2_extra_odds = 1 / (team2_extra_prob / margin_factor)
    draw_odds = 1 / (draw_prob / margin_factor)

    # Cap draw odds at 5.5 if necessary
    max_draw_odds = 5.5
    if draw_odds > max_draw_odds:
        draw_odds = max_draw_odds

    final_odds = {
        'team1': round(max(1.01, team1_odds), 2),
        'team2': round(max(1.01, team2_odds), 2),
        'team1_extra': round(max(1.01, team1_extra_odds), 2),
        'team2_extra': round(max(1.01, team2_extra_odds), 2),
        'draw': round(max(1.01, min(draw_odds, max_draw_odds)), 2)
    }

    # Save the calculated quotes
    match_id = f"{team1} - {team2}"
    save_quotes(date_str, match_id, final_odds)

    print(f"Calculated odds for {team1} vs {team2}: {final_odds}")
    return final_odds

    # Normalize probabilities for regular time outcomes
    total_prob = team1_prob + team2_prob
    team1_prob /= total_prob
    team2_prob /= total_prob

    # Calculate draw probability
    draw_prob = max(0.15, min(0.3, 1 - (team1_prob + team2_prob)))

    # Adjust regular win probabilities
    team1_prob *= (1 - draw_prob)
    team2_prob *= (1 - draw_prob)

    # Calculate extra time probabilities
    # We'll assume extra time odds are slightly lower than regular time
    extra_time_factor = 0.8  # This factor makes extra time odds ~20% lower than regular time
    team1_extra_prob = team1_prob * extra_time_factor
    team2_extra_prob = team2_prob * extra_time_factor

    # Apply bookmaker's margin (5%)
    margin = 0.05
    margin_factor = 1 - margin

    # Convert probabilities to odds
    team1_odds = 1 / (team1_prob / margin_factor)
    team2_odds = 1 / (team2_prob / margin_factor)
    team1_extra_odds = 1 / (team1_extra_prob / margin_factor)
    team2_extra_odds = 1 / (team2_extra_prob / margin_factor)
    draw_odds = 1 / (draw_prob / margin_factor)

    # Cap draw odds at 5.5 if necessary
    max_draw_odds = 5.5
    if draw_odds > max_draw_odds:
        draw_odds = max_draw_odds

    final_odds = {
        'team1': round(max(1.01, team1_odds), 2),
        'team2': round(max(1.01, team2_odds), 2),
        'team1_extra': round(max(1.01, team1_extra_odds), 2),
        'team2_extra': round(max(1.01, team2_extra_odds), 2),
        'draw': round(max(1.01, min(draw_odds, max_draw_odds)), 2)
    }

    # Save the calculated quotes
    match_id = f"{team1} - {team2}"
    save_quotes(date_str, match_id, final_odds)

    print(f"Calculated odds for {team1} vs {team2}: {final_odds}")
    return final_odds


def save_quotes(date_str, match_id, quotes):
    try:
        date_obj = parse_french_date(date_str)
        formatted_date = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        formatted_date = date_str

    csv_file = 'quotes_NHL.csv'
    file_exists = os.path.isfile(csv_file)

    # Read existing data
    existing_data = []
    if file_exists:
        with open(csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_data = list(reader)

    # Check if the match already exists
    match_exists = any(row['date'] == formatted_date and row['match'] == match_id for row in existing_data)

    if not match_exists:
        # Append new data
        with open(csv_file, 'a', newline='') as csvfile:
            fieldnames = ['date', 'match', 'team1', 'team2', 'draw', 'team1_extra', 'team2_extra']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                'date': formatted_date,
                'match': match_id,
                'team1': quotes['team1'],
                'team2': quotes['team2'],
                'draw': quotes['draw'],
                'team1_extra': quotes['team1_extra'],
                'team2_extra': quotes['team2_extra']
            })
        print(f"New quotes saved for {match_id} on {formatted_date}")
    else:
        print(f"Quotes for {match_id} on {formatted_date} already exist, skipping")


def filter_upcoming_matches(matches_data):
    today = date.today()
    upcoming_matches = []
    for match in matches_data:
        match_date = parse_french_date(match['date']).date()
        if match_date >= today and match['available'] == 'yes':
            upcoming_matches.append(match)
    return sorted(upcoming_matches, key=lambda x: parse_french_date(x['date']))


def find_next_match(team, upcoming_matches, processed_teams):
    for match in upcoming_matches:
        team1, team2 = match['match'].split(' - ')
        if (team1 == team or team2 == team) and team not in processed_teams:
            return match
    return None


def main():
    rankings_data = fetch_rankings_data()
    matches_data = fetch_matches_data()
    upcoming_matches = filter_upcoming_matches(matches_data)
    processed_teams = set()

    for team in team_prestige.keys():
        next_match = find_next_match(team, upcoming_matches, processed_teams)
        if next_match:
            team1, team2 = next_match['match'].split(' - ')
            match_date = next_match['date']
            odds = calculate_bookmaker_quotes(team1, team2, rankings_data, matches_data, match_date)
            print(f"Calculated odds for {team1} vs {team2} on {match_date}: {odds}")
            processed_teams.add(team1)
            processed_teams.add(team2)


main()
