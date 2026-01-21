#!/usr/bin/env python3
"""
Fetch all Pokémon data from PokeAPI and generate pokemon-data.json
Run once to generate the data file, then scraper.py loads it.
"""

import json
import time
import requests

BASE_URL = "https://pokeapi.co/api/v2"

def fetch_with_retry(url, retries=3):
    """Fetch URL with retry logic for rate limiting."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                print(f"  Rate limited, waiting...")
                time.sleep(2)
            else:
                print(f"  Error {resp.status_code} for {url}")
                return None
        except Exception as e:
            print(f"  Request failed: {e}")
            time.sleep(1)
    return None

def get_all_pokemon_species():
    """Fetch all Pokémon species with names, IDs, and legendary/mythical status."""
    print("Fetching all Pokémon species...")

    pokemon_names = {}
    legendaries = []
    mythicals = []
    species_to_evolution_chain = {}

    # Get list of all species
    url = f"{BASE_URL}/pokemon-species?limit=2000"
    data = fetch_with_retry(url)

    if not data:
        print("Failed to fetch species list")
        return None, None, None, None

    total = len(data['results'])
    print(f"Found {total} Pokémon species")

    for i, species in enumerate(data['results']):
        species_name = species['name']
        species_url = species['url']
        pokemon_id = int(species_url.split('/')[-2])

        if i % 100 == 0:
            print(f"  Processing {i}/{total}...")

        # Fetch species details
        species_data = fetch_with_retry(species_url)
        if not species_data:
            continue

        # Get English name
        english_name = species_name.title()
        for name_entry in species_data.get('names', []):
            if name_entry['language']['name'] == 'en':
                english_name = name_entry['name']
                break

        pokemon_names[pokemon_id] = english_name

        # Check legendary/mythical status
        if species_data.get('is_legendary'):
            legendaries.append(pokemon_id)
        if species_data.get('is_mythical'):
            mythicals.append(pokemon_id)

        # Track evolution chain URL
        evo_chain_url = species_data.get('evolution_chain', {}).get('url')
        if evo_chain_url:
            chain_id = int(evo_chain_url.split('/')[-2])
            species_to_evolution_chain[pokemon_id] = chain_id

        # Small delay to avoid rate limiting
        time.sleep(0.05)

    return pokemon_names, legendaries, mythicals, species_to_evolution_chain

def get_species_id_by_name(name, pokemon_names):
    """Find species ID by name."""
    name_lower = name.lower()
    for pid, pname in pokemon_names.items():
        if pname.lower() == name_lower:
            return pid
    return None

def parse_evolution_chain(chain, pokemon_names):
    """
    Parse an evolution chain recursively.
    Returns list of evolution paths like (base, evo1, evo2).
    """
    chains = []

    def get_chain_paths(node, current_path):
        species_name = node['species']['name']
        species_id = get_species_id_by_name(species_name, pokemon_names)

        if species_id is None:
            # Try to get ID from URL
            species_url = node['species']['url']
            species_id = int(species_url.split('/')[-2])

        new_path = current_path + [species_id]

        evolves_to = node.get('evolves_to', [])

        if not evolves_to:
            # End of chain - pad to 3 elements
            while len(new_path) < 3:
                new_path.append(new_path[-1])  # Repeat final form
            chains.append(tuple(new_path[:3]))
        else:
            for evolution in evolves_to:
                get_chain_paths(evolution, new_path)

    get_chain_paths(chain, [])
    return chains

def get_all_evolution_chains(pokemon_names):
    """Fetch all evolution chains."""
    print("\nFetching evolution chains...")

    all_chains = []
    seen_chain_ids = set()

    # Get total number of evolution chains
    url = f"{BASE_URL}/evolution-chain?limit=1"
    data = fetch_with_retry(url)
    total_chains = data['count'] if data else 500

    print(f"Found {total_chains} evolution chains")

    for chain_id in range(1, total_chains + 50):  # Some IDs might be skipped
        if chain_id % 100 == 0:
            print(f"  Processing chain {chain_id}...")

        url = f"{BASE_URL}/evolution-chain/{chain_id}"
        data = fetch_with_retry(url)

        if not data:
            continue

        chain_data = data.get('chain')
        if chain_data:
            paths = parse_evolution_chain(chain_data, pokemon_names)
            for path in paths:
                if path not in all_chains:
                    all_chains.append(path)

        time.sleep(0.05)

    return all_chains

def main():
    print("=" * 50)
    print("Pokémon Data Generator")
    print("=" * 50)

    # Step 1: Get all species
    pokemon_names, legendaries, mythicals, species_chains = get_all_pokemon_species()

    if not pokemon_names:
        print("Failed to fetch Pokémon data")
        return

    print(f"\nCollected:")
    print(f"  - {len(pokemon_names)} Pokémon")
    print(f"  - {len(legendaries)} legendaries")
    print(f"  - {len(mythicals)} mythicals")

    # Step 2: Get evolution chains
    evolution_chains = get_all_evolution_chains(pokemon_names)
    print(f"  - {len(evolution_chains)} evolution chains")

    # Combine legendaries and mythicals for the "elite" tier
    elite_pokemon = sorted(set(legendaries + mythicals))

    # Build output
    output = {
        "pokemon_names": {str(k): v for k, v in sorted(pokemon_names.items())},
        "evolution_chains": evolution_chains,
        "legendaries": sorted(legendaries),
        "mythicals": sorted(mythicals),
        "elite": elite_pokemon,  # Combined for 100+ PLW tier
        "metadata": {
            "total_pokemon": len(pokemon_names),
            "total_chains": len(evolution_chains),
            "total_legendaries": len(legendaries),
            "total_mythicals": len(mythicals),
            "generated_by": "generate-pokemon-data.py"
        }
    }

    # Save to file
    output_path = "pokemon-data.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to {output_path}")
    print("Done!")

if __name__ == "__main__":
    main()
