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
**Input:** Search Online for "Solo Piano Chill"  
**System Output:** Automatically identifies instrumental and acoustic characteristics.  
**AI Logic:** The `LocalFeatureEstimator` assigns a high **Instrumentalness** score and low **Energy**. The "Why this?" button explains: *"Matches your preference for acoustic and instrumental tracks."*

### 2. Explainable Global Discovery
**Input:** Request 10 recommendations based on a "High Energy" playlist.  
**System Output:** 10 diverse artists across different high-tempo genres.  
**AI Logic:** The model identifies that one track is *"Thematically similar to [Seed Song X]"* (TF-IDF), while another *"Shares the exact energy profile of [Seed Song Y]"* (Numerical KNN).

### 3. Real-Time Model Tuning
**Input:** User gives a 5-star rating to a recommended Jazz track.  
**System Output:** Notification: *"Model tuned! Finding more like this track..."*  
**AI Logic:** The system performs a "Preference Shift" by adding the new track to the session's active seeds, immediately influencing the next generation of results.

---

## Design Decisions
- **KNN vs. Deep Learning**: I chose a **KNN-based Ensemble** over a Neural Network (like a Two-Tower model) because this is a zero-cost project. KNN provides high accuracy with small datasets and requires zero expensive training or token costs.
- **MMR for Diversity**: Simple sorting by similarity often leads to "artist clusters" (recommending 10 songs by the same artist). I implemented **Maximal Marginal Relevance (MMR)** to penalize redundancy and force artist diversity.
- **Local Feature Estimation (LFE)**: Since external APIs for audio features require keys and complex auth, I built a local NLP engine that estimates vibes (Energy, Tempo, Speechiness) directly from metadata for free.

---

## Testing Summary
- **What Worked**: The Item-to-Item strategy successfully eliminated "Centroid Washout," allowing a user to like both high-energy and low-energy music and see both reflected in the results.
- **Challenges**: Initially, the model suffered from "Deterministic Bias" (giving the same results every time). I solved this by implementing **Randomized Multi-Query RAG** and a **Variety Sampling Pool**.
- **Learnings**: I learned that transparency is as important as accuracy. Adding the "Why this?" popover dramatically increased user trust in the AI's diverse suggestions.

---

## Reflection
This project taught me that **AI is an engineering problem, not just a modeling one.** Building the "perfect" model is useless if the data pipeline is too narrow or the UI is static. By implementing RAG and an ensemble of simple models, I achieved a "smart" feel without the overhead of heavy infrastructure. It reinforced my belief that **Explainable AI (XAI)** and **Human-in-the-loop feedback** are the most effective ways to build software that users actually enjoy.
