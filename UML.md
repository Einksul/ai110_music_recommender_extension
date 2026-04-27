# System Architecture & Data Flow

The Music Recommender Extension has evolved into an interactive web application. The following diagrams outline the modern architecture and how user data flows through the system.

## High-Level Architecture

```mermaid
graph TD
    %% User Layer
    subgraph UI [Streamlit User Interface]
        A[Profile Loader] --> B[Dashboard]
        B --> C1[Playlists Tab]
        B --> C2[Search & Add Tab]
        B --> C3[Liked Songs Tab]
    end

    %% Logic Layer
    subgraph AppLogic [Application Logic]
        C2 -- Search Query --> D{Search Router}
        D -- Local --> E[(songs.csv)]
        D -- Global --> F[iTunes Search API]
        
        C2 -- View Album/Artist --> G[iTunes Lookup API]
        
        C2 -- Interaction --> H[Action Logger]
    end

    %% Data Layer
    subgraph Data [Persistence Layer]
        H -- Save Interaction --> I[UserProfile JSON]
        C2 -- Add/Like --> I
        I -- Persistent Storage --> J[(profiles/ directory)]
        J -- Load Session --> A
    end

    %% Future Phase
    subgraph ML [Future Recommendation Engine]
        I -- Ingest History --> K[RAG / Advanced Model]
        K -- Predict --> L[Tailored Recommendations]
        L -- Display --> C2
    end

    %% Styling
    style UI fill:#e1f5fe,stroke:#01579b
    style AppLogic fill:#fff3e0,stroke:#e65100
    style Data fill:#e8f5e9,stroke:#1b5e20
    style ML fill:#f3e5f5,stroke:#4a148c
```

## Component Breakdown

### 1. Profile Persistence
- **State**: The `UserProfile` object is the single source of truth during a session.
- **Save**: Any change (creating a playlist, adding a song, liking a track) triggers an automatic `profile.save()` call, which serializes the state to `profiles/{name}.json`.
- **Load**: On startup, the UI lists all files in `profiles/`, allowing the user to resume their specific session.

### 2. Hybrid Search Engine
- **Local Branch**: Filters the internal `songs.csv` using pandas. This is fast and contains the specific audio features (energy, tempo) for the recommendation model.
- **Global Branch**: Queries the iTunes API in real-time. This provides access to millions of songs, album artwork, and audio previews.
- **Exploration**: Uses the iTunes `lookup` endpoint to drill down into specific album contents or artist discographies.

### 3. Interaction Logging
- Every user action is captured in the `user_metadata` field:
    - **Action**: "add_to_playlist", "like_song", "create_playlist".
    - **Context**: Timestamps, song metadata, and search source (Local vs. Global).
- This creates a rich behavioral dataset for future training of the advanced recommendation model.
