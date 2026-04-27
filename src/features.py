import re
import hashlib
import random
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

class LocalFeatureEstimator:
    """
    Zero-cost feature estimator that maps metadata to numerical song features.
    Now with deterministic variance and jitter for high expressiveness.
    """
    
    GENRE_MAP = {
        "rock": {"energy": 0.8, "tempo": 130, "mood": "intense", "valence": 0.5, "instrumentalness": 0.1},
        "metal": {"energy": 0.95, "tempo": 160, "mood": "intense", "valence": 0.3, "instrumentalness": 0.2},
        "pop": {"energy": 0.7, "tempo": 120, "mood": "happy", "valence": 0.8, "speechiness": 0.1},
        "lofi": {"energy": 0.3, "tempo": 80, "mood": "chill", "valence": 0.6, "instrumentalness": 0.8},
        "chill": {"energy": 0.4, "tempo": 90, "mood": "chill", "valence": 0.7, "instrumentalness": 0.5},
        "jazz": {"energy": 0.4, "tempo": 100, "mood": "mellow", "valence": 0.6, "instrumentalness": 0.6},
        "classical": {"energy": 0.3, "tempo": 70, "mood": "mellow", "valence": 0.4, "instrumentalness": 0.95},
        "electronic": {"energy": 0.85, "tempo": 128, "mood": "energetic", "valence": 0.7, "instrumentalness": 0.4},
        "hip hop": {"energy": 0.65, "tempo": 95, "mood": "confident", "valence": 0.6, "speechiness": 0.5},
        "rap": {"energy": 0.7, "tempo": 90, "mood": "confident", "valence": 0.5, "speechiness": 0.8},
        "folk": {"energy": 0.4, "tempo": 110, "mood": "mellow", "valence": 0.6, "acousticness": 0.7},
        "acoustic": {"energy": 0.3, "tempo": 100, "mood": "mellow", "valence": 0.5, "acousticness": 0.9},
        "asmr": {"energy": 0.1, "tempo": 60, "mood": "calm", "valence": 0.5, "speechiness": 0.9, "acousticness": 0.8},
        "spoken": {"energy": 0.2, "tempo": 70, "mood": "neutral", "valence": 0.5, "speechiness": 0.95},
        "ambient": {"energy": 0.2, "tempo": 60, "mood": "calm", "valence": 0.5, "instrumentalness": 0.9, "acousticness": 0.3},
    }

    KEYWORD_MODIFIERS = {
        r"\bacoustic\b": {"energy": -0.2, "acousticness": 0.8, "instrumentalness": 0.2},
        r"\bremix\b": {"energy": 0.1, "danceability": 0.1, "instrumentalness": 0.1},
        r"\blive\b": {"energy": 0.1, "liveness": 0.8},
        r"\bconcert\b": {"liveness": 0.9},
        r"\bchill\b": {"energy": -0.1, "mood": "chill"},
        r"\bsad\b": {"valence": -0.3, "mood": "sad"},
        r"\bhappy\b": {"valence": 0.3, "mood": "happy"},
        r"\binstrumental\b": {"instrumentalness": 0.9},
        r"\bkaraoke\b": {"instrumentalness": 0.8, "speechiness": -0.2},
        r"\basmr\b": {"speechiness": 0.9, "energy": -0.3, "mood": "calm"},
        r"\bfeat\b": {"speechiness": 0.1},
        r"\bvocals\b": {"instrumentalness": -0.5, "speechiness": 0.2},
    }

    @classmethod
    def _generate_deterministic_offset(cls, seed_str, scale=0.1):
        """Generates a pseudo-random float between -scale and +scale based on a string."""
        hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        return ((hash_val % 2000) / 1000.0 - 1.0) * scale

    @classmethod
    def estimate_features(cls, title, artist, genre):
        # Base features
        features = {
            "energy": 0.5,
            "tempo": 110,
            "mood": "neutral",
            "valence": 0.5,
            "danceability": 0.5,
            "acousticness": 0.5,
            "instrumentalness": 0.1,
            "speechiness": 0.05,
            "liveness": 0.1
        }

        # 1. Apply Genre Mappings
        genre_lower = str(genre).lower()
        for g_key, g_vals in cls.GENRE_MAP.items():
            if g_key in genre_lower:
                features.update(g_vals)
                break
        
        # 2. Apply Keyword Modifiers
        title_lower = str(title).lower()
        for pattern, mods in cls.KEYWORD_MODIFIERS.items():
            if re.search(pattern, title_lower):
                for k, v in mods.items():
                    if isinstance(v, (int, float)):
                        features[k] = features.get(k, 0.5) + v
                    else:
                        features[k] = v

        # 3. Add Deterministic Variance (The "Expressiveness" Fix)
        # Use a combination of title and artist to make every song unique
        unique_seed = f"{title}{artist}"
        for feat in ["energy", "valence", "danceability", "acousticness", "instrumentalness", "speechiness", "liveness"]:
            # Add unique offset based on song identity
            offset = cls._generate_deterministic_offset(f"{unique_seed}{feat}", scale=0.15)
            features[feat] = max(0.0, min(1.0, features[feat] + offset))
        
        # Unique Tempo jitter
        tempo_offset = cls._generate_deterministic_offset(f"{unique_seed}tempo", scale=20)
        features["tempo"] = max(50.0, min(220.0, features["tempo"] + tempo_offset))

        # 4. Add subtle Gaussian Jitter for session-level variety
        for feat in ["energy", "valence", "danceability", "acousticness"]:
            features[feat] = max(0.0, min(1.0, features[feat] + random.uniform(-0.02, 0.02)))

        features["tempo_norm"] = features["tempo"] / 200.0
        return features

class SemanticFeatureExtractor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.is_fitted = False

    def prepare_metadata_string(self, song_info):
        if hasattr(song_info, 'artist'):
            return f"{song_info.artist} {song_info.title} {song_info.genre}".lower()
        else:
            try:
                artist = song_info.get('artist', '')
                title = song_info.get('title', '')
                genre = song_info.get('genre', '')
                return f"{artist} {title} {genre}".lower()
            except:
                return ""

    def fit(self, songs_list):
        texts = [self.prepare_metadata_string(s) for s in songs_list if s is not None]
        texts = [t for t in texts if t.strip()]
        if texts:
            self.vectorizer.fit(texts)
            self.is_fitted = True

    def transform(self, items):
        if not self.is_fitted:
            return None
        if isinstance(items, list):
            texts = [self.prepare_metadata_string(s) for s in items]
        else:
            texts = [self.prepare_metadata_string(items)]
        return self.vectorizer.transform(texts)
