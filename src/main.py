"""
Command line runner for the Music Recommender Simulation.
Runs multiple user profiles including edge cases to stress test scoring logic.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from recommender import load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

PROFILES = [
    {
        "label": "High-Energy Pop",
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
        "target_acousticness": 0.10,
        "target_tempo_bpm": 128,
        "target_valence": 0.85,
        "likes_acoustic": False,
    },
    {
        "label": "Chill Lofi",
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.38,
        "target_acousticness": 0.80,
        "target_tempo_bpm": 75,
        "target_valence": 0.58,
        "likes_acoustic": True,
    },
    {
        "label": "Deep Intense Rock",
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "target_acousticness": 0.05,
        "target_tempo_bpm": 155,
        "target_valence": 0.40,
        "likes_acoustic": False,
    },
    # --- Edge cases (adversarial profiles) ---
    {
        "label": "EDGE: Conflicting (high energy + sad mood)",
        "favorite_genre": "blues",
        "favorite_mood": "sad",
        "target_energy": 0.90,
        "target_acousticness": 0.10,
        "target_tempo_bpm": 140,
        "target_valence": 0.20,
        "likes_acoustic": False,
    },
    {
        "label": "EDGE: Genre Orphan (metal — only 1 song in catalog)",
        "favorite_genre": "metal",
        "favorite_mood": "angry",
        "target_energy": 0.96,
        "target_acousticness": 0.07,
        "target_tempo_bpm": 168,
        "target_valence": 0.22,
        "likes_acoustic": False,
    },
    {
        "label": "EDGE: All-Middle (0.5 everything — no strong preference)",
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.50,
        "target_acousticness": 0.50,
        "target_tempo_bpm": 100,
        "target_valence": 0.50,
        "likes_acoustic": True,
    },
]


def run_profile(profile, songs):
    label = profile["label"]
    prefs = {k: v for k, v in profile.items() if k != "label"}
    results = recommend_songs(prefs, songs, k=5)

    print("\n" + "=" * 60)
    print(f"  Profile: {label}")
    print("=" * 60)
    for i, (song, score, explanation) in enumerate(results, 1):
        print(f"\n  #{i}  {song['title']} — {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}")
        print(f"       Score: {score:.2f} / 7.00")
        print(f"       Why:   {explanation}")
    print()


def main() -> None:
    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    for profile in PROFILES:
        run_profile(profile, songs)


if __name__ == "__main__":
    main()
