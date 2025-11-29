"""
PokeEnv Battle Adapter - bridges domain layer with poke_env infrastructure.
This adapter wraps poke_env's Player class to implement IBattleExecutor port.
"""
from typing import Optional, Dict, List
from poke_env.player import Player
from poke_env.battle import Battle, Move, Pokemon as PokeEnvPokemon
from poke_env.ps_client import ServerConfiguration, AccountConfiguration
from application.ports.battle_executor import IBattleExecutor, BattleResult
from domain.entities.agent import Agent
from domain.services.battle_strategy import IBattleStrategy
from domain.value_objects.battle_state import (
    BattleState, PokemonState, MoveInfo, Status, PokemonType, MoveCategory
)
from domain.value_objects.move_decision import MoveDecision, DecisionType
import asyncio


# Local server configuration
LOCAL_SERVER_CONFIG = ServerConfiguration(
    "ws://localhost:8000/showdown/websocket",
    "https://play.pokemonshowdown.com/action.php?"  # Won't be used for local server
)


class PokeEnvPlayer(Player):
    """
    Internal poke_env Player wrapper.
    Bridges poke_env callbacks with domain strategy.
    """
    
    def __init__(
        self,
        agent_id: str,
        strategy: IBattleStrategy,
        battle_format: str,
        server_url: str = "localhost:8000",
        username: str = None,
        **kwargs
    ):
        # Create account configuration with custom username
        account_config = AccountConfiguration(username or agent_id, None) if username else None
        
        # Use local server configuration without authentication
        super().__init__(
            account_configuration=account_config,
            battle_format=battle_format,
            server_configuration=LOCAL_SERVER_CONFIG,
            **kwargs
        )
        self.agent_id = agent_id
        self.strategy = strategy
        self._current_battle_states: Dict[str, BattleState] = {}

    def choose_move(self, battle: Battle):
        """
        Called by poke_env when a move decision is needed.
        Converts Battle to BattleState, calls domain strategy, converts back.
        """
        # Convert poke_env Battle to domain BattleState
        battle_state = self._convert_to_battle_state(battle)
        self._current_battle_states[battle.battle_tag] = battle_state
        
        # Get decision from domain strategy
        decision = self.strategy.choose_action(battle_state)
        
        # Convert domain MoveDecision to poke_env BattleOrder
        return self._convert_to_battle_order(decision, battle)

    def _convert_to_battle_state(self, battle: Battle) -> BattleState:
        """Convert poke_env Battle to domain BattleState."""
        # Convert active Pokemon
        my_active = self._convert_pokemon(battle.active_pokemon) if battle.active_pokemon else None
        opp_active = self._convert_pokemon(battle.opponent_active_pokemon) if battle.opponent_active_pokemon else None
        
        # Convert teams
        my_team = [self._convert_pokemon(p) for p in battle.team.values()]
        opp_team = [self._convert_pokemon(p) for p in battle.opponent_team.values()]
        
        return BattleState(
            my_active_pokemon=my_active,
            opponent_active_pokemon=opp_active,
            my_team=my_team,
            opponent_team=opp_team,
            turn=battle.turn,
            battle_tag=battle.battle_tag,
            finished=battle.finished,
            won=battle.won if battle.finished else None,
            can_switch=not battle.force_switch,
            force_switch=battle.force_switch
        )

    def _convert_pokemon(self, pokemon: PokeEnvPokemon) -> PokemonState:
        """Convert poke_env Pokemon to domain PokemonState."""
        # Convert status
        status = Status.NONE
        if pokemon.status:
            status_map = {
                "fnt": Status.FNT,
                "brn": Status.BRN,
                "frz": Status.FRZ,
                "par": Status.PAR,
                "psn": Status.PSN,
                "slp": Status.SLP,
                "tox": Status.TOX
            }
            status = status_map.get(str(pokemon.status).lower(), Status.NONE)
        
        # Convert types
        types = []
        if pokemon.type_1:
            try:
                types.append(PokemonType(pokemon.type_1.name))
            except:
                pass
        if pokemon.type_2:
            try:
                types.append(PokemonType(pokemon.type_2.name))
            except:
                pass
        
        # Convert moves
        available_moves = []
        for move in pokemon.moves.values():
            try:
                move_type = PokemonType(move.type.name) if move.type else PokemonType.NORMAL
                move_category = MoveCategory.PHYSICAL
                if move.category:
                    cat_map = {
                        "physical": MoveCategory.PHYSICAL,
                        "special": MoveCategory.SPECIAL,
                        "status": MoveCategory.STATUS
                    }
                    move_category = cat_map.get(str(move.category).lower(), MoveCategory.PHYSICAL)
                
                move_info = MoveInfo(
                    name=move.id,
                    type=move_type,
                    category=move_category,
                    power=move.base_power,
                    accuracy=int(move.accuracy * 100) if move.accuracy else 100,
                    pp=move.current_pp,
                    priority=move.priority
                )
                available_moves.append(move_info)
            except:
                pass
        
        return PokemonState(
            species=pokemon.species,
            current_hp=int(pokemon.current_hp or 0),
            max_hp=pokemon.max_hp,
            level=pokemon.level,
            status=status,
            types=types,
            active=pokemon.active,
            fainted=pokemon.fainted,
            boosts=pokemon.boosts.copy(),
            available_moves=available_moves
        )

    def _convert_to_battle_order(self, decision: MoveDecision, battle: Battle):
        """Convert domain MoveDecision to poke_env BattleOrder."""
        if decision.is_forfeit():
            return self.choose_random_move(battle)
        
        if decision.is_switch():
            # Get available switches
            available = [p for p in battle.team.values() if not p.fainted and not p.active]
            if available and decision.switch_target < len(available):
                return self.create_order(available[decision.switch_target])
            return self.choose_random_move(battle)
        
        if decision.is_move():
            # Get available moves
            available_moves = [m for m in battle.available_moves]
            if available_moves and decision.move_index < len(available_moves):
                move = available_moves[decision.move_index]
                return self.create_order(
                    move,
                    mega=decision.mega_evolve,
                    z_move=decision.z_move,
                    dynamax=decision.dynamax
                )
            return self.choose_random_move(battle)
        
        return self.choose_random_move(battle)


class PokeEnvBattleAdapter(IBattleExecutor):
    """
    Adapter that implements IBattleExecutor using poke_env.
    Manages PokeEnvPlayer instances and executes battles.
    """
    
    def __init__(self, server_url: str = "localhost:8000", username_prefix: str = "Bot_"):
        """
        Initialize battle adapter.
        
        Args:
            server_url: Pokemon Showdown server URL
            username_prefix: Prefix for player usernames to avoid conflicts
        """
        self.server_url = server_url
        self.username_prefix = username_prefix
        self._players: Dict[str, PokeEnvPlayer] = {}
        self._strategies: Dict[str, IBattleStrategy] = {}

    def register_strategy(self, agent_id: str, strategy: IBattleStrategy) -> None:
        """Register a battle strategy for an agent."""
        self._strategies[agent_id] = strategy

    async def execute_battle(
        self,
        agent_a: Agent,
        agent_b: Agent,
        save_replay: bool = False
    ) -> BattleResult:
        """
        Execute a battle between two agents.
        
        Args:
            agent_a: First agent
            agent_b: Second agent
            save_replay: Whether to save battle replay
            
        Returns:
            Battle result with winner and stats
        """
        # Get or create players with strategies
        strategy_a = self._strategies.get(agent_a.agent_id)
        strategy_b = self._strategies.get(agent_b.agent_id)
        
        if not strategy_a or not strategy_b:
            raise ValueError("Both agents must have registered strategies")
        
        player_a = PokeEnvPlayer(
            agent_id=agent_a.agent_id,
            strategy=strategy_a,
            battle_format=agent_a.battle_format,
            server_url=self.server_url,
            max_concurrent_battles=1,
            save_replays=save_replay,
            username=f"{self.username_prefix}{agent_a.agent_id}"
        )
        
        player_b = PokeEnvPlayer(
            agent_id=agent_b.agent_id,
            strategy=strategy_b,
            battle_format=agent_b.battle_format,
            server_url=self.server_url,
            max_concurrent_battles=1,
            save_replays=save_replay,
            username=f"{self.username_prefix}{agent_b.agent_id}"
        )
        
        # Execute battle
        await player_a.battle_against(player_b, n_battles=1)
        
        # Get battle result
        battle_tag = list(player_a.battles.keys())[0] if player_a.battles else None
        if not battle_tag:
            raise RuntimeError("No battle was executed")
        
        battle = player_a.battles[battle_tag]
        
        # Determine winner and calculate final HP
        # Note: We calculate HP before battle cleanup clears the team
        try:
            agent_a_hp = sum(p.current_hp_fraction for p in battle.team.values()) / 6 if battle.team else 0.0
            agent_b_hp = sum(p.current_hp_fraction for p in player_b.team.values()) / 6 if player_b.team else 0.0
        except (AttributeError, ZeroDivisionError):
            # Fallback if team data is unavailable
            agent_a_hp = 1.0 if battle.won else 0.0
            agent_b_hp = 1.0 if battle.lost else 0.0
        
        if battle.won:
            winner = "a"
        elif battle.lost:
            winner = "b"
        else:
            winner = "draw"
        
        result = BattleResult(
            agent_a_id=agent_a.agent_id,
            agent_b_id=agent_b.agent_id,
            winner=winner,
            turns=battle.turn,
            agent_a_final_hp=agent_a_hp,
            agent_b_final_hp=agent_b_hp,
            replay_data=None  # Could extract replay if needed
        )
        
        return result

    async def execute_battles(
        self,
        agent_pairs: List[tuple[Agent, Agent]],
        save_replays: bool = False
    ) -> List[BattleResult]:
        """Execute multiple battles concurrently."""
        tasks = [
            self.execute_battle(a, b, save_replays)
            for a, b in agent_pairs
        ]
        return await asyncio.gather(*tasks)

    def get_current_state(self, battle_id: str) -> Optional[BattleState]:
        """Get current state of an ongoing battle."""
        for player in self._players.values():
            if battle_id in player._current_battle_states:
                return player._current_battle_states[battle_id]
        return None
