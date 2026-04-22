"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from recommender import load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


def main() -> None:
    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    # Default pop/happy profile
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "target_acousticness": 0.20,
        "target_tempo_bpm": 120,
        "target_valence": 0.82,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 55)
    print("  🎵  Top Recommendations for pop/happy listener")
    print("=" * 55)
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n#{i}  {song['title']} — {song['artist']}")
        print(f"    Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"    Score: {score:.2f} / 7.00")
        print(f"    Why:   {explanation}")
    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
