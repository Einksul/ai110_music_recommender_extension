# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  
**VibeFinder 1.0**

---

## 2. Intended Use  
This model generates personalized music suggestions from a catalog of 30 songs. It is specifically focuses on how weighted linear combinations can be used with both quantitative and qualitative features of songs.

---

## 3. How the Model Works  
The model uses a **Weighted Content-Based Filtering** approach. It looks at every song in the database and calculates a compatability score by comparing the song's attributes to the user's target profile.
- **Matching Categories**: It gives points if the genre or mood matches exactly.
- **Measuring Distance**: For things like Energy or Tempo, it calculates how "close" the song is to the user's ideal. The closer the match, the higher the score.
- **Custom Importance**: The weight for each feature vary depending on which matters the most. For example, weighting "Mood" and "Energy" more heavily than "Genre" leads to better discovery of new music that fits a specific "vibe."

---

## 4. Data  
The dataset consists of **30 songs** across a wide variety of genres including Pop, Lofi, Rock, Metal, Classical, Jazz, Techno, and Ambient. Each song is tagged with 10 features, ranging from simple labels (Artist, Title) to acoustic properties (Valence, Danceability, Acousticness).

---

## 5. Strengths  
- **Vibe Alignment**: The system is excellent at finding songs that match a user's vibe, even across different genres.
- **Flexibility**: We are able to expand this system to allow for user feeback, which can be used to tune the weights for each user.

---

## 6. Limitations and Bias 
- Incorrect weights: Songs that are "okay" at everything can sometimes outrank songs that are "perfect" at one thing if weights are too evenly distributed.
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
- User behavior: At the moment, the weights are fixed based on how an average user would behave. It would benefit to  incoporate user specific behavior after we import a profile, such as "Likes" and "Skips" to learn from user behavior over time. Additionally, we could automatically adjusting weights based on user feedback (e.g., if a user skips a different genre, increase the Genre weight).
- **Diversity Re-ranking**: Ensuring the top 5 results aren't all from the same artist or genre to encourage broader discovery.

---

## 9. Personal Reflection  
I was surprsised at how sensitive the mdoel was with respect to the weights. A small change on favoring a feature more would skew the recommendations. Due to this, I would suspect actual production level recommenders would have a lot more parameters to refine the state space. Additionally, they would also probably have a different architecture to make use of the user's data and behvaior. Humans should still be at the center, having a recommender thats more interactive would help it tailor its suggestions to the user, and with anything art related, there are always exceptions that can't be defined rigidly, so humans would be needed to classify it.
