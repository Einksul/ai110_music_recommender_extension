# System Architecture & Data Flow

## Ensemble Recommendation Architecture

The core of the system is a three-pillar ensemble model that ensures accurate and diverse suggestions.

```mermaid
graph TD
    %% Seeds
    UserSeeds[User History / Seeds] --> FE[Feature Extraction]
    
    %% Pillars
    subgraph Ensemble [Ensemble Engine]
        direction TB
        P1[Item-to-Item KNN]
        P2[Multi-Centroid K-Means]
        P3[Semantic TF-IDF]
    end
    
    FE -- Numerical Vectors --> P1
    FE -- Numerical Vectors --> P2
    FE -- Text Metadata --> P3
    
    %% Logic
    P1 -- Individual Matches --> Blender[Ranker & Blender]
    P2 -- Vibe Clusters --> Blender
    P3 -- Text Similarity --> Blender
    
    %% Final
    Blender -- Ranked Results --> Explanation[Explainable AI Layer]
    Explanation -- Output --> UI[Streamlit Frontend]
    
    %% Feedback
    UI -- 5-Star Rating --> UserSeeds
```

## High-Level System Flow

```mermaid
graph TD
    subgraph UI [Frontend]
        A[Profile Loader] --> B[Interactive Dashboard]
        B --> C[Management & Exploration]
    end

    subgraph RAG [Internet Integration]
        C -- Search/Discover --> D[iTunes Search API]
        D -- Raw Data --> E[Local Feature Estimator]
        E -- Vibe Vectors --> B
    end

    subgraph Data [Storage]
        B -- Save --> F[JSON Profiles]
        F -- Load --> A
    end
```

## Strategy Details

### 1. Item-to-Item Similarity
- Each seed song acts as an individual query.
- Bypasses averaging to preserve polar-opposite tastes (e.g., Chill vs. Metal).

### 2. Multi-Centroid (K-Means)
- Groups user history into $K$ distinct taste clusters.
- Finds candidates that match the center of these specific "listening moods."

### 3. TF-IDF Semantic Matching
- Analyzes text metadata (Title, Artist, Genre).
- Captures nuances like "Remix," "Live," or specific artist names that numerical features might overlook.

### 4. Dynamic Weighting
- **Numerical Score**: 70% of total ranking weight.
- **Semantic Score**: 30% of total ranking weight.
- High-star feedback triggers a real-time shift in the session's active seeds.
