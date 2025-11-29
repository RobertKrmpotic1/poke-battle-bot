"""
Pure Agent entity - no external dependencies.
Extracted from driver.py with Player inheritance removed.
"""
from typing import Optional
from dataclasses import dataclass, field
from .team import Team


@dataclass
class Agent:
    """
    Represents a competitive agent (bot/driver) that battles with a team.
    Pure domain entity with no infrastructure dependencies.
    """
    agent_id: str
    team: Optional[Team] = None
    elo: int = 1000
    wins: int = 0
    losses: int = 0
    draws: int = 0
    battles: int = 0
    battle_format: str = "gen1randombattle"
    generation: int = 0  # For tracking evolutionary generation

    def __post_init__(self):
        """Validate agent state."""
        if not self.agent_id:
            raise ValueError("Agent must have an ID")
        if self.elo < 0:
            raise ValueError("ELO rating cannot be negative")

    @property
    def win_rate(self) -> float:
        """Calculate win rate."""
        if self.battles == 0:
            return 0.0
        return self.wins / self.battles

    @property
    def total_games(self) -> int:
        """Total number of games played."""
        return self.wins + self.losses + self.draws

    def record_win(self) -> None:
        """Record a win for this agent."""
        self.wins += 1
        self.battles += 1

    def record_loss(self) -> None:
        """Record a loss for this agent."""
        self.losses += 1
        self.battles += 1

    def record_draw(self) -> None:
        """Record a draw for this agent."""
        self.draws += 1
        self.battles += 1

    def reset_battle_stats(self) -> None:
        """Reset battle statistics (for new generations)."""
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.battles = 0

    def update_elo(self, new_elo: int) -> None:
        """
        Update the agent's ELO rating.
        
        Args:
            new_elo: New ELO rating
            
        Raises:
            ValueError: If new_elo is negative
        """
        if new_elo < 0:
            raise ValueError(f"ELO rating cannot be negative, got {new_elo}")
        self.elo = new_elo

    def set_team(self, team: Team) -> None:
        """
        Set the agent's team.
        
        Args:
            team: Team to assign
            
        Raises:
            ValueError: If team is invalid or wrong format
        """
        if not team.is_valid():
            raise ValueError("Cannot assign invalid team to agent")
        if team.battle_format != self.battle_format:
            raise ValueError(
                f"Team format {team.battle_format} does not match "
                f"agent format {self.battle_format}"
            )
        self.team = team

    def has_team(self) -> bool:
        """Check if agent has a team assigned."""
        return self.team is not None

    def copy(self, new_id: str) -> 'Agent':
        """
        Create a copy of this agent with a new ID (for mutation/offspring).
        
        Args:
            new_id: ID for the new agent
            
        Returns:
            New Agent instance
        """
        return Agent(
            agent_id=new_id,
            team=self.team.copy() if self.team else None,
            elo=self.elo,
            wins=0,  # Reset stats for new agent
            losses=0,
            draws=0,
            battles=0,
            battle_format=self.battle_format,
            generation=self.generation + 1
        )

    def __repr__(self) -> str:
        return (
            f"Agent(id={self.agent_id}, elo={self.elo}, "
            f"record={self.wins}-{self.losses}-{self.draws})"
        )

    def __str__(self) -> str:
        return (
            f"Agent {self.agent_id}: "
            f"ELO {self.elo}, "
            f"W/L/D: {self.wins}/{self.losses}/{self.draws}, "
            f"Win Rate: {self.win_rate:.1%}"
        )
