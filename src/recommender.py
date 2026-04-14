import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class Song:
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
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_tempo: float = 120.0
    target_valence: float = 0.5
    likes_acoustic: bool = False
    
    # Adjustable weights for the scoring algorithm
    weights: Dict[str, float] = field(default_factory=lambda: {
        "genre": 0.35,
        "mood": 0.25,
        "energy": 0.1,
        "tempo": 0.1,
        "valence": 0.05,
        "acousticness": 0.1,
        "danceability": 0.05
    })

class Recommender:
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def score_song(self, user: UserProfile, song: Song) -> float:
        score = 0.0
        w = user.weights

        # Categorical matching
        if song.genre.lower() == user.favorite_genre.lower():
            score += w["genre"]
        
        if song.mood.lower() == user.favorite_mood.lower():
            score += w["mood"]

        # Numerical "Closeness" (1.0 - normalized difference)
        # Energy (0.0 - 1.0)
        energy_score = 1.0 - abs(song.energy - user.target_energy)
        score += w["energy"] * energy_score

        # Tempo (Normalized roughly between 60 and 200 BPM)
        tempo_diff = abs(song.tempo_bpm - user.target_tempo)
        tempo_score = 1.0 - min(tempo_diff / 100.0, 1.0) 
        score += w["tempo"] * tempo_score

        # Valence (0.0 - 1.0)
        valence_score = 1.0 - abs(song.valence - user.target_valence)
        score += w["valence"] * valence_score

        # Acousticness (0.0 - 1.0)
        acoustic_score = 1.0 - abs(song.acousticness - (1.0 if user.likes_acoustic else 0.0))
        score += w["acousticness"] * acoustic_score

        # Danceability (0.0 - 1.0)
        # We'll assume a high danceability preference for now, or could add target_danceability to UserProfile
        dance_score = song.danceability 
        score += w["danceability"] * dance_score

        return score

    def recommend(self, user: UserProfile, k: int = 5) -> List[Tuple[Song, float]]:
        # Ranking Rule: Score all, sort descending, take top K
        scored_list = []
        for song in self.songs:
            score = self.score_song(user, song)
            scored_list.append((song, score))
        
        scored_list.sort(key=lambda x: x[1], reverse=True)
        return scored_list[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre.lower() == user.favorite_genre.lower():
            reasons.append(f"it matches your favorite genre ({user.favorite_genre})")
        if song.mood.lower() == user.favorite_mood.lower():
            reasons.append(f"it aligns with your current mood ({user.favorite_mood})")
        
        # Check which numerical feature contributed most significantly
        energy_closeness = 1.0 - abs(song.energy - user.target_energy)
        if energy_closeness > 0.9:
            reasons.append("the energy level is exactly what you're looking for")

        if not reasons:
            return "This song is a well-rounded match based on your overall profile."
        
        return "Because " + " and ".join(reasons) + "."

def load_songs(csv_path: str) -> List[Dict]:
    songs = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                songs.append({
                    'id': int(row['id']),
                    'title': row['title'],
                    'artist': row['artist'],
                    'genre': row['genre'],
                    'mood': row['mood'],
                    'energy': float(row['energy']),
                    'tempo_bpm': float(row['tempo_bpm']),
                    'valence': float(row['valence']),
                    'danceability': float(row['danceability']),
                    'acousticness': float(row['acousticness'])
                })
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    user = UserProfile(
        favorite_genre=user_prefs.get('genre', ''),
        favorite_mood=user_prefs.get('mood', ''),
        target_energy=user_prefs.get('energy', 0.5),
        target_tempo=user_prefs.get('tempo', 120.0),
        target_valence=user_prefs.get('valence', 0.5)
    )
    
    song_objects = [Song(**s) for s in songs]
    recommender = Recommender(song_objects)
    recommendations = recommender.recommend(user, k)
    
    return [
        (s.__dict__, score, recommender.explain_recommendation(user, s))
        for s, score in recommendations
    ]
