"""
Mutation service - Genetic algorithm operations.
Extracted from team_generator.py and neural_network.py mutation logic.
"""
import random
from typing import List, Protocol
from ..entities.pokemon import Pokemon
from ..entities.team import Team


class PokemonFactory(Protocol):
    """Protocol for creating random Pokemon."""
    def create_random_pokemon(self, species: str) -> Pokemon:
        """Create a random Pokemon of given species."""
        ...
    
    def get_available_species(self) -> List[str]:
        """Get list of available Pokemon species."""
        ...


class MutationService:
    """
    Service for genetic algorithm mutations.
    Pure domain logic - strategies for mutating teams and agents.
    """
    
    def __init__(
        self, 
        pokemon_mutation_rate: int = 2,
        new_pokemon_rate: int = 16
    ):
        """
        Initialize mutation service.
        
        Args:
            pokemon_mutation_rate: Chance out of pokemon_in_team to mutate each Pokemon
            new_pokemon_rate: Chance out of new_pokemon to replace with completely new Pokemon
        """
        self.pokemon_mutation_rate = pokemon_mutation_rate
        self.new_pokemon_rate = new_pokemon_rate

    def should_mutate_pokemon(self) -> bool:
        """Determine if a Pokemon should be mutated."""
        return random.randint(1, 6) <= self.pokemon_mutation_rate

    def should_replace_with_new(self) -> bool:
        """Determine if Pokemon should be replaced with new species."""
        return random.randint(1, self.new_pokemon_rate) <= self.pokemon_mutation_rate

    def mutate_team(
        self, 
        team: Team, 
        pokemon_factory: PokemonFactory
    ) -> Team:
        """
        Mutate a team by changing some Pokemon or their moves.
        
        Args:
            team: Team to mutate
            pokemon_factory: Factory for creating new Pokemon
            
        Returns:
            New mutated team (original team is not modified)
        """
        mutated_team = team.copy()
        
        for i in range(len(mutated_team)):
            if self.should_mutate_pokemon():
                if self.should_replace_with_new():
                    # Replace with completely new Pokemon
                    species = random.choice(pokemon_factory.get_available_species())
                    new_pokemon = pokemon_factory.create_random_pokemon(species)
                    mutated_team.replace_pokemon(i, new_pokemon)
                else:
                    # Mutate moves of existing Pokemon
                    pokemon = mutated_team.get_pokemon(i)
                    mutated_pokemon = self.mutate_pokemon_moves(pokemon)
                    mutated_team.replace_pokemon(i, mutated_pokemon)
        
        return mutated_team

    def mutate_pokemon_moves(self, pokemon: Pokemon) -> Pokemon:
        """
        Mutate a Pokemon by changing 1-2 of its moves.
        
        Args:
            pokemon: Pokemon to mutate
            
        Returns:
            New Pokemon with mutated moves
        """
        mutated = pokemon.copy()
        
        if not mutated.possible_moves:
            return mutated
        
        # Decide how many moves to change (1 or 2)
        num_changes = random.randint(1, min(2, len(mutated.moves)))
        
        # Select which move slots to change
        if mutated.moves:
            slots_to_change = random.sample(range(len(mutated.moves)), num_changes)
        else:
            slots_to_change = []
        
        # Get new moves
        new_moves = mutated.moves.copy()
        available_moves = [m for m in mutated.possible_moves if m not in new_moves]
        
        if available_moves:
            for slot in slots_to_change:
                new_move = random.choice(available_moves)
                if slot < len(new_moves):
                    new_moves[slot] = new_move
                    available_moves.remove(new_move)
        
        mutated.set_moves(new_moves)
        return mutated

    def crossover_teams(self, team_a: Team, team_b: Team) -> Team:
        """
        Create offspring team by combining two parent teams.
        
        Args:
            team_a: First parent team
            team_b: Second parent team
            
        Returns:
            New team with Pokemon from both parents
        """
        offspring = Team(battle_format=team_a.battle_format)
        
        # Take 3 Pokemon from each parent
        size = min(len(team_a), len(team_b), 6)
        split_point = size // 2
        
        # First half from team_a
        for i in range(min(split_point, len(team_a))):
            offspring.add_pokemon(team_a[i].copy())
        
        # Second half from team_b
        start = size - split_point
        for i in range(start, min(size, len(team_b))):
            offspring.add_pokemon(team_b[i].copy())
        
        return offspring
