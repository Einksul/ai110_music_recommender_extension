# Project Report: Music Discovery and Recommendation Engine

## Executive Summary
The Music Recommender Extension is a sophisticated discovery and management platform designed to address critical challenges in personalized content delivery, such as "cold start" data gaps and "centroid washout" (the dilution of distinct user preferences). By utilizing a **Multi-Query RAG (Retrieval-Augmented Generation)** pipeline and an **Ensemble Recommendation Engine**, the system delivers highly accurate, diverse, and explainable suggestions. The platform integrates local library management with the global iTunes catalog, providing a zero-cost, high-performance solution for scalable music discovery.

---

## Architecture Overview
The system utilizes a modular, three-tier architecture to ensure scalability and real-time responsiveness:

1.  The **Interface Layer (Streamlit)** provides an interactive, web-based dashboard for user profile management, playlist curation, and global data exploration.
2.  The **Logic Layer (Ensemble Engine & RAG)** includes:
    - The **RAG Pipeline** dynamically generates optimized search queries from user history to retrieve high-quality candidates from global datasets.
    - The **Ensemble Engine** processes data through three concurrent models: **Item-to-Item Similarity**, **Multi-Centroid Clustering (K-Means)**, and **Semantic Text Matching (TF-IDF)**.
    - The **MMR Ranking** implements *Maximal Marginal Relevance* to mathematically balance relevance with novelty, preventing artist concentration and ensuring variety.
3.  The **Persistence Layer (JSON)** ensures session continuity by serializing user metadata, preferences, and interaction history into secure local profiles.

---

## Implementation and Deployment
To deploy the application in a local environment:

1.  **Repository Setup**:
    ```bash
    git clone https://github.com/Einksul/ai110_music_recommender_extension.git
    cd ai110_music_recommender_extension
    ```
2.  **Dependency Installation**:
    ```bash
    pip install streamlit pandas scikit-learn requests
    ```
3.  **Application Launch**:
    ```bash
    streamlit run src/app.py
    ```
4.  **Onboarding**: New users initiate the system by creating a profile, which serves as the foundation for the incremental learning algorithm.

---

## Sample Interactions and System Output

### 1. Zero-Cost Feature Estimation
- The **Input** was a search for "Solo Acoustic Guitar."
- The **System Output** provided automated identification of instrumental and acoustic characteristics.
- For the **AI Logic**, the `LocalFeatureEstimator` assigns a high **Instrumentalness** score and low **Energy**, with the transparency module providing the following justification: *"Matches established preference for acoustic and instrumental compositions."*

### 2. Explainable Global Discovery
- The **Input** was a request for 10 recommendations based on a high-tempo electronic playlist.
- The **System Output** returned 10 diverse selections across multiple high-energy sub-genres.
- For the **AI Logic**, the engine identifies specific matches, such as one track being *"Thematically similar to [Reference Track]"* (Semantic) and another *"Sharing an identical energy profile with [Reference Track]"* (Numerical).

### 3. Real-Time Preference Adaptation
- The **Input** occurred when the user provides a 5-star rating to a suggested ambient track.
- The **System Output** was a model optimization notification.
- For the **AI Logic**, the system executes a "Preference Shift," temporarily incorporating the high-rated track into the active seed set to refine the parameters for subsequent recommendation generations.

---

## Design Decisions and Strategic Trade-offs
- Regarding **KNN Ensemble vs. Deep Learning**, a **KNN-based Ensemble** was selected over Neural Network architectures to maintain a zero-cost infrastructure, delivering high precision with smaller datasets while eliminating the need for expensive training hardware or recurring API token fees.
- For **MMR for Diversification**, **Maximal Marginal Relevance (MMR)** was implemented to prevent the "filter bubble" effect where a single artist dominates results by penalizing redundancy and ensuring a mathematically diverse output.
- **Local Feature Estimation (LFE)** was developed to avoid dependency on third-party audio analysis APIs (e.g., Spotify), with the local NLP-based estimation engine extracting 8 distinct musical dimensions directly from available metadata.

---

## Testing and Quality Assurance
- **Functional Success** was achieved as the Item-to-Item strategy effectively resolved "Centroid Washout," enabling the system to support users with diametrically opposed tastes (e.g., Classical and Industrial Rock) without compromising the relevance of either.
- **Optimization Challenges** were encountered where initial iterations exhibited "Deterministic Bias," providing repetitive results, which was mitigated through the implementation of **Randomized Multi-Query RAG** and a **Variety Sampling Pool**.
- **Observability** was enhanced by the inclusion of an "Explainable AI" layer, which significantly improved the perceived quality of suggestions by providing users with clear logical justifications for each match.

---

## Conclusion
This project demonstrates that robust AI solutions can be achieved through disciplined engineering and strategic algorithmic blending rather than relying solely on high-compute infrastructure. By prioritizing **Explainable AI (XAI)** and **Human-in-the-Loop** feedback mechanisms, the system achieves a level of personalization and discovery variety typically reserved for larger, high-cost platforms. The resulting engine is a highly efficient, scalable, and user-centric discovery tool.
