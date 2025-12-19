from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from datetime import datetime

def replace_team_names(team_name):
    replacements = {
        "Genève": "Geneve",
        # Add more replacements here if needed
    }
    return replacements.get(team_name, team_name)

def deduplicate_matches(matches_data):
    """Remove duplicate matches based on date + match combination"""
    seen = set()
    unique_matches = []
    for match in matches_data:
        match_key = f"{match['date']} - {match['match']}"
        if match_key not in seen:
            seen.add(match_key)
            unique_matches.append(match)
    print(f"Deduplication: {len(matches_data)} -> {len(unique_matches)} unique matches")
    return unique_matches

def is_future_match(match):
    """Only keep matches from today onwards"""
    try:
        # Parse the French date back to datetime
        date_str = match['date']
        parts = date_str.split()
        day = int(parts[0])
        month_name = parts[1]
        year = int(parts[-1])
        
        # Month mapping
        month_map = {
            'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
            'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
        }
        month = month_map.get(month_name, 1)
        match_date = datetime(year, month, day)
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return match_date >= today
    except:
        return True  # Keep if parsing fails

web = "https://www.rts.ch/sport/resultats/#/results/hockey/nhl/Phase-1-0"
driver = None
try:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    driver.get(web)
    print(f"Webpage loaded: {web}")

    def parsefrenchdate(datestr):
        day, month, year = map(int, datestr.split('.'))
        return datetime(year, month, day)
    
    french_months = {
        1: 'janvier', 2: 'février', 3: 'mars', 4: 'avril', 5: 'mai', 6: 'juin',
        7: 'juillet', 8: 'août', 9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'
    }
    
    def format_french_date(date):
        return f"{date.day} {french_months[date.month]} {date.year}"
    
    def accept_cookies(driver):
        try:
            print("Waiting for cookie consent dialog...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "usercentrics-root"))
            )
            print("Cookie consent dialog found. Attempting to click 'Accept' button...")
            script = """
            var shadowRoot = document.querySelector("#usercentrics-root").shadowRoot;
            var button = shadowRoot.querySelector("button[data-testid='uc-deny-all-button']");
            if (button) {
                button.click();
                return true;
            }
            return false;
            """
            result = driver.execute_script(script)
            if result:
                print("Cookies accepted successfully")
            else:
                print("Failed to find or click the 'Accept' button")
            time.sleep(5)
        except Exception as e:
            print(f"Error accepting cookies: {str(e)}")
    
    
    def select_month(driver, month):
        try:
            print(f"Attempting to select month: {month}")
            month_selector = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//p[@class='stxt-scrollselection__label' and text()='{month}']"))
            )
            print(f"Month selector found for {month}")
    
            # Try regular click first
            try:
                month_selector.click()
            except:
                # If regular click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", month_selector)
    
            print(f"Clicked on month: {month}")
            time.sleep(5)
        except Exception as e:
            print(f"Error selecting month {month}: {str(e)}")
    
    def determine_win_type(score):
        return "Extra Time" if "ap" in score or "tb" in score else "Regular Time"
    
    
    def determine_winner(home_team, away_team, score):
        if score == "No Score":
            return ""  # Return empty string if no score
    
        try:
            # Clean the score by removing any trailing text
            score_parts = score.split('-')
            home_score = int(score_parts[0].strip())
            away_score = int(score_parts[1].split()[0].strip())  # Handle cases like "3 - 2 ap"
    
            if home_score > away_score:
                return home_team
            elif away_score > home_score:
                return away_team
            else:
                return ""  # In case of a tie
        except (ValueError, IndexError):
            print(f"Error determining winner: Invalid score format '{score}'")
            return ""  # Return empty string on error
    
    
    def clean_score(score):
        if score == "No Score":
            return score
        # Remove 'ap' or 'tb' from the score
        score_parts = score.split(' - ')
        cleaned_score = ' - '.join(part.split()[0] for part in score_parts)
        return cleaned_score

    def scrape_month(driver):
        try:
            teams = {
                "Detroit Red Wings", "Montreal Canadiens", "Boston Bruins", "Tampa Bay Lightning", "Florida Panthers", "Ottawa Senators", "Toronto Maple Leafs", "Buffalo Sabres",
                "Carolina Hurricanes", "Washington Capitals", "New York Islanders", "Philadelphia Flyers", "New Jersey Devils", "New York Rangers", "Pittsburgh Penguins", "Columbus Blue Jackets",
                "Colorado Avalanche", "Dallas Stars", "Minnesota Wild", "Utah Mammoth", "St.Louis Blues", "Winnipeg Jets", "Chicago Blackhawks", "Nashville Predators",
                "Vegas Golden Knights", "Anaheim Ducks", "Edmonton Oilers", "Los Angeles Kings", "San Jose Sharks", "Calgary Flames", "Seattle Kraken", "Vancouver Canucks",
            }
            
            print("Waiting for results table to load...")
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".stxt-results-table"))
            )
            print("Results table loaded.")
            
            matches_data = []
            
            # --- STEP 1: Extract all dates via span text to create a list of all dates ---
            date_elements = driver.find_elements(By.CSS_SELECTOR, ".stxt-results-table__date-inner")
            dates_text = [date.text.strip() for date in date_elements]
            print(f"Found date headers: {dates_text}")
            
            # --- STEP 2: Extract all span texts for fallback date association ---
            span_elements = driver.find_elements(By.XPATH, "//span")
            all_spans = [span.text.strip() for span in span_elements]
            
            # Create a map from each match key (home + away + score) to the corresponding date
            current_date_for_match = None
            matches_date_map = []  # list of (home_team, away_team, score, date) item placeholders
            
            temp_match = {}
            temp_score = None
            
            print("Processing spans to map matches to dates...")
            for span_text in all_spans:
                if span_text in dates_text:
                    current_date_for_match = span_text
                    temp_match = {}
                    temp_score = None
                elif current_date_for_match:
                    if span_text in teams:
                        if "home_team" not in temp_match:
                            temp_match["home_team"] = replace_team_names(span_text)
                        elif "away_team" not in temp_match:
                            temp_match["away_team"] = replace_team_names(span_text)
                            temp_match["date"] = current_date_for_match
                            temp_match["score"] = clean_score(temp_score) if temp_score else "No Score"
                            matches_date_map.append(temp_match)
                            temp_match = {}
                            temp_score = None
                    elif " - " in span_text:
                        temp_score = span_text
            
            print(f"Total matches mapped from spans: {len(matches_date_map)}")
            
            # --- STEP 3: Extract match rows and correlate with dates from step 2 ---
            rows = driver.find_elements(By.CSS_SELECTOR, "li.stxt-results-table-row")
            print(f"Found {len(rows)} match rows.")
    
            unmatched_matches = matches_date_map.copy()
            
            for i, row in enumerate(rows, start=1):
                # Extract hour
                try:
                    hour_elem = row.find_element(By.CSS_SELECTOR, "div.cell.status")
                    hour = hour_elem.text.strip()
                except Exception:
                    hour = ""
                
                # Extract home and away teams
                try:
                    home_elem = row.find_element(By.CSS_SELECTOR, "div.home span")
                    away_elem = row.find_element(By.CSS_SELECTOR, "div.away span")
                    home_team = replace_team_names(home_elem.text.strip()) if home_elem else ""
                    away_team = replace_team_names(away_elem.text.strip()) if away_elem else ""
                except Exception:
                    home_team = ""
                    away_team = ""
                    continue  # skip this row
                
                # Extract score
                try:
                    score_elem = row.find_element(By.CSS_SELECTOR, "div.cell.lrc-score")
                    score = score_elem.text.strip()
                    if score == "":
                        score = "No Score"
                except Exception:
                    score = "No Score"
                
                # Find the matching date based on team names
                matched_date = None
                for match in unmatched_matches[:]:  # Use slice to avoid modification during iteration
                    if (match.get("home_team") == home_team and 
                        match.get("away_team") == away_team):
                        matched_date = match.get("date")
                        unmatched_matches.remove(match)
                        break
                
                if matched_date is None:
                    continue
                
                win_type = determine_win_type(score)
                cleaned_score = clean_score(score)
                winner = determine_winner(home_team, away_team, cleaned_score)
                leg = "Second Leg" if parsefrenchdate(matched_date) >= datetime(2024, 12, 4) else "First Leg"
                
                match_data = {
                    "leg": leg,
                    "journee": "",
                    "date": format_french_date(parsefrenchdate(matched_date)),
                    "hour": hour,
                    "match": f"{home_team} - {away_team}",
                    "win_type": win_type,
                    "score": cleaned_score,
                    "available": "yes" if cleaned_score == "No Score" else "no",
                    "winner": winner
                }
                matches_data.append(match_data)
            
            print(f"Total matches scraped for month: {len(matches_data)}")
            return matches_data
    
        except Exception as e:
            print(f"Error scraping month: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def write_matches_to_csv(matches_data, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['leg', 'journee', 'date', 'hour', 'match', 'win_type', 'score', 'available', 'winner']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
            writer.writeheader()
            for match in matches_data:
                writer.writerow(match)
        
    print("Starting the scraping process...")
    driver.get(web)
    print("Webpage loaded")
    accept_cookies(driver)
    
    months = ["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril"]
    
    all_matches_data = []
    for month in months:
        print(f"\n{'='*50}")
        print(f"Scraping data for: {month}")
        print(f"{'='*50}")
        select_month(driver, month)
        matches_data = scrape_month(driver)
        all_matches_data.extend(matches_data)
    
    print(f"\n{'='*50}")
    print("POST-PROCESSING ALL DATA")
    print(f"{'='*50}")
    
    # Step 1: Remove duplicates
    all_matches_data = deduplicate_matches(all_matches_data)
    
    # Step 2: Filter future matches only
    initial_count = len(all_matches_data)
    all_matches_data = [m for m in all_matches_data if is_future_match(m)]
    print(f"Future matches filter: {initial_count} -> {len(all_matches_data)} matches")
    
    if all_matches_data:
        write_matches_to_csv(all_matches_data, 'nhl_matches.csv')
        print(f"\n✅ Total UNIQUE FUTURE matches written to CSV: {len(all_matches_data)}")
        print("📁 File: nhl_matches.csv")
    else:
        print("❌ No future matches collected")
    
    print("\n🎉 Scraping process completed successfully!")

except Exception as e:
    print(f"\n❌ An error occurred: {str(e)}")
    import traceback
    print(traceback.format_exc())

finally:
    if driver:
        driver.quit()
        print("Browser closed.")
