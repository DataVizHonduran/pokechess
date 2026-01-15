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
                    if player and player["plw"] >= 20:
                        player_data.append(player)
                        print(f"  Found player: {name} (PLW: {player['plw']})")
                    elif player:
                        print(f"  Skipped player: {name} (PLW: {player['plw']} < 20)")

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
    - 20-49 PLW: Base form
    - 50-74 PLW: First evolution
    - 75-99 PLW: Final evolution
    - 100+ PLW: Legendary
    """

    # Use name hash to pick consistently
    name_hash = sum(ord(c) for c in name)

    # Evolution chains: (base, evolution1, evolution2 or None for 2-stage)
    EVOLUTION_CHAINS = [
        (1, 2, 3),       # Bulbasaur → Ivysaur → Venusaur
        (4, 5, 6),       # Charmander → Charmeleon → Charizard
        (7, 8, 9),       # Squirtle → Wartortle → Blastoise
        (10, 11, 12),    # Caterpie → Metapod → Butterfree
        (13, 14, 15),    # Weedle → Kakuna → Beedrill
        (16, 17, 18),    # Pidgey → Pidgeotto → Pidgeot
        (19, 20, 20),    # Rattata → Raticate → Raticate
        (21, 22, 22),    # Spearow → Fearow → Fearow
        (23, 24, 24),    # Ekans → Arbok → Arbok
        (25, 26, 26),    # Pikachu → Raichu → Raichu
        (27, 28, 28),    # Sandshrew → Sandslash → Sandslash
        (29, 30, 31),    # Nidoran♀ → Nidorina → Nidoqueen
        (32, 33, 34),    # Nidoran♂ → Nidorino → Nidoking
        (35, 36, 36),    # Clefairy → Clefable → Clefable
        (37, 38, 38),    # Vulpix → Ninetales → Ninetales
        (39, 40, 40),    # Jigglypuff → Wigglytuff → Wigglytuff
        (41, 42, 42),    # Zubat → Golbat → Golbat
        (43, 44, 45),    # Oddish → Gloom → Vileplume
        (46, 47, 47),    # Paras → Parasect → Parasect
        (48, 49, 49),    # Venonat → Venomoth → Venomoth
        (50, 51, 51),    # Diglett → Dugtrio → Dugtrio
        (52, 53, 53),    # Meowth → Persian → Persian
        (54, 55, 55),    # Psyduck → Golduck → Golduck
        (56, 57, 57),    # Mankey → Primeape → Primeape
        (58, 59, 59),    # Growlithe → Arcanine → Arcanine
        (60, 61, 62),    # Poliwag → Poliwhirl → Poliwrath
        (63, 64, 65),    # Abra → Kadabra → Alakazam
        (66, 67, 68),    # Machop → Machoke → Machamp
        (69, 70, 71),    # Bellsprout → Weepinbell → Victreebel
        (72, 73, 73),    # Tentacool → Tentacruel → Tentacruel
        (74, 75, 76),    # Geodude → Graveler → Golem
        (77, 78, 78),    # Ponyta → Rapidash → Rapidash
        (79, 80, 80),    # Slowpoke → Slowbro → Slowbro
        (81, 82, 82),    # Magnemite → Magneton → Magneton
        (84, 85, 85),    # Doduo → Dodrio → Dodrio
        (86, 87, 87),    # Seel → Dewgong → Dewgong
        (88, 89, 89),    # Grimer → Muk → Muk
        (90, 91, 91),    # Shellder → Cloyster → Cloyster
        (92, 93, 94),    # Gastly → Haunter → Gengar
        (96, 97, 97),    # Drowzee → Hypno → Hypno
        (98, 99, 99),    # Krabby → Kingler → Kingler
        (100, 101, 101), # Voltorb → Electrode → Electrode
        (104, 105, 105), # Cubone → Marowak → Marowak
        (109, 110, 110), # Koffing → Weezing → Weezing
        (111, 112, 112), # Rhyhorn → Rhydon → Rhydon
        (116, 117, 117), # Horsea → Seadra → Seadra
        (118, 119, 119), # Goldeen → Seaking → Seaking
        (120, 121, 121), # Staryu → Starmie → Starmie
        (129, 130, 130), # Magikarp → Gyarados → Gyarados
        (133, 134, 134), # Eevee → Vaporeon → Vaporeon
        (133, 135, 135), # Eevee → Jolteon → Jolteon
        (133, 136, 136), # Eevee → Flareon → Flareon
        (138, 139, 139), # Omanyte → Omastar → Omastar
        (140, 141, 141), # Kabuto → Kabutops → Kabutops
        (147, 148, 149), # Dratini → Dragonair → Dragonite
    ]

    # Legendaries for 100+ PLW
    LEGENDARIES = [
        150,  # Mewtwo
        151,  # Mew
        144,  # Articuno
        145,  # Zapdos
        146,  # Moltres
        143,  # Snorlax
        131,  # Lapras
        142,  # Aerodactyl
        149,  # Dragonite
        130,  # Gyarados
        6,    # Charizard
        9,    # Blastoise
        3,    # Venusaur
        65,   # Alakazam
        94,   # Gengar
        59,   # Arcanine
    ]

    # At 100+ PLW, get a legendary
    if plw >= 100:
        return LEGENDARIES[name_hash % len(LEGENDARIES)]

    # Otherwise, pick an evolution chain and get the right stage
    chain = EVOLUTION_CHAINS[name_hash % len(EVOLUTION_CHAINS)]

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
