import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a single song and its audio feature attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Stores a user's target feature values used to score and rank songs."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # Extended numeric targets for weighted scoring (optional — safe defaults keep existing tests passing)
    target_acousticness: float = 0.5
    target_tempo_bpm: float = 100.0
    target_valence: float = 0.5


class Recommender:
    """OOP wrapper around score_song for recommending and explaining songs."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _profile_to_dict(self, user: UserProfile) -> Dict:
        return {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "target_acousticness": user.target_acousticness,
            "target_tempo_bpm": user.target_tempo_bpm,
            "target_valence": user.target_valence,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = self._profile_to_dict(user)
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "tempo_bpm": song.tempo_bpm,
                "valence": song.valence,
                "acousticness": song.acousticness,
            }
            score, _ = score_song(prefs, song_dict)
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        prefs = self._profile_to_dict(user)
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "acousticness": song.acousticness,
        }
        score, reasons = score_song(prefs, song_dict)
        return f"Score {score:.2f}: " + "; ".join(reasons)


# ---------------------------------------------------------------------------
# Algorithm Recipe
# ---------------------------------------------------------------------------
# Categorical bonuses (flat points):
#   +2.0  genre match  — broad style alignment; strongest signal
#   +1.0  mood match   — emotional intent; cross-genre signal
#
# Numeric similarity (each feature uses 1 - |user_target - song_value|,
# then scaled by weight; tempo is normalized to 0–1 via /200 before diff):
#   energy        × 1.50  — best cluster separator in this dataset
#   acousticness  × 1.25  — near-inverse of energy; reinforces chill vs. intense axis
#   tempo_bpm     × 0.75  — activity context (workout vs. study)
#   valence       × 0.50  — emotional color; less decisive in small catalog
#
# Max possible score: 2.0 + 1.0 + 1.5 + 1.25 + 0.75 + 0.50 = 7.0
# ---------------------------------------------------------------------------

WEIGHTS = {
    "genre_match": 1.5,
    "mood_match": 1.0,
    "energy": 1.5,
    "acousticness": 1.25,
    "tempo_bpm": 0.75,
    "valence": 0.50,
}
# Max possible score: 1.5 + 1.0 + 1.5 + 1.25 + 0.75 + 0.50 = 6.50


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Returns (score, reasons) by applying genre/mood bonuses and weighted numeric similarity."""
    score = 0.0
    reasons = []

    user_genre = user_prefs.get("favorite_genre", user_prefs.get("genre", ""))
    user_mood = user_prefs.get("favorite_mood", user_prefs.get("mood", ""))

    if str(song.get("genre", "")).lower() == user_genre.lower():
        score += WEIGHTS["genre_match"]
        reasons.append(f"genre match ({song['genre']}) +{WEIGHTS['genre_match']:.1f}")

    if str(song.get("mood", "")).lower() == user_mood.lower():
        score += WEIGHTS["mood_match"]
        reasons.append(f"mood match ({song['mood']}) +{WEIGHTS['mood_match']:.1f}")

    user_energy = float(user_prefs.get("target_energy", user_prefs.get("energy", 0.5)))
    energy_sim = 1.0 - abs(user_energy - float(song.get("energy", 0.5)))
    pts = energy_sim * WEIGHTS["energy"]
    score += pts
    reasons.append(f"energy sim {energy_sim:.2f} ×{WEIGHTS['energy']} = +{pts:.2f}")

    user_acousticness = float(user_prefs.get("target_acousticness", 0.5))
    acousticness_sim = 1.0 - abs(user_acousticness - float(song.get("acousticness", 0.5)))
    pts = acousticness_sim * WEIGHTS["acousticness"]
    score += pts
    reasons.append(f"acousticness sim {acousticness_sim:.2f} ×{WEIGHTS['acousticness']} = +{pts:.2f}")

    user_tempo = float(user_prefs.get("target_tempo_bpm", 100.0))
    # Normalize tempo to 0–1 range (max BPM in catalog is 168; use 200 as ceiling)
    tempo_sim = 1.0 - abs(user_tempo - float(song.get("tempo_bpm", 100.0))) / 200.0
    pts = tempo_sim * WEIGHTS["tempo_bpm"]
    score += pts
    reasons.append(f"tempo sim {tempo_sim:.2f} ×{WEIGHTS['tempo_bpm']} = +{pts:.2f}")

    user_valence = float(user_prefs.get("target_valence", 0.5))
    valence_sim = 1.0 - abs(user_valence - float(song.get("valence", 0.5)))
    pts = valence_sim * WEIGHTS["valence"]
    score += pts
    reasons.append(f"valence sim {valence_sim:.2f} ×{WEIGHTS['valence']} = +{pts:.2f}")

    return round(score, 4), reasons


def load_songs(csv_path: str) -> List[Dict]:
    """Reads songs.csv and returns a list of dicts with numeric fields cast to int/float."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, sorts by score descending, and returns the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored.append((song, score, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
