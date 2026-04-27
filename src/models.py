import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class SongInfo:
    id: str
    title: str
    artist: str
    album: str
    genre: str = ""
    mood: str = ""
    artwork_url: str = ""
    # Numerical features for KNN
    energy: float = 0.5
    tempo: float = 110.0
    valence: float = 0.5
    danceability: float = 0.5
    acousticness: float = 0.5
    instrumentalness: float = 0.0
    speechiness: float = 0.0
    liveness: float = 0.0
    preview_url: str = ""

@dataclass
class Playlist:
    name: str
    songs: List[SongInfo] = field(default_factory=list)

@dataclass
class UserProfile:
    name: str
    playlists: Dict[str, Playlist] = field(default_factory=dict)
    liked_songs: List[SongInfo] = field(default_factory=list)
    user_metadata: Dict[str, Any] = field(default_factory=lambda: {
        "interaction_history": [],
        "inferred_preferences": {}
    })

    def save(self, directory: str = "profiles"):
        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, f"{self.name}.json")
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    def to_dict(self):
        return {
            "name": self.name,
            "playlists": {k: {"name": v.name, "songs": [asdict(s) for s in v.songs]} for k, v in self.playlists.items()},
            "liked_songs": [asdict(s) for s in self.liked_songs],
            "user_metadata": self.user_metadata
        }

    @classmethod
    def load(cls, name: str, directory: str = "profiles"):
        filepath = os.path.join(directory, f"{name}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        playlists = {}
        for k, v in data.get("playlists", {}).items():
            songs = [SongInfo(**s) for s in v.get("songs", [])]
            playlists[k] = Playlist(name=v["name"], songs=songs)
            
        liked_songs = [SongInfo(**s) for s in data.get("liked_songs", [])]
        
        return cls(
            name=data["name"],
            playlists=playlists,
            liked_songs=liked_songs,
            user_metadata=data.get("user_metadata", {})
        )

def list_profiles(directory: str = "profiles"):
    if not os.path.exists(directory):
        os.makedirs(directory)
        return []
    return [f.replace(".json", "") for f in os.listdir(directory) if f.endswith(".json")]
