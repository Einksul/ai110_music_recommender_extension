import pytest
from recommender import Song, UserProfile, Recommender

def test_score_song_perfect_match():
    song = Song(1, "Hit", "Artist", "pop", "happy", 0.8, 120, 0.8, 0.8, 0.1)
    user = UserProfile("pop", "happy", 0.8, 120, 0.8)
    rec = Recommender([song])
    
    score = rec.score_song(user, song)
    # With default weights: 0.4 (genre) + 0.3 (mood) + 0.1 (energy) + 0.1 (tempo) + 0.1 (valence) = 1.0
    assert score == pytest.approx(1.0)

def test_score_song_no_match():
    song = Song(1, "Niche", "Artist", "metal", "dark", 0.9, 180, 0.1, 0.2, 0.1)
    user = UserProfile("pop", "happy", 0.2, 80, 0.9)
    rec = Recommender([song])
    
    score = rec.score_song(user, song)
    # Should be very low, but > 0 because of numerical differences
    assert score < 0.3

def test_ranking_logic():
    songs = [
        Song(1, "Low Match", "A", "rock", "sad", 0.1, 60, 0.1, 0.1, 0.9),
        Song(2, "High Match", "B", "pop", "happy", 0.8, 120, 0.8, 0.8, 0.1)
    ]
    user = UserProfile("pop", "happy", 0.8, 120, 0.8)
    rec = Recommender(songs)
    
    results = rec.recommend(user, k=2)
    assert results[0][0].title == "High Match"
    assert results[0][1] > results[1][1]

def test_adjustable_weights():
    song = Song(1, "Pop Sad", "Artist", "pop", "sad", 0.5, 120, 0.5, 0.5, 0.5)
    # Heavy weight on mood
    user = UserProfile("pop", "happy", 0.5, 120, 0.5, weights={
        "genre": 0.1, "mood": 0.8, "energy": 0.05, "tempo": 0.025, "valence": 0.025
    })
    rec = Recommender([song])
    
    score = rec.score_song(user, song)
    # Mood doesn't match and it's 80% of the score
    assert score < 0.3
