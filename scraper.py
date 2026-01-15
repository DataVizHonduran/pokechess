from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time
import random

def scrape_ps11_stats():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    print("Launching headless browser...")
    driver = webdriver.Chrome(options=options)

    try:
        # Fetch the iframe source directly
        url = "https://icnadmin2.com/icnroster/ck_data_PS11.html"
        print(f"Fetching {url}...")
        driver.get(url)

        # Wait for content to load
        print("Waiting for content to load...")
        time.sleep(5)

        # Find tables
        tables = driver.find_elements(By.TAG_NAME, 'table')
        print(f"Found {len(tables)} tables")

        player_data = []

        for table in tables:
            rows = table.find_elements(By.TAG_NAME, 'tr')
            print(f"Table has {len(rows)} rows")

            for row in rows[1:]:  # Skip header
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 6:
                    name = cols[0].text.strip()
                    if not name or name.lower() == 'name':
                        continue

                    player = extract_player_data(cols, name)
                    if player:
                        player_data.append(player)
                        print(f"  Found player: {name}")

        if player_data:
            with open('public/players.json', 'w') as f:
                json.dump(player_data, f, indent=4)
            print(f"\nSuccess! {len(player_data)} players scraped to public/players.json")
        else:
            # Debug: show page content
            body = driver.find_element(By.TAG_NAME, 'body')
            print(f"\nPage text:\n{body.text[:1000]}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()

def extract_player_data(cols, name):
    def safe_int(text):
        try:
            # Remove commas and other formatting
            clean = ''.join(c for c in text if c.isdigit())
            return int(clean) if clean else 0
        except:
            return 0

    plw = safe_int(cols[5].text) if len(cols) > 5 else 0
    puzzles = safe_int(cols[3].text) if len(cols) > 3 else 0
    uscf = safe_int(cols[6].text) if len(cols) > 6 else 0
    group = cols[7].text.strip() if len(cols) > 7 else ""

    pokemon_id = (sum(ord(c) for c in name) % 150) + 1

    return {
        "id": name.lower().replace(" ", "-").replace(".", ""),
        "name": name,
        "puzzles": puzzles,
        "plw": plw,
        "uscf": uscf,
        "group": group,
        "pokemonId": pokemon_id,
        "element": "fire" if plw < 75 else "psychic",
        "delta": random.randint(0, 5)
    }

if __name__ == "__main__":
    scrape_ps11_stats()
