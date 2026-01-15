from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import time
import random

# Pokemon ID to Name mapping (Gen 1)
POKEMON_NAMES = {
    1: "Bulbasaur", 2: "Ivysaur", 3: "Venusaur", 4: "Charmander", 5: "Charmeleon",
    6: "Charizard", 7: "Squirtle", 8: "Wartortle", 9: "Blastoise", 10: "Caterpie",
    11: "Metapod", 12: "Butterfree", 13: "Weedle", 14: "Kakuna", 15: "Beedrill",
    16: "Pidgey", 17: "Pidgeotto", 18: "Pidgeot", 19: "Rattata", 20: "Raticate",
    21: "Spearow", 22: "Fearow", 23: "Ekans", 24: "Arbok", 25: "Pikachu",
    26: "Raichu", 27: "Sandshrew", 28: "Sandslash", 29: "Nidoran F", 30: "Nidorina",
    31: "Nidoqueen", 32: "Nidoran M", 33: "Nidorino", 34: "Nidoking", 35: "Clefairy",
    36: "Clefable", 37: "Vulpix", 38: "Ninetales", 39: "Jigglypuff", 40: "Wigglytuff",
    41: "Zubat", 42: "Golbat", 43: "Oddish", 44: "Gloom", 45: "Vileplume",
    46: "Paras", 47: "Parasect", 48: "Venonat", 49: "Venomoth", 50: "Diglett",
    51: "Dugtrio", 52: "Meowth", 53: "Persian", 54: "Psyduck", 55: "Golduck",
    56: "Mankey", 57: "Primeape", 58: "Growlithe", 59: "Arcanine", 60: "Poliwag",
    61: "Poliwhirl", 62: "Poliwrath", 63: "Abra", 64: "Kadabra", 65: "Alakazam",
    66: "Machop", 67: "Machoke", 68: "Machamp", 69: "Bellsprout", 70: "Weepinbell",
    71: "Victreebel", 72: "Tentacool", 73: "Tentacruel", 74: "Geodude", 75: "Graveler",
    76: "Golem", 77: "Ponyta", 78: "Rapidash", 79: "Slowpoke", 80: "Slowbro",
    81: "Magnemite", 82: "Magneton", 83: "Farfetch'd", 84: "Doduo", 85: "Dodrio",
    86: "Seel", 87: "Dewgong", 88: "Grimer", 89: "Muk", 90: "Shellder",
    91: "Cloyster", 92: "Gastly", 93: "Haunter", 94: "Gengar", 95: "Onix",
    96: "Drowzee", 97: "Hypno", 98: "Krabby", 99: "Kingler", 100: "Voltorb",
    101: "Electrode", 102: "Exeggcute", 103: "Exeggutor", 104: "Cubone", 105: "Marowak",
    106: "Hitmonlee", 107: "Hitmonchan", 108: "Lickitung", 109: "Koffing", 110: "Weezing",
    111: "Rhyhorn", 112: "Rhydon", 113: "Chansey", 114: "Tangela", 115: "Kangaskhan",
    116: "Horsea", 117: "Seadra", 118: "Goldeen", 119: "Seaking", 120: "Staryu",
    121: "Starmie", 122: "Mr. Mime", 123: "Scyther", 124: "Jynx", 125: "Electabuzz",
    126: "Magmar", 127: "Pinsir", 128: "Tauros", 129: "Magikarp", 130: "Gyarados",
    131: "Lapras", 132: "Ditto", 133: "Eevee", 134: "Vaporeon", 135: "Jolteon",
    136: "Flareon", 137: "Porygon", 138: "Omanyte", 139: "Omastar", 140: "Kabuto",
    141: "Kabutops", 142: "Aerodactyl", 143: "Snorlax", 144: "Articuno", 145: "Zapdos",
    146: "Moltres", 147: "Dratini", 148: "Dragonair", 149: "Dragonite", 150: "Mewtwo",
    151: "Mew"
}

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

    # Tier 5: Legendaries & Pseudo-Legendaries (300+ PLW) - 20 Pokemon
    legendaries = [
        150, 151, 149,  # Mewtwo, Mew, Dragonite
        144, 145, 146,  # Articuno, Zapdos, Moltres
        143, 130, 131, 142,  # Snorlax, Gyarados, Lapras, Aerodactyl
        148, 139, 141,  # Dragonair, Omastar, Kabutops
        6, 9, 3,  # Charizard, Blastoise, Venusaur (starters are legendary tier too)
        59, 38, 94, 65  # Arcanine, Ninetales, Gengar, Alakazam
    ]

    # Tier 4: Final evolutions (150-299 PLW) - 35 Pokemon
    final_evos = [
        68, 76, 103, 112,  # Machamp, Golem, Exeggutor, Rhydon
        134, 135, 136,  # Vaporeon, Jolteon, Flareon
        45, 71, 62, 73,  # Vileplume, Victreebel, Poliwrath, Tentacruel
        78, 80, 82, 83,  # Rapidash, Slowbro, Magneton, Farfetch'd
        85, 87, 89, 91,  # Dodrio, Dewgong, Muk, Cloyster
        97, 99, 101, 105,  # Hypno, Kingler, Electrode, Marowak
        106, 107, 110, 113,  # Hitmonlee, Hitmonchan, Weezing, Chansey
        115, 117, 119, 121,  # Kangaskhan, Seadra, Seaking, Starmie
        122, 123, 124, 125, 126, 128  # Mr. Mime, Scyther, Jynx, Electabuzz, Magmar, Tauros
    ]

    # Tier 3: Stage 1 evolutions (75-149 PLW) - 35 Pokemon
    stage1_evos = [
        5, 8, 2,  # Charmeleon, Wartortle, Ivysaur
        64, 67, 75, 93,  # Kadabra, Machoke, Graveler, Haunter
        24, 28, 31, 34,  # Arbok, Sandslash, Nidoqueen, Nidoking
        36, 40, 44, 47,  # Clefable, Wigglytuff, Gloom, Parasect
        49, 51, 53, 55,  # Venomoth, Dugtrio, Persian, Golduck
        57, 61, 70, 102,  # Primeape, Poliwhirl, Weepinbell, Exeggcute
        111, 30, 33, 20,  # Rhyhorn, Nidorina, Nidorino, Raticate
        22, 17, 42, 15,  # Fearow, Pidgeotto, Golbat, Beedrill
        12, 26  # Butterfree, Raichu
    ]

    # Tier 2: Basic Pokemon (25-74 PLW) - 35 Pokemon
    basic = [
        4, 7, 1, 25,  # Charmander, Squirtle, Bulbasaur, Pikachu
        37, 58, 63, 66, 74,  # Vulpix, Growlithe, Abra, Machop, Geodude
        92, 133, 147,  # Gastly, Eevee, Dratini
        27, 29, 32, 35, 39,  # Sandshrew, Nidoran F, Nidoran M, Clefairy, Jigglypuff
        43, 60, 69, 79,  # Oddish, Poliwag, Bellsprout, Slowpoke
        77, 81, 95, 104,  # Ponyta, Magnemite, Onix, Cubone
        111, 116, 120, 127,  # Rhyhorn, Horsea, Staryu, Pinsir
        23, 19, 16, 21,  # Ekans, Rattata, Pidgey, Spearow
        56, 54, 52  # Mankey, Psyduck, Meowth
    ]

    # Tier 1: Starter/Common Pokemon (0-24 PLW) - 30 Pokemon
    starters = [
        10, 11, 13, 14,  # Caterpie, Metapod, Weedle, Kakuna
        41, 46, 48, 50,  # Zubat, Paras, Venonat, Diglett
        72, 84, 86, 88, 90,  # Tentacool, Doduo, Seel, Grimer, Shellder
        96, 98, 100,  # Drowzee, Krabby, Voltorb
        108, 109, 114,  # Lickitung, Koffing, Tangela
        118, 129,  # Goldeen, Magikarp
        137, 138, 140,  # Porygon, Omanyte, Kabuto
        132,  # Ditto
        83,  # Farfetch'd
        106, 107  # Hitmonlee, Hitmonchan (rare but low evolution)
    ]

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
        "pokemonName": POKEMON_NAMES.get(pokemon_id, "Unknown"),
        "element": element,
        "delta": random.randint(0, 5)
    }

if __name__ == "__main__":
    scrape_ps11_stats()
