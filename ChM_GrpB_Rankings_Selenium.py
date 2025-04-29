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
        "Autriche": "Austria",
        "Finlande": "Finland",
        "Suède": "Sweden",
        "Slovaquie": "Slovakia",
        "Suisse": "Switzerland",
        "Tchéquie": "Czechia",
        "Danemark": "Denmark",
        "USA": "USA",
        "Slovénie": "Slovenia",
        "Canada": "Canada",
        "France": "France",
        "Lettonie": "Latvia",
        "Norvège": "Norway",
        "Kazakhstan": "Kazakhstan",
        "Allemagne": "Germany",
        "Hongrie": "Hungary",
        # Add more if needed
    }
    return replacements.get(team_name, team_name)

web = "https://www.rts.ch/sport/resultats/#/results/hockey/wm/GroupPhase-1-0/Group-2-1/rankings/700333"
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


# path = r'C:\WebDrivers\chromedriver-win64\chromedriver.exe'
# service = Service(executable_path=path)
# chrome_options = Options()
# chrome_options.add_experimental_option("detach", True)
# driver = webdriver.Chrome(service=service, options=chrome_options)

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


    def get_rankings():
        try:
            # Wait for the rankings table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.stxt-ranking-table__table"))
            )

            # Get all td elements within the rankings table
            td_elements = driver.find_elements(By.CSS_SELECTOR, "td")

            # Parse the data
            rankings_data = []
            current_row = []
            for td in td_elements:
                text = td.text.strip()
                if text:  # Only add non-empty text
                    current_row.append(text)
                if len(current_row) == 9:  # Each row should have exactly 9 fields
                    rank, team, games_played, wins, overtime_wins, overtime_losses, losses, goals, points = current_row
                    team = replace_team_names(team)

                    # Split goals into goals_for and goals_against
                    goals_for, goals_against = map(int, goals.split('-'))

                    # Append parsed data to rankings_data
                    rankings_data.append([
                        rank.strip('.'), team, points, games_played, wins,
                        overtime_wins, overtime_losses, losses,
                        goals_for, goals_against
                    ])
                    current_row = []

            # Write to CSV
            with open('ChM_GrpB_rankings.csv', 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['rank', 'team', 'points', 'games_played', 'wins',
                                 'overtime_wins', 'overtime_losses', 'losses',
                                 'goals_for', 'goals_against'])
                writer.writerows(rankings_data)

            print("Rankings data has been written to ChM_GrpB_rankings.csv")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            import traceback
            print(traceback.format_exc())


    driver.get(web)
    accept_cookies(driver)
    accept_cookies(driver)
    get_rankings()

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    if driver:
        driver.quit()

