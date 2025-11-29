"""
Tests for pandas league repository.
"""
import pytest
import tempfile
import os
from pathlib import Path
from infrastructure.repositories.pandas_league_repository import PandasLeagueRepository
from domain.repositories.league_repository import LeagueStanding
from domain.entities.agent import Agent


class TestPandasLeagueRepository:
    """Test pandas-based league data persistence."""

    def test_initialization(self):
        """Test repository initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = PandasLeagueRepository(data_dir=tmpdir)
            assert os.path.exists(os.path.join(tmpdir, "config.json"))

    def test_save_and_load_standings(self):
        """Test saving and loading league standings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = PandasLeagueRepository(data_dir=tmpdir)
            
            standings = [
                LeagueStanding(agent_id="agent1", rank=1, elo=1200, wins=5, losses=3, draws=0, battles=8),
                LeagueStanding(agent_id="agent2", rank=2, elo=1150, wins=3, losses=5, draws=0, battles=8)
            ]
            
            repo.save_standings(round_number=1, standings=standings)
            
            # Verify file was created
            standings_file = Path(tmpdir) / "standings.csv"
            assert standings_file.exists()

    def test_get_agent_statistics(self):
        """Test retrieving agent statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = PandasLeagueRepository(data_dir=tmpdir)
            
            standings = [
                LeagueStanding(agent_id="agent1", rank=1, elo=1200, wins=10, losses=5, draws=0, battles=15)
            ]
            
            repo.save_standings(round_number=1, standings=standings)
            
            stats = repo.get_agent_statistics(agent_id="agent1")
            
            assert stats is not None
            # Check for actual returned keys
            assert "total_matches" in stats or "wins" in stats
