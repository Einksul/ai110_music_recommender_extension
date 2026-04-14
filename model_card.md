# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  
**VibeFinder 1.0**

---

## 2. Intended Use  
This model generates personalized music suggestions from a small, diverse catalog of 30 songs. It is designed for classroom exploration of recommendation logic, specifically focusing on how weighted linear combinations can balance categorical preferences (like Genre) with numerical "vibes" (like Energy and Tempo).

---

## 3. How the Model Works  
The model uses a **Weighted Content-Based Filtering** approach. It looks at every song in the database and calculates a "compatibility score" by comparing the song's attributes to the user's target profile.
- **Matching Categories**: It gives points if the genre or mood matches exactly.
- **Measuring Distance**: For things like Energy or Tempo, it calculates how "close" the song is to the user's ideal. The closer the match, the higher the score.
- **Custom Importance**: We use a set of "weights" to decide which features matter most. For example, we found that weighting "Mood" and "Energy" more heavily than "Genre" leads to better discovery of new music that fits a specific "vibe."

---

## 4. Data  
The dataset consists of **30 songs** across a wide variety of genres including Pop, Lofi, Rock, Metal, Classical, Jazz, Techno, and Ambient. Each song is tagged with 10 features, ranging from simple labels (Artist, Title) to acoustic properties (Valence, Danceability, Acousticness).

---

## 5. Strengths  
- **Vibe Alignment**: The system is excellent at finding songs that match a specific physiological state (e.g., high-energy workout or low-energy study session) even across different genres.
- **Transparency**: Every recommendation comes with a "Reason" that explains which specific features (like a perfect energy match) drove the result.
- **Flexibility**: The adjustable weight system allows the engine to be tuned for different types of users (e.g., those who are genre-loyal vs. those who are mood-seekers).

---

## 6. Limitations and Bias 
- **The "Average" Trap**: Songs that are "okay" at everything can sometimes outrank songs that are "perfect" at one thing if weights are too evenly distributed.
- **Genre Blindness**: If energy and mood are weighted too heavily, the system might ignore a user's explicit request for a specific genre (e.g., suggesting Lofi to a Metalhead).
- **Small Catalog**: With only 30 songs, the system cannot capture the true diversity of musical sub-genres or cultural contexts.

---

## 7. Evaluation  
We performed **Stress Testing** using four distinct profiles:
1. **Adversarial**: Searching for high-energy classical (testing cross-genre pivots).
2. **Contradictory**: An "Acoustic Metalhead" (testing feature conflict resolution).
3. **Minimalist**: No specific labels provided (testing numerical defaults).
4. **Niche**: Searching for a rare genre/mood combination.
We verified that the top 5 results logically followed our weighting math in every case.

---

## 8. Future Work  
- **Collaborative Filtering**: Incorporating "Likes" and "Skips" to learn from user behavior over time.
- **Dynamic Weighting**: Automatically adjusting weights based on user feedback (e.g., if a user skips a different genre, increase the Genre weight).
- **Diversity Re-ranking**: Ensuring the top 5 results aren't all from the same artist or genre to encourage broader discovery.

---

## 9. Personal Reflection  
I learned that recommendation is a delicate balancing act. There is no "perfect" algorithm; every change in weights creates a trade-off between giving the user exactly what they asked for and surprising them with something they didn't know they would like. It's fascinating how a simple linear equation can mimic "intuition" so effectively.
