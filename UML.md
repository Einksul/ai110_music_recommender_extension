# System Data Flow & Architecture

The following Mermaid diagram outlines how data moves through the Music Recommender Simulation, from initial user input to the final generated recommendations.

```mermaid
graph TD
    %% Input Phase
    subgraph Input [User Profile & Preferences]
        A[User Input] --> B[UserProfile Object]
        B1[Categorical Targets: Genre, Mood] -.-> B
        B2[Numerical Targets: Energy, Tempo, etc.] -.-> B
        B3[Adjustable Weights Dictionary] -.-> B
    end

    %% Processing Phase
    subgraph Process [The Scoring Loop]
        C[(songs.csv Library)] -- Load --> D[Song Objects List]
        B -- Passed to --> E[Recommender.score_song]
        D -- Iterated through --> E
        
        subgraph Logic [Scoring Rules]
            E1[Categorical Match: exact strings]
            E2[Numerical Closeness: 1.0 - abs_diff]
            E1 & E2 --> E3[Weighted Linear Combination]
        end
        E3 -- Result --> F[Raw Score: 0.0 to 1.0]
    end

    %% Output Phase
    subgraph Output [The Ranking]
        F -- List of Tuple: Song, Score --> G[Global Sort: Descending]
        G -- Slice Top K --> H[Final Recommendation List]
        H -- For Each Song --> I[Generate Human Explanation]
        I -- Display --> J[Console Output]
    end

    %% Styling
    style Input fill:#e1f5fe,stroke:#01579b
    style Process fill:#fff3e0,stroke:#e65100
    style Output fill:#e8f5e9,stroke:#1b5e20
```

## Data Flow Summary

1.  **Input**: The system captures a `UserProfile` containing both categorical preferences and numerical targets, along with a set of `weights` that define the importance of each feature.
2.  **Process (Pointwise)**: The system loops through every `Song` in the catalog. For each song, it calculates a weighted compatibility score using the `score_song` logic.
3.  **Ranking (Listwise)**: Once all songs have individual scores, they are sorted globally. The system then selects the top `K` results and generates natural language explanations for the user.
