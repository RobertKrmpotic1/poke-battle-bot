"""
CSV Pokedex Repository implementation.
Extracted from game_setup.py MyPokedex class.
"""
import pandas as pd
import json
import random
from typing import Dict, List, Optional
from pathlib import Path
from domain.entities.pokemon import Pokemon
from domain.repositories.pokedex_repository import IPokedexRepository


class CSVPokedexRepository(IPokedexRepository):
    """
    Repository implementation using CSV files for Pokedex data.
    Adapter that wraps file I/O to implement domain repository interface.
    """
    
    def __init__(self, battle_format: str = "gen1ou", data_path: Optional[str] = None):
        """
        Initialize repository.
        
        Args:
            battle_format: Battle format (e.g., "gen1ou", "gen1randombattle")
            data_path: Root path to data folder (defaults to ./data)
        """
        self.battle_format = battle_format
        self.generation = int(battle_format[3]) if battle_format.startswith("gen") else 1
        
        if data_path is None:
            self.data_path = Path(__file__).parent.parent.parent / "data"
        else:
            self.data_path = Path(data_path)
        
        self.pokedex: Dict[str, Pokemon] = {}
        self.banned_pokemon: List[str] = []
        self.banned_moves: List[str] = []
        self.banned_items: List[str] = []
        
        self._load_pokedex()

    def _load_pokedex(self) -> None:
        """Load Pokedex data from CSV files."""
        # Load moves mapping
        learnset = self._load_moves()
        
        # Load Pokedex from poke_env GenData (we still use this for data loading)
        from poke_env.data import GenData
        gen_data = GenData(self.generation)
        
        pokedex_data = gen_data.load_pokedex(self.generation)
        
        # Filter out fan-made Pokemon and regional forms
        filtered_pokedex = {
            key: value 
            for key, value in pokedex_data.items() 
            if (value.get("num", 0) > 0) and ("forme" not in value)
        }
        
        # Parse into domain Pokemon entities
        for species, data in filtered_pokedex.items():
            types = data.get("types", [])
            abilities_dict = data.get("abilities", {})
            possible_abilities = list(abilities_dict.values())
            possible_moves = list(set(learnset.get(species, [])))
            
            pokemon = Pokemon(
                name=species,
                types=types,
                possible_abilities=possible_abilities,
                possible_moves=possible_moves
            )
            self.pokedex[species] = pokemon
        
        # Load banned lists
        self._load_banned_lists()
        
        # Apply exclusions
        self._apply_exclusions()

    def _load_moves(self) -> Dict[str, List[str]]:
        """Load move learnsets from CSV files."""
        try:
            moves_df = pd.read_csv(self.data_path / "moves" / "moves.csv")
            moves_df = moves_df.loc[moves_df["generation_id"] == self.generation]
            moves_df["identifier"] = moves_df["identifier"].str.replace("-", "")
            moves_dict = moves_df.loc[:, ["id", "identifier"]].set_index("id").to_dict()["identifier"]
            
            species_df = pd.read_csv(self.data_path / "moves" / "pokemon_species.csv")
            species_df = species_df.loc[species_df["generation_id"] == self.generation]
            species_df["identifier"] = species_df["identifier"].str.replace("-", "")
            species_dict = species_df.loc[:, ["id", "identifier"]].set_index("id").to_dict()["identifier"]
            
            learnset_df = pd.read_csv(self.data_path / "moves" / "pokemon_moves.csv")
            learnset_df = learnset_df.loc[
                (learnset_df["version_group_id"] == 1) & 
                (learnset_df["pokemon_move_method_id"] != 5)
            ]
            learnset_df = learnset_df.loc[:, ["pokemon_id", "move_id"]]
            learnset_df["move_id"] = learnset_df["move_id"].map(moves_dict)
            learnset_df["pokemon_id"] = learnset_df["pokemon_id"].map(species_dict)
            
            pokemon_moves_dict = learnset_df.groupby('pokemon_id')['move_id'].agg(list).to_dict()
            return pokemon_moves_dict
        except Exception as e:
            print(f"Warning: Could not load moves from CSV: {e}")
            return {}

    def _load_banned_lists(self) -> None:
        """Load banned Pokemon/moves/items for the format."""
        try:
            banned_file = self.data_path / "banned" / f"{self.battle_format}.json"
            if banned_file.exists():
                with open(banned_file) as f:
                    exclusions = json.load(f)
                    self.banned_moves = exclusions.get("moves", [])
                    self.banned_pokemon = exclusions.get("pokemon", [])
                    self.banned_items = exclusions.get("items", [])
        except Exception as e:
            print(f"Warning: Could not load banned lists: {e}")

    def _apply_exclusions(self) -> None:
        """Remove banned Pokemon and moves."""
        # Remove banned Pokemon
        self.pokedex = {
            key: value 
            for key, value in self.pokedex.items() 
            if key not in self.banned_pokemon
        }
        
        # Remove banned moves from each Pokemon
        for pokemon in self.pokedex.values():
            pokemon.possible_moves = [
                move for move in pokemon.possible_moves 
                if move not in self.banned_moves
            ]

    def get_pokemon(self, species: str) -> Optional[Pokemon]:
        """Get Pokemon by species name."""
        return self.pokedex.get(species)

    def get_all_pokemon(self, battle_format: str) -> Dict[str, Pokemon]:
        """Get all Pokemon available in a battle format."""
        # For now, return current pokedex (could load different format)
        return self.pokedex.copy()

    def get_available_species(self, battle_format: str) -> List[str]:
        """Get list of available Pokemon species."""
        return list(self.pokedex.keys())

    def get_banned_pokemon(self, battle_format: str) -> List[str]:
        """Get banned Pokemon for a format."""
        return self.banned_pokemon.copy()

    def get_banned_moves(self, battle_format: str) -> List[str]:
        """Get banned moves for a format."""
        return self.banned_moves.copy()

    def get_banned_items(self, battle_format: str) -> List[str]:
        """Get banned items for a format."""
        return self.banned_items.copy()

    def create_random_pokemon(self, species: str) -> Pokemon:
        """Create a Pokemon with random moves, ability, etc."""
        base_pokemon = self.pokedex.get(species)
        if not base_pokemon:
            raise ValueError(f"Species {species} not found in Pokedex")
        
        # Create a copy
        pokemon = base_pokemon.copy()
        
        # Randomize ability
        if pokemon.possible_abilities:
            pokemon.ability = random.choice(pokemon.possible_abilities)
        
        # Randomize moveset (4 moves)
        if pokemon.possible_moves:
            num_moves = min(4, len(pokemon.possible_moves))
            selected_moves = random.sample(pokemon.possible_moves, num_moves)
            pokemon.set_moves(selected_moves)
        
        return pokemon

    def get_generation(self, battle_format: str) -> int:
        """Get generation number from battle format."""
        if battle_format.startswith("gen"):
            return int(battle_format[3])
        return 1
