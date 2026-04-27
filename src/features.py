import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

class LocalFeatureEstimator:
    """
    Zero-cost feature estimator that maps metadata to numerical song features.
    """
    
    # Simple genre mappings
    GENRE_MAP = {
        "rock": {"energy": 0.8, "tempo": 130, "mood": "intense", "valence": 0.5},
        "metal": {"energy": 0.95, "tempo": 160, "mood": "intense", "valence": 0.3},
        "pop": {"energy": 0.7, "tempo": 120, "mood": "happy", "valence": 0.8},
        "lofi": {"energy": 0.3, "tempo": 80, "mood": "chill", "valence": 0.6},
        "chill": {"energy": 0.4, "tempo": 90, "mood": "chill", "valence": 0.7},
        "jazz": {"energy": 0.4, "tempo": 100, "mood": "mellow", "valence": 0.6},
        "classical": {"energy": 0.3, "tempo": 70, "mood": "mellow", "valence": 0.4},
        "electronic": {"energy": 0.85, "tempo": 128, "mood": "energetic", "valence": 0.7},
        "hip hop": {"energy": 0.65, "tempo": 95, "mood": "confident", "valence": 0.6},
        "rap": {"energy": 0.7, "tempo": 90, "mood": "confident", "valence": 0.5},
        "folk": {"energy": 0.4, "tempo": 110, "mood": "mellow", "valence": 0.6},
        "acoustic": {"energy": 0.3, "tempo": 100, "mood": "mellow", "valence": 0.5},
    }

    # Keyword modifiers
    KEYWORD_MODIFIERS = {
        r"\bacoustic\b": {"energy": -0.2, "acousticness": 0.8},
        r"\bremix\b": {"energy": 0.1, "danceability": 0.1},
        r"\blive\b": {"energy": 0.1},
        r"\bchill\b": {"energy": -0.1, "mood": "chill"},
        r"\bsad\b": {"valence": -0.3, "mood": "sad"},
        r"\bhappy\b": {"valence": 0.3, "mood": "happy"},
    }

    @classmethod
    def estimate_features(cls, title, artist, genre):
        # Start with defaults
        features = {
            "energy": 0.5,
            "tempo": 110,
            "mood": "neutral",
            "valence": 0.5,
            "danceability": 0.5,
            "acousticness": 0.5
        }

        # 1. Apply Genre Mappings
        genre_lower = genre.lower()
        matched_genre = False
        for g_key, g_vals in cls.GENRE_MAP.items():
            if g_key in genre_lower:
                features.update(g_vals)
                matched_genre = True
                break
        
        # 2. Apply Keyword Modifiers from Title
        title_lower = title.lower()
        for pattern, mods in cls.KEYWORD_MODIFIERS.items():
            if re.search(pattern, title_lower):
                for k, v in mods.items():
                    if isinstance(v, (int, float)):
                        features[k] = max(0.0, min(1.0, features.get(k, 0.5) + v))
                    else:
                        features[k] = v

        # Normalize Tempo (Simple 0-1 scaling for model usage later)
        features["tempo_norm"] = features["tempo"] / 200.0

        return features

class SemanticFeatureExtractor:
    """
    Handles TF-IDF vectorization for semantic understanding of song metadata.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.is_fitted = False

    def prepare_metadata_string(self, song_info):
        """Combines artist, title, and genre into a single searchable string."""
        # song_info can be a SongInfo object or a dict from a row
        if hasattr(song_info, 'artist'):
            return f"{song_info.artist} {song_info.title} {song_info.genre}".lower()
        else:
            # Handle case where song_info might be a Series or dict
            try:
                artist = song_info.get('artist', '')
                title = song_info.get('title', '')
                genre = song_info.get('genre', '')
                return f"{artist} {title} {genre}".lower()
            except:
                return ""

    def fit(self, songs_list):
        """Fits the TF-IDF vectorizer on a list of items."""
        # Fix: Use 'is not None' because pandas objects have ambiguous truth values
        texts = [self.prepare_metadata_string(s) for s in songs_list if s is not None]
        texts = [t for t in texts if t.strip()]
        if texts:
            self.vectorizer.fit(texts)
            self.is_fitted = True

    def transform(self, items):
        """Transforms items into TF-IDF vectors."""
        if not self.is_fitted:
            return None
        
        if isinstance(items, list):
            texts = [self.prepare_metadata_string(s) for s in items]
        else:
            # Single item
            texts = [self.prepare_metadata_string(items)]
            
        return self.vectorizer.transform(texts)
