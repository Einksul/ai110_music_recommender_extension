# Music Recommender Simulation Documentation

## Infrastructure Overview
The system is designed with both functional and object-oriented approaches to handle music recommendations based on user profiles and song attributes.

## Files and Modules

### `src/recommender.py`
This module contains the core logic and data structures for the recommendation engine.

#### Data Structures
- **`Song`**: A dataclass representing a song with attributes like genre, mood, energy, tempo, and more.
- **`UserProfile`**: A dataclass representing user preferences. Includes an adjustable `weights` dictionary to control the influence of different features.

#### Classes
- **`Recommender`**: 
  - `score_song(user, song)`: **Pointwise Evaluation**. Calculates a raw score (0.0 to 1.0) for a single song based on the user's weighted preferences.
  - `recommend(user, k)`: **Listwise Ranking**. Scores all songs in the library, sorts them by score, and returns the top `k` results.
  - `explain_recommendation(user, song)`: Provides human-readable reasoning for why a song was chosen.

## Scoring Algorithm

The scoring system uses a weighted linear combination of categorical and numerical matches:

1.  **Categorical Match (Exact)**:
    - `Genre`: Exact match (Default weight: 0.4)
    - `Mood`: Exact match (Default weight: 0.3)
2.  **Numerical Closeness (Distance-based)**:
    - Calculated as `1.0 - abs(song_value - user_target)`.
    - `Energy` (Default weight: 0.1)
    - `Tempo` (Normalized diff / 100, Default weight: 0.1)
    - `Valence` (Default weight: 0.05)
    - `Acousticness` (Checks against `likes_acoustic` boolean, Default weight: 0.1)
    - `Danceability` (Default weight: 0.05)

This approach ensures that even if a song doesn't match the genre exactly, it can still rank high if its "vibe" (energy/tempo) is perfectly aligned with the user's needs.

#### Functional Interface
- **`load_songs(csv_path: str)`**: Loads song data from a CSV file.
- **`recommend_songs(user_prefs: Dict, songs: List[Dict], k: int)`**: A functional entry point for recommendation logic, returning a list of tuples containing the song, its score, and an explanation.

### `src/main.py`
The command-line entry point for the simulation. It demonstrates the loading of songs and the generation of recommendations based on a hardcoded user profile.

### `tests/test_recommender.py`
Contains unit tests to ensure the validity of the recommendation logic and data loading.

## Design Philosophy
- **Modularity**: Data structures are separated from logic to allow for easy scaling and modification.
- **Extensibility**: The system supports both OOP and functional patterns to accommodate different integration styles.
- **Transparency**: Every recommendation is accompanied by an explanation to provide user-facing reasoning.

## Recommendation Strategies Research

### Content-Based Filtering
- **Logic**: "If you liked this, you'll like this similar thing."
- **Focus**: Song attributes (genre, tempo, mood).
- **Pros**: Handles new items well, very transparent.
- **Cons**: Can lead to "filter bubbles" (low diversity).

### Collaborative Filtering
- **Logic**: "If people who are like you liked this, you'll like it too."
- **Focus**: User behavior (likes, skips, playlist additions).
- **Pros**: High discovery/serendipity, doesn't need song metadata.
- **Cons**: "Cold start" problem for new users/items.

## Proposed Data Model Expansion

### 1. Song Metadata (Current `songs.csv`)
- **Content features**: `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`.

### 2. User Interaction Data (Collaborative)
- **`Likes`**: Binary (True/False) or scale (1-5). Crucial for explicit feedback.
- **`Skips`**: Implicit negative feedback. Frequent skips should lower a song's score.
- **`Playlists`**: Groups of songs that users think "belong" together. High signal for item-item similarity.

### 3. Temporal/Contextual Data
- **`Timestamp`**: When was the song played? (Helps with recency bias).
- **`Mood`**: Dynamic user mood vs. static song mood.
