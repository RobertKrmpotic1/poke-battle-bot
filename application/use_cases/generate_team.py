"""
Generate Team Use Case - Creates random Pokemon teams.
Low-priority feature: Team generation with optional validation.
"""
import random
from typing import Optional
from domain.entities.team import Team
from domain.repositories.pokedex_repository import IPokedexRepository
from domain.services.mutation_service import MutationService
from application.ports.team_validator import ITeamValidator


class GenerateTeam:
    """
    Use case for generating random Pokemon teams.
    Uses pokedex repository for available Pokemon and mutation service for randomization.
    """

    def __init__(
        self,
        pokedex_repository: IPokedexRepository,
        mutation_service: MutationService,
        team_validator: Optional[ITeamValidator] = None
    ):
        """
        Initialize generate team use case.

        Args:
            pokedex_repository: Repository for Pokemon data
            mutation_service: Service for team mutations
            team_validator: Optional validator for team legality
        """
        self.pokedex_repository = pokedex_repository
        self.mutation_service = mutation_service
        self.team_validator = team_validator

    def execute(
        self,
        battle_format: str = "gen1randombattle",
        team_size: int = 6,
        validate_team: bool = False
    ) -> tuple[Team, Optional[list]]:
        """
        Generate a random team for the given battle format.

        Args:
            battle_format: Battle format (e.g., "gen1randombattle")
            team_size: Number of Pokemon in team (1-6)
            validate_team: Whether to validate the generated team

        Returns:
            Tuple of (generated_team, validation_errors)
            validation_errors is None if validate_team=False or no validator
        """
        # Get available species for the format
        available_species = self.pokedex_repository.get_available_species(battle_format)

        if not available_species:
            raise ValueError(f"No Pokemon available for format: {battle_format}")

        # Select random species
        selected_species = random.sample(available_species, min(team_size, len(available_species)))

        # Create team
        team = Team(battle_format=battle_format)

        for species in selected_species:
            pokemon = self.pokedex_repository.create_random_pokemon(species)
            team.add_pokemon(pokemon)

        # Validate if requested and validator available
        validation_errors = None
        if validate_team and self.team_validator:
            is_valid, errors = self.team_validator.validate_team(team)
            validation_errors = errors if not is_valid else []

        return team, validation_errors

    def execute_multiple(
        self,
        count: int,
        battle_format: str = "gen1randombattle",
        team_size: int = 6,
        validate_teams: bool = False
    ) -> list[tuple[Team, Optional[list]]]:
        """
        Generate multiple random teams.

        Args:
            count: Number of teams to generate
            battle_format: Battle format
            team_size: Pokemon per team
            validate_teams: Whether to validate generated teams

        Returns:
            List of (team, validation_errors) tuples
        """
        teams = []
        for _ in range(count):
            team, errors = self.execute(battle_format, team_size, validate_teams)
            teams.append((team, errors))
        return teams

    def mutate_existing_team(
        self,
        base_team: Team,
        validate_result: bool = False
    ) -> tuple[Team, Optional[list]]:
        """
        Create a mutated version of an existing team.

        Args:
            base_team: Team to mutate
            validate_result: Whether to validate the mutated team

        Returns:
            Tuple of (mutated_team, validation_errors)
        """
        # Create a PokemonFactory adapter for the mutation service
        class PokedexAdapter:
            def __init__(self, pokedex_repo: IPokedexRepository, battle_format: str):
                self.pokedex_repo = pokedex_repo
                self.battle_format = battle_format

            def create_random_pokemon(self, species: str) -> 'Pokemon':
                return self.pokedex_repo.create_random_pokemon(species)

            def get_available_species(self) -> list[str]:
                return self.pokedex_repo.get_available_species(self.battle_format)

        adapter = PokedexAdapter(self.pokedex_repository, base_team.battle_format)
        mutated_team = self.mutation_service.mutate_team(base_team, adapter)

        # Validate if requested
        validation_errors = None
        if validate_result and self.team_validator:
            is_valid, errors = self.team_validator.validate_team(mutated_team)
            validation_errors = errors if not is_valid else []

        return mutated_team, validation_errors