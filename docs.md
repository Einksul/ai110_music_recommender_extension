# Music Recommender Extension Documentation

## Infrastructure Overview
The system has evolved from a CLI simulation into a full-featured Streamlit web application. It handles user persistence via JSON profiles, manages playlists, and integrates with the iTunes Search API for global music discovery. A detailed data flow diagram can be found in [UML.md](UML.md).

## Files and Modules

### `src/app.py` (New)
The main entry point for the interactive web application.
- **Profile Management**: Handles session state for loading/creating user profiles.
- **Search Engine**: Orchestrates both local (CSV) and global (iTunes) searches.
- **Exploration Logic**: Implements drill-down views for Albums and Artists.
- **Interactive Components**: Features audio preview players, artwork displays, and real-time playlist management.

### `src/models.py` (New)
Defines the core data structures for persistence and UI state.
- **`SongInfo`**: A robust representation of a track, including IDs, metadata, and artwork URLs.
- **`Playlist`**: A named collection of `SongInfo` objects.
- **`UserProfile`**: Manages user data, multiple playlists, liked songs, and `user_metadata` for future model learning. Includes `save()` and `load()` logic for JSON persistence in the `profiles/` directory.

### `src/recommender.py`
Contains the core recommendation logic (weighted linear scoring). *Note: Integration with the new UI for active recommendations is the next development phase.*

## External Integrations

### iTunes Search API
Used for real-time global music discovery without requiring API keys.
- **Search**: Queries songs by title, artist, or album.
- **Lookup**: Retrieves all tracks for a specific album or the top tracks for an artist.
- **Media**: Provides 30-second audio previews and high-quality album artwork.

## Persistence Layer
- **Profiles**: Stored as JSON files in `profiles/{username}.json`.
- **Interaction Logs**: User behavior (adds, likes, searches) is captured in the `user_metadata` field of the profile to provide training data for future model iterations.

## Design Philosophy
- **User-Centric**: Shifted from hardcoded simulations to a dynamic, interactive experience.
- **Visual & Auditory**: Integration of artwork and audio previews to provide a rich music discovery environment.
- **Hybrid Data**: Combines a local "known" library (`songs.csv`) with a massive global dataset (iTunes).
- **Extensibility**: The architecture is ready for RAG (Retrieval-Augmented Generation) and advanced machine learning models.

---
*See [GEMINI.md](GEMINI.md) for the development roadmap and implementation status.*
