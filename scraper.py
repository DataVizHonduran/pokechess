from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time
import random
import os

# Try to use webdriver-manager if available (for CI), otherwise use system Chrome
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False

# Load Pokemon data from generated JSON file (all 1025 Pokemon)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POKEMON_DATA_PATH = os.path.join(SCRIPT_DIR, "pokemon-data.json")
PLAYER_ASSIGNMENTS_PATH = os.path.join(SCRIPT_DIR, "player-pokemon.json")

with open(POKEMON_DATA_PATH, 'r') as f:
    POKEMON_DATA = json.load(f)

# Convert string keys back to int for POKEMON_NAMES
POKEMON_NAMES = {int(k): v for k, v in POKEMON_DATA["pokemon_names"].items()}
ELITE_POKEMON = POKEMON_DATA["elite"]  # Legendaries + Mythicals
ELITE_SET = set(ELITE_POKEMON)  # For fast lookup

# Filter out chains that contain any legendary/mythical Pokemon
# These should only be available to players with PLW >= 100
EVOLUTION_CHAINS = [
    tuple(chain) for chain in POKEMON_DATA["evolution_chains"]
    if not any(pid in ELITE_SET for pid in chain)
]

# Persistent player assignments (loaded from player-pokemon.json)
# Structure: {"player_name": {"chain_index": int, "elite_index": int, "last_plw": int}}
PLAYER_ASSIGNMENTS = {}


def load_player_assignments():
    """Load player Pokemon assignments from JSON file."""
    global PLAYER_ASSIGNMENTS
    if os.path.exists(PLAYER_ASSIGNMENTS_PATH):
        with open(PLAYER_ASSIGNMENTS_PATH, 'r') as f:
            PLAYER_ASSIGNMENTS = json.load(f)
        print(f"Loaded {len(PLAYER_ASSIGNMENTS)} player assignments from player-pokemon.json")
    else:
        PLAYER_ASSIGNMENTS = {}
        print("No existing player-pokemon.json found, starting fresh")


def save_player_assignments():
    """Save player Pokemon assignments to JSON file."""
    with open(PLAYER_ASSIGNMENTS_PATH, 'w') as f:
        json.dump(PLAYER_ASSIGNMENTS, f, indent=2)
    print(f"Saved {len(PLAYER_ASSIGNMENTS)} player assignments to player-pokemon.json")


def detect_new_week(all_players_plw):
    """
    Returns True if any player who was previously on the board (PLW >= 20)
    now has PLW of 0. This indicates the weekly reset has occurred.

    all_players_plw: dict of {name: plw} for ALL players (including those with 0)
    """
    for name, data in PLAYER_ASSIGNMENTS.items():
        old_plw = data.get("last_plw", 0)
        new_plw = all_players_plw.get(name, -1)  # -1 if player not found
        # Player was on the board (>= 20) AND now has zero = new week
        if old_plw >= 20 and new_plw == 0:
            print(f"New week detected: {name} went from PLW {old_plw} to {new_plw}")
            return True
    return False

def scrape_ps11_stats():
    global PLAYER_ASSIGNMENTS

    # Load existing player assignments
    load_player_assignments()

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    print("Launching headless browser...")
    if USE_WEBDRIVER_MANAGER:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
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

        # FIRST PASS: Collect ALL players with their PLW values (including PLW = 0)
        all_players_plw = {}
        raw_player_rows = []  # Store (cols, name) for second pass

        for table in tables:
            rows = table.find_elements(By.TAG_NAME, 'tr')
            print(f"Table has {len(rows)} rows")

            for row in rows[1:]:  # Skip header
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 6:
                    name = cols[0].text.strip()
                    if not name or name.lower() == 'name':
                        continue

                    # Extract PLW for weekly reset detection
                    try:
                        plw_text = cols[5].text if len(cols) > 5 else "0"
                        plw = int(''.join(c for c in plw_text if c.isdigit()) or '0')
                    except:
                        plw = 0

                    player_key = name.lower().strip()
                    all_players_plw[player_key] = plw
                    raw_player_rows.append((cols, name))

        print(f"First pass: found {len(all_players_plw)} total players")

        # Check for weekly reset
        if detect_new_week(all_players_plw):
            print("Weekly reset detected! Clearing all player assignments.")
            PLAYER_ASSIGNMENTS = {}

        # SECOND PASS: Build player data (filter to PLW >= 20, assign Pokemon)
        player_data = []

        for cols, name in raw_player_rows:
            player = extract_player_data(cols, name)
            if player and player["plw"] >= 20:
                player_data.append(player)
                print(f"  Found player: {name} (PLW: {player['plw']})")

        # Save updated assignments
        save_player_assignments()

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

def get_pokemon_by_plw(plw, name):
    """
    Assign Pokemon based on PLW with real evolution chains.
    Uses all 1025 Pokemon from pokemon-data.json.

    Assignments persist within a week (stored in player-pokemon.json).
    Weekly reset is detected when a previously tracked player has PLW = 0.
    - 20-49 PLW: Base form
    - 50-74 PLW: First evolution
    - 75-99 PLW: Final evolution
    - 100+ PLW: Legendary/Mythical
    """
    # Normalize name for consistent lookup
    player_key = name.lower().strip()

    # Assign random chain if not yet assigned, or use existing assignment
    if player_key not in PLAYER_ASSIGNMENTS:
        PLAYER_ASSIGNMENTS[player_key] = {
            "chain_index": random.randint(0, len(EVOLUTION_CHAINS) - 1),
            "elite_index": random.randint(0, len(ELITE_POKEMON) - 1),
            "last_plw": plw
        }
    else:
        # Update last_plw for existing player
        PLAYER_ASSIGNMENTS[player_key]["last_plw"] = plw

    assignment = PLAYER_ASSIGNMENTS[player_key]

    # At 100+ PLW, get a legendary/mythical
    if plw >= 100:
        return ELITE_POKEMON[assignment["elite_index"]]

    # Otherwise, use assigned chain and get the right stage based on PLW
    chain = EVOLUTION_CHAINS[assignment["chain_index"]]

    if plw >= 75:
        return chain[2]  # Final evolution
    elif plw >= 50:
        return chain[1]  # First evolution
    else:
        return chain[0]  # Base form


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

    pokemon_id = get_pokemon_by_plw(plw, name)

    # Determine tier based on PLW
    if plw >= 100:
        tier = "legendary"
    elif plw >= 75:
        tier = "final"
    elif plw >= 50:
        tier = "evolved"
    else:
        tier = "basic"

    return {
        "id": name.lower().replace(" ", "-").replace(".", ""),
        "name": name,
        "puzzles": puzzles,
        "plw": plw,
        "uscf": uscf,
        "group": group,
        "pokemonId": pokemon_id,
        "pokemonName": POKEMON_NAMES.get(pokemon_id, "Unknown"),
        "tier": tier,
        "delta": random.randint(0, 5)
    }

if __name__ == "__main__":
    scrape_ps11_stats()
