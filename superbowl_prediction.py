#!/usr/bin/env python3
"""
Super Bowl Winner Prediction: Seahawks vs Patriots
Uses multiple factors to simulate and predict the winner.
"""

import random
import hashlib
from datetime import datetime

# Team stats and factors (inspired by historical data)
TEAMS = {
    "Seahawks": {
        "name": "Seattle Seahawks",
        "offense_rating": 85,
        "defense_rating": 88,
        "special_teams": 82,
        "coaching": 87,
        "momentum": 84,
        "experience": 80,
        "clutch_factor": 86,
    },
    "Patriots": {
        "name": "New England Patriots",
        "offense_rating": 87,
        "defense_rating": 86,
        "special_teams": 84,
        "coaching": 95,  # Belichick factor
        "momentum": 88,
        "experience": 92,
        "clutch_factor": 90,  # Brady factor
    }
}


def calculate_team_score(team_stats: dict) -> float:
    """Calculate overall team score based on weighted factors."""
    weights = {
        "offense_rating": 0.20,
        "defense_rating": 0.20,
        "special_teams": 0.10,
        "coaching": 0.15,
        "momentum": 0.10,
        "experience": 0.10,
        "clutch_factor": 0.15,
    }

    score = sum(team_stats[factor] * weight
                for factor, weight in weights.items())
    return score


def simulate_game(seahawks_score: float, patriots_score: float) -> tuple:
    """Simulate a single game with some randomness."""
    # Add game-day variability (random factor between 0.9 and 1.1)
    seahawks_final = seahawks_score * random.uniform(0.9, 1.1)
    patriots_final = patriots_score * random.uniform(0.9, 1.1)

    # Simulate actual game score (roughly)
    seahawks_points = int(seahawks_final * 0.35 + random.randint(-7, 7))
    patriots_points = int(patriots_final * 0.35 + random.randint(-7, 7))

    # Ensure no ties
    if seahawks_points == patriots_points:
        if random.random() > 0.5:
            seahawks_points += 3
        else:
            patriots_points += 3

    winner = "Seahawks" if seahawks_points > patriots_points else "Patriots"
    return winner, seahawks_points, patriots_points


def run_simulation(num_simulations: int = 10000) -> dict:
    """Run multiple game simulations to predict the winner."""
    seahawks_base = calculate_team_score(TEAMS["Seahawks"])
    patriots_base = calculate_team_score(TEAMS["Patriots"])

    results = {"Seahawks": 0, "Patriots": 0}
    total_scores = {"Seahawks": [], "Patriots": []}

    for _ in range(num_simulations):
        winner, sea_pts, ne_pts = simulate_game(seahawks_base, patriots_base)
        results[winner] += 1
        total_scores["Seahawks"].append(sea_pts)
        total_scores["Patriots"].append(ne_pts)

    return {
        "wins": results,
        "avg_scores": {
            "Seahawks": sum(total_scores["Seahawks"]) / num_simulations,
            "Patriots": sum(total_scores["Patriots"]) / num_simulations,
        },
        "base_ratings": {
            "Seahawks": seahawks_base,
            "Patriots": patriots_base,
        }
    }


def display_results(results: dict) -> str:
    """Display the prediction results."""
    total_games = sum(results["wins"].values())

    seahawks_pct = (results["wins"]["Seahawks"] / total_games) * 100
    patriots_pct = (results["wins"]["Patriots"] / total_games) * 100

    winner = "Seahawks" if results["wins"]["Seahawks"] > results["wins"]["Patriots"] else "Patriots"
    winner_pct = max(seahawks_pct, patriots_pct)

    output = []
    output.append("=" * 60)
    output.append("       SUPER BOWL PREDICTION: SEAHAWKS vs PATRIOTS")
    output.append("=" * 60)
    output.append("")
    output.append("Team Ratings:")
    output.append(f"  Seattle Seahawks:     {results['base_ratings']['Seahawks']:.1f}")
    output.append(f"  New England Patriots: {results['base_ratings']['Patriots']:.1f}")
    output.append("")
    output.append(f"Simulation Results ({total_games:,} games):")
    output.append(f"  Seahawks wins: {results['wins']['Seahawks']:,} ({seahawks_pct:.1f}%)")
    output.append(f"  Patriots wins: {results['wins']['Patriots']:,} ({patriots_pct:.1f}%)")
    output.append("")
    output.append("Average Projected Score:")
    output.append(f"  Seahawks: {results['avg_scores']['Seahawks']:.1f}")
    output.append(f"  Patriots: {results['avg_scores']['Patriots']:.1f}")
    output.append("")
    output.append("-" * 60)
    output.append(f"  PREDICTION: {TEAMS[winner]['name'].upper()}")
    output.append(f"  Win Probability: {winner_pct:.1f}%")
    output.append("-" * 60)

    return "\n".join(output)


def main():
    """Main function to run the Super Bowl prediction."""
    # Seed with current timestamp for reproducibility tracking
    seed = int(datetime.now().timestamp())
    random.seed(seed)

    print(f"\nRunning Super Bowl simulation (seed: {seed})...\n")

    results = run_simulation(num_simulations=10000)
    print(display_results(results))
    print()


if __name__ == "__main__":
    main()
