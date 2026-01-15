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

def get_pokemon_by_plw(plw, name):
    """Assign Pokemon based on PLW tier - higher PLW = more evolved/legendary Pokemon"""

    # Use name hash to pick consistently within each tier
    name_hash = sum(ord(c) for c in name)

    # Tier 5: Legendaries (300+ PLW)
    legendaries = [150, 151, 149, 144, 145, 146, 143, 130, 131, 142]  # Mewtwo, Mew, Dragonite, Articuno, Zapdos, Moltres, Snorlax, Gyarados, Lapras, Aerodactyl

    # Tier 4: Final evolutions (150-299 PLW)
    final_evos = [6, 9, 3, 65, 68, 76, 94, 103, 112, 134, 135, 136, 59, 38, 45]  # Charizard, Blastoise, Venusaur, Alakazam, Machamp, Golem, Gengar, Exeggutor, Rhydon, Vaporeon, Jolteon, Flareon, Arcanine, Ninetales, Vileplume

    # Tier 3: Stage 1 evolutions (75-149 PLW)
    stage1_evos = [5, 8, 2, 64, 67, 75, 93, 102, 111, 24, 28, 31, 34, 36, 40]  # Charmeleon, Wartortle, Ivysaur, Kadabra, Machoke, Graveler, Haunter, Exeggcute, Rhyhorn, Arbok, Sandslash, Nidoqueen, Nidoking, Clefable, Wigglytuff

    # Tier 2: Basic Pokemon (25-74 PLW)
    basic = [4, 7, 1, 25, 37, 58, 63, 66, 74, 92, 133, 147, 27, 29, 32, 35, 39]  # Charmander, Squirtle, Bulbasaur, Pikachu, Vulpix, Growlithe, Abra, Machop, Geodude, Gastly, Eevee, Dratini, Sandshrew, Nidoran, Clefairy, Jigglypuff

    # Tier 1: Starter/Cute Pokemon (0-24 PLW)
    starters = [10, 13, 16, 19, 21, 23, 41, 43, 46, 48, 50, 52, 54, 56, 60, 69, 72, 77, 79, 81, 84, 86, 88, 90, 96, 98, 100, 104, 108, 109, 114, 116, 118, 120, 127, 129, 137, 138, 140]  # Caterpie, Weedle, Pidgey, Rattata, Spearow, Ekans, Zubat, Oddish, Paras, Venonat, Diglett, Meowth, Psyduck, Mankey, Poliwag, Bellsprout, Tentacool, Ponyta, Slowpoke, Magnemite, Doduo, Seel, Grimer, Shellder, Drowzee, Krabby, Voltorb, Cubone, Lickitung, Koffing, Tangela, Horsea, Goldeen, Staryu, Pinsir, Magikarp, Porygon, Omanyte, Kabuto

    if plw >= 300:
        pokemon_list = legendaries
    elif plw >= 150:
        pokemon_list = final_evos
    elif plw >= 75:
        pokemon_list = stage1_evos
    elif plw >= 25:
        pokemon_list = basic
    else:
        pokemon_list = starters

    return pokemon_list[name_hash % len(pokemon_list)]


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

    # Determine element based on PLW tier
    if plw >= 300:
        element = "legendary"
    elif plw >= 150:
        element = "psychic"
    elif plw >= 75:
        element = "electric"
    else:
        element = "fire"

    return {
        "id": name.lower().replace(" ", "-").replace(".", ""),
        "name": name,
        "puzzles": puzzles,
        "plw": plw,
        "uscf": uscf,
        "group": group,
        "pokemonId": pokemon_id,
        "element": element,
        "delta": random.randint(0, 5)
    }

if __name__ == "__main__":
    scrape_ps11_stats()
