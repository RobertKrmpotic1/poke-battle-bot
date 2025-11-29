"""
Rating service - ELO rating calculations.
Extracted from driver.py calculate_new_elo method.
"""
import math
from typing import Tuple


class RatingService:
    """
    Service for calculating ELO ratings.
    Pure domain logic with no external dependencies.
    """
    
    def __init__(self, k_value: int = 50):
        """
        Initialize rating service.
        
        Args:
            k_value: K-factor for ELO calculation (higher = more volatile)
        """
        self.k_value = k_value

    def calculate_expected_score(self, rating_a: int, rating_b: int) -> float:
        """
        Calculate expected score for player A against player B.
        
        Args:
            rating_a: Rating of player A
            rating_b: Rating of player B
            
        Returns:
            Expected score between 0 and 1
        """
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def calculate_new_rating(
        self, 
        current_rating: int, 
        opponent_rating: int, 
        score: float
    ) -> int:
        """
        Calculate new ELO rating after a game.
        
        Args:
            current_rating: Current ELO rating
            opponent_rating: Opponent's ELO rating
            score: Actual score (1.0 = win, 0.5 = draw, 0.0 = loss)
            
        Returns:
            New ELO rating
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"Score must be between 0 and 1, got {score}")
        
        expected = self.calculate_expected_score(current_rating, opponent_rating)
        rating_change = self.k_value * (score - expected)
        new_rating = int(current_rating + rating_change)
        
        # Ensure rating doesn't go negative
        return max(0, new_rating)

    def calculate_ratings_after_battle(
        self,
        rating_a: int,
        rating_b: int,
        winner: str  # "a", "b", or "draw"
    ) -> Tuple[int, int]:
        """
        Calculate new ratings for both players after a battle.
        
        Args:
            rating_a: Rating of player A
            rating_b: Rating of player B
            winner: "a" if A won, "b" if B won, "draw" for draw
            
        Returns:
            Tuple of (new_rating_a, new_rating_b)
        """
        if winner == "a":
            score_a, score_b = 1.0, 0.0
        elif winner == "b":
            score_a, score_b = 0.0, 1.0
        elif winner == "draw":
            score_a, score_b = 0.5, 0.5
        else:
            raise ValueError(f"Invalid winner value: {winner}. Must be 'a', 'b', or 'draw'")
        
        new_rating_a = self.calculate_new_rating(rating_a, rating_b, score_a)
        new_rating_b = self.calculate_new_rating(rating_b, rating_a, score_b)
        
        return new_rating_a, new_rating_b

    def rating_difference_threshold(self, rating_diff: int) -> str:
        """
        Categorize rating difference.
        
        Args:
            rating_diff: Absolute difference in ratings
            
        Returns:
            Category string
        """
        if rating_diff < 50:
            return "even"
        elif rating_diff < 100:
            return "slight_advantage"
        elif rating_diff < 200:
            return "moderate_advantage"
        else:
            return "large_advantage"
