# 🎵 Music Recommender Extension

A robust, interactive music discovery and management application powered by an **Ensemble Recommendation Engine** and **RAG (Retrieval-Augmented Generation)**.

## 🚀 Key Features

### 1. Advanced Ensemble Recommender
The core engine now uses three distinct AI strategies to ensure highly accurate and diverse suggestions:
- **Item-to-Item Similarity**: Matches candidates against *individual* songs in your history to respect distinct tastes.
- **Multi-Centroid Clustering (K-Means)**: Groups your liked songs into "vibes" and finds suggestions for each listening mood.
- **Semantic Text Matching (TF-IDF)**: Analyzes song metadata (Artist, Title, Genre) to understand keywords like "Acoustic" or "Remix."

### 2. Global RAG Discovery
- **Live Internet Querying**: Automatically "describes" your current taste and queries the **iTunes API** to find new music from across the entire world.
- **Zero-Cost Feature Estimation**: A local NLP engine estimates Energy, Tempo, and Mood for millions of online songs for free.

### 3. Interactive Streamlit UI
- **Profile Persistence**: Save and load user sessions via JSON profiles in the `profiles/` directory.
- **Full Playlist Management**: Create, manage, and delete playlists with ease.
- **Visual & Auditory**: Includes high-resolution album artwork and 30-second audio previews for all results.
- **Explainable AI**: Click the "Why this?" button on any recommendation to see exactly which part of your profile triggered the suggestion.

### 4. Real-Time Learning
- **Feedback Loop**: Rate recommendations (1-5 stars) to tune the model in real-time during your session.
- **Dynamic Centroid Shift**: 5-star ratings immediately influence the next set of suggestions.

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **ML/Analytics**: Scikit-Learn (KNN, K-Means, TF-IDF, MinMaxScaler)
- **Data**: Pandas, Requests (iTunes Search API)
- **Persistence**: JSON-based User Profiles

## 🏁 Getting Started
1. Install dependencies: `pip install streamlit pandas scikit-learn requests`
2. Run the app: `streamlit run src/app.py`

---
*Developed as a robust, zero-cost music discovery simulation.*
