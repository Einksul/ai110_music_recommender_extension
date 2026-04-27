# Project Report: Music Recommender Extension

## Title and Summary
**Project Title:** Interactive Ensemble Music Recommender & RAG Discovery Engine  
**Summary:** This project is a robust, interactive music management and discovery application built with Python and Streamlit. It solves the "cold start" and "diversity" problems in music recommendation by using a **Multi-Query RAG (Retrieval-Augmented Generation)** pipeline and an **Ensemble Recommendation Engine**. Unlike standard recommenders that often "wash out" a user's varied tastes into a single average, this system identifies distinct listening moods and provides explainable, diverse suggestions from both a local library and the entire global iTunes catalog—all with zero API costs.

---

## Architecture Overview
The system follows a three-layer architecture designed for persistence, discovery, and explainable AI:

1.  **Frontend (Streamlit)**: An interactive dashboard for profile management, playlist curation, and real-time discovery.
2.  **Logic Layer (Ensemble Engine & RAG)**: 
    - **RAG Pipeline**: Dynamically generates diverse search queries based on user history to "retrieve" global candidates from the internet.
    - **Ensemble Engine**: Combines **Item-to-Item Similarity**, **Multi-Centroid Clustering (K-Means)**, and **Semantic Text Matching (TF-IDF)** to score candidates.
    - **MMR Ranking**: Uses *Maximal Marginal Relevance* to mathematically balance similarity with novelty, ensuring artist diversity.
3.  **Persistence Layer (JSON)**: Serializes user tastes, playlists, and interaction history into local profiles for session continuity.

*For detailed diagrams, see [UML.md](UML.md).*

---

## Setup Instructions
To run this project locally, follow these steps:

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd ai110_music_recommender_extension
    ```
2.  **Install Dependencies**:
    ```bash
    pip install streamlit pandas scikit-learn requests
    ```
3.  **Launch the Application**:
    ```bash
    streamlit run src/app.py
    ```
4.  **Usage**: Create a new profile on the startup screen to begin building your music taste profile.

---

## Sample Interactions

### 1. Zero-Cost Feature Estimation
**Input:** Search Online for "ASMR rain sounds"  
**System Output:** Automatically identifies the "ASMR" keyword and genre.  
**AI Logic:** The `LocalFeatureEstimator` assigns a **Speechiness** score of 0.9 and **Energy** of 0.1. The "Why this?" button explains: *"Matches your interest in spoken word/ASMR."*

### 2. Explainable Global Discovery
**Input:** Request 10 recommendations based on a "Rock" playlist.  
**System Output:** 10 diverse artists (e.g., Hitsujibungaku, Ginger Root, Yorushika).  
**AI Logic:** The model identifies that Hitsujibungaku is *"Thematically similar to [Seed Song X]"* (TF-IDF), while Ginger Root *"Shares the exact energy profile of [Seed Song Y]"* (Numerical KNN).

### 3. Real-Time Model Tuning
**Input:** User gives a 5-star rating to a recommended Jazz track.  
**System Output:** Notification: *"Model tuned! Finding more like 'Midnight Jazz'..."*  
**AI Logic:** The system performs a "Preference Shift" by adding the new track to the session's active seeds, immediately influencing the next generation of results.

---

## Design Decisions
- **KNN vs. Deep Learning**: I chose a **KNN-based Ensemble** over a Neural Network (like a Two-Tower model) because this is a zero-cost test project. KNN provides high accuracy with small datasets and requires zero expensive training or token costs.
- **MMR for Diversity**: Simple sorting by similarity often leads to "artist clusters" (recommending 10 songs by the same artist). I implemented **Maximal Marginal Relevance (MMR)** to penalize redundancy and force diversity.
- **Local Feature Estimation (LFE)**: Since external APIs for audio features (like Spotify) require keys and complex auth, I built a local NLP engine that estimates vibes (Energy, Tempo, Instrumentalness) directly from metadata for free.

---

## Testing Summary
- **What Worked**: The Item-to-Item strategy successfully eliminated "Centroid Washout," allowing a user to like both Metal and Classical and see both reflected in the results.
- **Challenges**: Initially, the model suffered from "Deterministic Bias" (giving the same 5 results every time). I solved this by implementing **Randomized Multi-Query RAG** and a **Variety Sampling Pool**.
- **Learnings**: I learned that transparency is as important as accuracy. Adding the "Why this?" popover dramatically increased user trust in the AI's "weird" but diverse suggestions.

---

## Reflection
This project taught me that **AI is an engineering problem, not just a modeling one.** Building the "perfect" model is useless if the data pipeline is too narrow or the UI is static. By implementing RAG and an ensemble of simple models, I achieved a "smart" feel without the overhead of heavy infrastructure. It reinforced my belief that **Explainable AI (XAI)** and **Human-in-the-loop feedback** are the most effective ways to build software that users actually enjoy.
