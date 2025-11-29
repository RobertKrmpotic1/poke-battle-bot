"""
Pandas League Repository - League standings and match history using pandas.
Low-priority feature: Analytics and persistence for league data.
"""
import os
import json
from typing import List, Dict, Optional
import pandas as pd
from domain.repositories.league_repository import ILeagueRepository, LeagueStanding


class PandasLeagueRepository(ILeagueRepository):
    """
    League repository implementation using pandas DataFrames.
    Stores standings and match history in CSV files for analysis.
    """

    def __init__(self, data_dir: str = "data/league"):
        """
        Initialize pandas league repository.

        Args:
            data_dir: Directory to store league data files
        """
        self.data_dir = data_dir
        self.standings_file = os.path.join(data_dir, "standings.csv")
        self.matches_file = os.path.join(data_dir, "matches.csv")
        self.config_file = os.path.join(data_dir, "config.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize empty DataFrames if files don't exist
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensure required data files exist with proper structure."""
        if not os.path.exists(self.standings_file):
            df = pd.DataFrame(columns=[
                'round_number', 'agent_id', 'rank', 'elo', 'wins', 'losses', 'draws', 'battles'
            ])
            df.to_csv(self.standings_file, index=False)

        if not os.path.exists(self.matches_file):
            df = pd.DataFrame(columns=[
                'round_number', 'agent_a_id', 'agent_b_id', 'winner', 'turns', 'timestamp'
            ])
            df.to_csv(self.matches_file, index=False)

        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({'current_round': 0}, f)

    def save_standings(
        self,
        standings: List[LeagueStanding],
        round_number: int
    ) -> None:
        """
        Save league standings for a round.

        Args:
            standings: List of standings
            round_number: Current round number
        """
        # Convert standings to DataFrame
        data = []
        for standing in standings:
            data.append({
                'round_number': round_number,
                'agent_id': standing.agent_id,
                'rank': standing.rank,
                'elo': standing.elo,
                'wins': standing.wins,
                'losses': standing.losses,
                'draws': standing.draws,
                'battles': standing.battles
            })

        new_df = pd.DataFrame(data)

        # Load existing standings and append
        existing_df = pd.read_csv(self.standings_file)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Save back to file
        combined_df.to_csv(self.standings_file, index=False)

    def get_standings(self, round_number: int) -> List[LeagueStanding]:
        """
        Get standings for a specific round.

        Args:
            round_number: Round number

        Returns:
            List of standings
        """
        df = pd.read_csv(self.standings_file)
        round_data = df[df['round_number'] == round_number]

        standings = []
        for _, row in round_data.iterrows():
            standings.append(LeagueStanding(
                agent_id=row['agent_id'],
                rank=int(row['rank']),
                elo=int(row['elo']),
                wins=int(row['wins']),
                losses=int(row['losses']),
                draws=int(row['draws']),
                battles=int(row['battles'])
            ))

        return standings

    def get_latest_standings(self) -> List[LeagueStanding]:
        """
        Get the most recent standings.

        Returns:
            List of standings
        """
        df = pd.read_csv(self.standings_file)
        if df.empty:
            return []

        latest_round = df['round_number'].max()
        return self.get_standings(latest_round)

    def save_league_config(self, config: Dict) -> None:
        """
        Save league configuration.

        Args:
            config: Configuration dictionary
        """
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def get_league_config(self) -> Optional[Dict]:
        """
        Get league configuration.

        Returns:
            Configuration dictionary or None
        """
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def get_current_round(self) -> int:
        """
        Get current round number.

        Returns:
            Current round number
        """
        config = self.get_league_config()
        return config.get('current_round', 0) if config else 0

    def increment_round(self) -> int:
        """
        Increment and return new round number.

        Returns:
            New round number
        """
        current = self.get_current_round()
        new_round = current + 1

        config = self.get_league_config() or {}
        config['current_round'] = new_round
        self.save_league_config(config)

        return new_round

    def save_match_result(
        self,
        round_number: int,
        agent_a_id: str,
        agent_b_id: str,
        winner: str,
        turns: int
    ) -> None:
        """
        Save individual match result.

        Args:
            round_number: Round number
            agent_a_id: First agent ID
            agent_b_id: Second agent ID
            winner: "a", "b", or "draw"
            turns: Number of turns
        """
        import datetime

        # Load existing matches
        df = pd.read_csv(self.matches_file)

        # Add new match
        new_match = pd.DataFrame([{
            'round_number': round_number,
            'agent_a_id': agent_a_id,
            'agent_b_id': agent_b_id,
            'winner': winner,
            'turns': turns,
            'timestamp': datetime.datetime.now().isoformat()
        }])

        # Combine and save
        combined_df = pd.concat([df, new_match], ignore_index=True)
        combined_df.to_csv(self.matches_file, index=False)

    def get_match_history(
        self,
        agent_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get match history for an agent.

        Args:
            agent_id: Agent identifier
            limit: Maximum number of matches to return

        Returns:
            List of match dictionaries
        """
        df = pd.read_csv(self.matches_file)

        # Find matches where agent participated
        agent_matches = df[
            (df['agent_a_id'] == agent_id) | (df['agent_b_id'] == agent_id)
        ].copy()

        # Sort by round number (most recent first)
        agent_matches = agent_matches.sort_values('round_number', ascending=False)

        # Limit if specified
        if limit:
            agent_matches = agent_matches.head(limit)

        # Convert to list of dicts
        matches = []
        for _, row in agent_matches.iterrows():
            match = {
                'round_number': int(row['round_number']),
                'opponent_id': row['agent_b_id'] if row['agent_a_id'] == agent_id else row['agent_a_id'],
                'winner': row['winner'],
                'turns': int(row['turns']),
                'timestamp': row['timestamp'],
                'agent_won': (row['winner'] == 'a' and row['agent_a_id'] == agent_id) or
                            (row['winner'] == 'b' and row['agent_b_id'] == agent_id)
            }
            matches.append(match)

        return matches

    # Analytics methods (bonus functionality)

    def get_agent_statistics(self, agent_id: str) -> Dict:
        """
        Get comprehensive statistics for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Statistics dictionary
        """
        matches = self.get_match_history(agent_id)

        if not matches:
            return {
                'total_matches': 0,
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'win_rate': 0.0,
                'avg_turns': 0.0
            }

        wins = sum(1 for m in matches if m['agent_won'])
        draws = sum(1 for m in matches if m['winner'] == 'draw')
        losses = len(matches) - wins - draws

        return {
            'total_matches': len(matches),
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': wins / len(matches) if matches else 0,
            'avg_turns': sum(m['turns'] for m in matches) / len(matches)
        }

    def get_round_summary(self, round_number: int) -> Dict:
        """
        Get summary statistics for a round.

        Args:
            round_number: Round number

        Returns:
            Round summary dictionary
        """
        df = pd.read_csv(self.matches_file)
        round_matches = df[df['round_number'] == round_number]

        if round_matches.empty:
            return {'total_matches': 0}

        total_turns = round_matches['turns'].sum()
        draws = (round_matches['winner'] == 'draw').sum()

        return {
            'total_matches': len(round_matches),
            'total_turns': int(total_turns),
            'avg_turns': total_turns / len(round_matches),
            'draws': int(draws)
        }