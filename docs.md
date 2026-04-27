# Music Recommender Extension Documentation

## Infrastructure Overview
The system is an interactive Streamlit application powered by an **Ensemble Recommendation Engine**. It combines numerical audio feature analysis with semantic text matching and internet discovery (RAG) to provide personalized music suggestions.

## Files and Modules

### `src/app.py`
The central orchestration layer.
- **Session Management**: Maintains persistence via JSON profiles.
- **Dynamic Interaction**: Handles real-time feedback (ratings) and navigates between library management and global exploration.
- **UI State**: Uses `st.session_state` to persist searches and recommendation results during a session.

### `src/models.py`
Defines the `UserProfile`, `Playlist`, and `SongInfo` data structures.
- Supports comprehensive metadata storage, including numerical features and artwork/preview URLs.

### `src/features.py` (Enhanced)
- **`LocalFeatureEstimator`**: Maps genre/title metadata to numerical vectors (Energy, Tempo, Mood).
- **`SemanticFeatureExtractor`**: Implements **TF-IDF Vectorization** to provide semantic context (Artist/Genre/Title matching).

### `src/recommender_v2.py` (New)
The heart of the system. Implements an **Ensemble Model**:
1.  **Item-to-Item Similarity**: Pairwise cosine similarity between candidates and individual seed songs.
2.  **Multi-Centroid Clustering**: Uses **K-Means** to identify distinct "vibes" in user history and finds matches for each cluster.
3.  **TF-IDF Similarity**: Weights suggestions based on semantic text overlap.
4.  **Explainable AI**: Generates human-readable reasons for every suggestion based on which ensemble pillar triggered it.

## Key Logic Flows

### 1. Global RAG Discovery
- **Identify**: Extract top artists/genres from seeds.
- **Retrieve**: Query iTunes API for fresh world-wide candidates.
- **Ensemble Rank**: Score candidates using both numerical and semantic models.
- **Deliver**: Display with artwork, previews, and "Why this?" explanations.

### 2. Session-Based Learning
- When a user provides a **5-star rating**, the model performs a "Preference Shift."
- The song is temporarily added to the session's active seeds.
- This immediately influences the next generation of recommendations by moving the user's "taste centroid."

---
*See [UML.md](UML.md) for architectural diagrams.*
