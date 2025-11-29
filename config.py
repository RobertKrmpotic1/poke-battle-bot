from dataclasses import dataclass

@dataclass
class Config:
    showdown_folder_path = r"C:/Users/Unknown/Downloads/Cheating is learning/pokemon-showdown"
    this_project_path = r"C:/Users/Unknown/Downloads/Cheating is learning/Pokebot"
    battle_format = "gen1randombattle"

class MutationRates:
    pokemon_in_team = 2
    new_pokemon = 16

class LeagueRules:
    n_players = 100
    n_discarded = 40
    top_n = 8
    starting_elo = 1000
    elo_k_value = 50